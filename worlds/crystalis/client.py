from typing import TYPE_CHECKING, List, Dict, Tuple
from NetUtils import ClientStatus, NetworkItem
from Utils import async_start

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from .items import items_data_by_id, items_data
from .regions import regions_data
from .types import CRYSTALIS_BASE_ID

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

LOCATION_FLAGS_ADDR = 0x64A0
ITEM_FLAGS_ADDR = 0x64C0
RECEIVED_INDEX_ADDR = 0x657D
SCREEN_MODE_ADDR = 0x0051
END_OF_CONSUMABLE_INV_ADDR = 0x6447
GET_ITEM_FLAG_ADDR = 0x6250
MAIN_LOOP_MODE_ADDR = 0x40
GAME_MODE_ADDR = 0x41
CRYSTALIS_ITEM_ID = 0x04
CURRENT_LOCATION_ADDR = 0x6c


class CrystalisClient(BizHawkClient):
    game = "Crystalis"
    system = "NES"
    #intentionally not defining patch_suffix because Archipelago will not be responsible for patching the game
    expected_start: List[bytes] = [bytes([0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9])]
    #TODO: Consider a better method for identifying valid Crystalis ROMs
    loc_id_to_addr: Dict[int, Tuple[int, int]] = {}
    unidentified_item_rom_ids: Dict[int, int] = {}
    current_location: int = 0


    def __init__(self):
        super().__init__()
        for region in regions_data.values():
            for location in region.locations:
                byte: int = location.rom_id // 8
                bit: int = location.rom_id % 8
                self.loc_id_to_addr[location.ap_id_offset + CRYSTALIS_BASE_ID] = (byte, bit)


    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger
        try:
            rom_start: List[bytes] = (await bizhawk.read(ctx.bizhawk_ctx, [(0x0, 8, "PRG ROM")]))
            if rom_start != self.expected_start:
                logger.info("Expected: " + str(self.expected_start))
                logger.info("Found: " + str(rom_start))
                return False
        except bizhawk.RequestFailedError:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True
        return True


    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd == "Connected":
            #slot_data should be set now
            key_item_names: Dict[str, str] = ctx.slot_data["shuffle_data"]["key_item_names"]
            for original_name, new_name in key_item_names.items():
                #want to map the new item's AP ID to the original item's in-game ID.
                self.unidentified_item_rom_ids[items_data[new_name].ap_id_offset + CRYSTALIS_BASE_ID] = \
                    items_data[original_name].rom_id


    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            read_value = await bizhawk.read(ctx.bizhawk_ctx, [(LOCATION_FLAGS_ADDR, 16, "System Bus"),
                                                              (ITEM_FLAGS_ADDR, 16, "System Bus"),
                                                              (RECEIVED_INDEX_ADDR, 2, "System Bus"),
                                                              (GET_ITEM_FLAG_ADDR, 1, "System Bus"),
                                                              (GAME_MODE_ADDR, 1, "System Bus"),
                                                              (MAIN_LOOP_MODE_ADDR, 1, "System Bus"),
                                                              (CURRENT_LOCATION_ADDR, 1, "System Bus")])
            if read_value is not None:
                game_mode = read_value[4][0]
                main_loop_mode = read_value[5][0]
                if main_loop_mode == 1: #MAIN_LOOP_GAME
                    location_flags = read_value[0]
                    locations_to_send: List[int] = []
                    for location_id in ctx.missing_locations:
                        byte, bit = self.loc_id_to_addr[location_id]
                        if location_flags[byte] & (1 << bit) != 0:
                            locations_to_send.append(location_id)
                            ctx.locations_checked.add(location_id)

                    if len(locations_to_send) > 0:
                        await ctx.send_msgs([{
                                "cmd": "LocationChecks",
                                "locations": list(locations_to_send)
                            }])
                        return #Bail now to keep this loop short

                    get_item_flag: bool = read_value[3][0] != 0
                    item_flags: bytes = read_value[1]
                    received_crystalis: bool = item_flags[0] & 16 != 0
                    if not get_item_flag and not received_crystalis and location_flags[0] & 16 != 0:
                        success: bool = await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                        [(GET_ITEM_FLAG_ADDR, [1, CRYSTALIS_ITEM_ID], "System Bus")],
                                                        [(MAIN_LOOP_MODE_ADDR, [1], "System Bus")])
                        if success:
                            self.received_crystalis = True
                    received_indices: bytes = read_value[2]
                    nonconsumable_index: int = received_indices[0]
                    consumable_index: int = received_indices[1]
                    new_location: int = read_value[6][0]
                    if new_location != self.current_location:
                        self.current_location = new_location
                        async_start(ctx.send_msgs([{
                                    "cmd": "Set",
                                    "key": f"current_location_{ctx.slot}",
                                    "default": 0,
                                    "want_reply": False,
                                    "operations": [{"operation": "replace", "value": new_location}]
                                }]), name="send current_location")
                    #if we're not already processing an item and we're not in Mezame Shrine...
                    #Prevent receiving items in Mezame Shrine to make reloading saves for asyncs a bit smoother.
                    if not get_item_flag and self.current_location != 0:
                        if nonconsumable_index + consumable_index < len(ctx.items_received):
                            non_consumables = [item for item in ctx.items_received if
                                               items_data_by_id[item.item].groups != ["Consumable"]]
                            if nonconsumable_index < len(non_consumables):
                                item_to_write: NetworkItem = non_consumables[nonconsumable_index]
                                unique: bool = items_data_by_id[item_to_write.item].unique
                                item_id: int
                                if item_to_write.item in self.unidentified_item_rom_ids.keys():
                                    item_id = self.unidentified_item_rom_ids[item_to_write.item]
                                else:
                                    item_id = items_data_by_id[item_to_write.item].rom_id
                                byte: int = item_id // 8
                                bit: int = item_id % 8
                                item_flag_byte: byte = item_flags[byte] if unique \
                                    else item_flags[byte] & (0xFF ^ (1 << bit))

                                await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                        [(RECEIVED_INDEX_ADDR, [nonconsumable_index + 1], "System Bus"),
                                                         (GET_ITEM_FLAG_ADDR, [1, item_id], "System Bus"),
                                                         (ITEM_FLAGS_ADDR + byte, [item_flag_byte], "System Bus")],
                                                        [(MAIN_LOOP_MODE_ADDR, [1], "System Bus")])
                            else:
                                consumables = [item for item in ctx.items_received if
                                               items_data_by_id[item.item].groups == ["Consumable"]]
                                if consumable_index < len(consumables):
                                    item_to_write: NetworkItem = consumables[consumable_index]
                                    item_id: int = items_data_by_id[item_to_write.item].rom_id
                                    byte: int = item_id // 8
                                    bit: int = item_id % 8
                                    item_flag_byte: byte = item_flags[byte] & (0xFF ^ (1 << bit))
                                    await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                       [(RECEIVED_INDEX_ADDR + 1, [consumable_index + 1], "System Bus"),
                                                        (GET_ITEM_FLAG_ADDR, [1, item_id], "System Bus"),
                                                        (ITEM_FLAGS_ADDR + byte, [item_flag_byte], "System Bus")],
                                                       [(END_OF_CONSUMABLE_INV_ADDR, [0xFF], "System Bus"),
                                                        (MAIN_LOOP_MODE_ADDR, [1], "System Bus")])
                    if game_mode == 0x1e and not ctx.finished_game: #GAME_MODE_DYNA_DEFEATED
                        await ctx.send_msgs([{
                            "cmd": "StatusUpdate",
                            "status": ClientStatus.CLIENT_GOAL
                        }])
        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass


