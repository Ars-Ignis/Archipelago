from typing import TYPE_CHECKING, List, Dict, Tuple, Optional
from NetUtils import ClientStatus, NetworkItem

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from .items import items_data_by_id
from .regions import regions_data
from .types import CRYSTALIS_BASE_ID

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

LOCATION_FLAGS_ADDR = 0x64A0
RECEIVED_INDEX_ADDR = 0x657E
SCREEN_MODE_ADDR = 0x0051
END_OF_CONSUMABLE_INV_ADDR = 0x6447
GET_ITEM_FLAG_ADDR = 0x6250
GAME_MODE_ADDR = 0x40


class CrystalisClient(BizHawkClient):
    game = "Crystalis"
    system = "NES"
    #intentionally not defining patch_suffix because Archipelago will not be responsible for patching the game
    expected_start: List[bytes] = [bytes([0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9])]
    #TODO: Consider a better method for identifying valid Crystalis ROMs
    id_to_addr: Dict[int, Tuple[int, int]] = {}

    def __init__(self):
        super().__init__()
        #self.locally_checked_ids = set()
        for region in regions_data.values():
            for location in region.locations:
                byte: int = location.rom_id // 8
                bit: int = location.rom_id % 8
                self.id_to_addr[location.ap_id_offset + CRYSTALIS_BASE_ID] = (byte, bit)


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
        return True


    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        from CommonClient import logger
        try:
            read_value = await bizhawk.read(ctx.bizhawk_ctx, [(LOCATION_FLAGS_ADDR, 16, "System Bus"),
                                                              (RECEIVED_INDEX_ADDR, 2, "System Bus"),
                                                              (GET_ITEM_FLAG_ADDR, 1, "System Bus"),
                                                              (GAME_MODE_ADDR, 1, "System Bus")])
            if read_value is not None:
                game_mode = read_value[3]
                if game_mode[0] == 1: #GAME_MODE_NORMAL

                    location_flags = read_value[0]
                    locations_to_send: List[int] = []
                    for location_id in ctx.missing_locations:
                        byte, bit = self.id_to_addr[location_id]
                        if location_flags[byte] & (1 << bit) != 0:
                            locations_to_send.append(location_id)

                    if len(locations_to_send) > 0:
                        await ctx.send_msgs([{
                                "cmd": "LocationChecks",
                                "locations": list(locations_to_send)
                            }])

                    received_indices: bytes = read_value[1]
                    nonconsumable_index: int = received_indices[0]
                    consumable_index: int = received_indices[1]
                    get_item_flag: bool = read_value[2][0] != 0
                    if not get_item_flag:
                        if nonconsumable_index + consumable_index < len(ctx.items_received):
                            non_consumables = [item for item in ctx.items_received if
                                               items_data_by_id[item.item].groups != ["Consumable"]]
                            if nonconsumable_index < len(non_consumables):
                                item_to_write: NetworkItem = non_consumables[nonconsumable_index]
                                item_id: int = items_data_by_id[item_to_write.item].rom_id
                                success: bool = await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                        [(RECEIVED_INDEX_ADDR, [nonconsumable_index + 1], "System Bus"),
                                                         (GET_ITEM_FLAG_ADDR, [1, item_id], "System Bus")],
                                                        [(GAME_MODE_ADDR, [1], "System Bus")])
                            else:
                                consumables = [item for item in ctx.items_received if
                                               items_data_by_id[item.item].groups == ["Consumable"]]
                                if consumable_index < len(consumables):
                                    item_to_write: NetworkItem = consumables[consumable_index]
                                    item_id: int = items_data_by_id[item_to_write.item].rom_id
                                    success: bool = await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                       [(RECEIVED_INDEX_ADDR + 1, [consumable_index + 1], "System Bus"),
                                                        (GET_ITEM_FLAG_ADDR, [1, item_id], "System Bus")],
                                                       [(GAME_MODE_ADDR, [1], "System Bus"),
                                                        (END_OF_CONSUMABLE_INV_ADDR, [0xFF], "System Bus")])
                elif game_mode == 0x1e and not ctx.finished_game: #GAME_MODE_DYNA_DEFEATED
                    await ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL
                    }])
        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass


