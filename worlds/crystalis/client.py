from typing import TYPE_CHECKING, List, Dict, Tuple, Set
from NetUtils import ClientStatus

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from .regions import regions_data
from .types import CRYSTALIS_BASE_ID

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

LOCATION_FLAGS_ADDR = 0x64A0


class CrystalisClient(BizHawkClient):
    game = "Crystalis"
    system = "NES"
    #intentionally not defining patch_suffix because Archipelago will not be responsible for patching the game
    expected_start: List[bytes] = [bytes([0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9, 0xd9])]
    id_to_addr: Dict[int, Tuple[int, int]] = {}
    #locally_checked_ids: Set[int]

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
            read_value = await bizhawk.guarded_read(ctx.bizhawk_ctx, [(LOCATION_FLAGS_ADDR, 16, "System Bus")],
                                                        [(0x40, [1], "System Bus")])
            if read_value is not None:
                location_flags = read_value[0]
                locations_to_send: List[int] = []
                for location_id in ctx.missing_locations:
                    byte, bit = self.id_to_addr[location_id]
                    if location_flags[byte] & (1 << bit) != 0:
                        locations_to_send.append(location_id)

                await ctx.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": list(locations_to_send)
                    }])

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass


