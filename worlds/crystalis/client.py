# Python Imports
import copy
from time import time
from typing import TYPE_CHECKING, Set

# Archipelago Imports
import worlds._bizhawk as bizhawk
from NetUtils import ClientStatus, NetworkItem
from Utils import async_start, VersionException, tuplize_version
from worlds._bizhawk.client import BizHawkClient

# Crystalis Imports
from .constants import *
from .items import items_data, items_data_by_id
from .regions import regions_data

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext, BizHawkClientCommandProcessor


def cmd_deathlink(self: "BizHawkClientCommandProcessor") -> None:
    """Toggle DeathLink on or off."""
    from CommonClient import logger
    if self.ctx.game != "Crystalis":
        logger.warning(f"Somehow running a Crystalis command handler while playing a different game: {self.ctx.game}")
        return
    else:
        if "DeathLink" in self.ctx.tags:
            async_start(self.ctx.update_death_link(False))
            logger.info("Death Link is now disabled.")
        else:
            async_start(self.ctx.update_death_link(True))
            logger.info("Death Link is now enabled.")


class CrystalisClient(BizHawkClient):
    game = "Crystalis"
    system = "NES"
    patch_suffix = ".apcrys"

    # Crystalis Client Class Variables
    asina_hint_collected: bool = False
    asina_location_id: int = -1
    compressed_flags: int = 0
    current_location: int = 0
    formatted_key_cache: dict[str, str] = {}
    is_dying: bool = False
    has_processed_current_flags: bool = False
    is_race: bool = False
    iterations_matched: int = 0
    last_death_link: float = time()
    last_entrance: int = -1
    loc_id_to_addr: Dict[int, Tuple[int, int]] = {}
    pending_death_link: bool = False
    prev_base_flags: bytes = bytes(0)
    unidentified_item_rom_ids: Dict[int, int] = {}
    used_entrances: Set[int] = set()
    whirlpool_location_id: int = -1

    def __init__(self):
        super().__init__()
        self.formatted_key_cache[ASINA_HINT_KEY] = ""
        self.formatted_key_cache[COMPRESSED_FLAGS_KEY] = ""
        self.formatted_key_cache[CURRENT_LOCATION_KEY] = ""
        self.formatted_key_cache[FOUND_ENTRANCES_KEY] = ""
        for region in regions_data.values():
            for location in region.locations:
                byte: int = location.rom_id // 8
                bit: int = location.rom_id % 8
                self.loc_id_to_addr[location.ap_id_offset + CRYSTALIS_BASE_ID] = (byte, bit)
                if location.name == ASINA_LOCATION_NAME:
                    self.asina_location_id = location.ap_id_offset + CRYSTALIS_BASE_ID
                elif location.name == WHIRLPOOL_LOCATION_NAME:
                    self.whirlpool_location_id = location.ap_id_offset + CRYSTALIS_BASE_ID

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        from CommonClient import logger
        try:
            rom_start: List[bytes] = (await bizhawk.read(ctx.bizhawk_ctx, [(0x0, 8, "PRG ROM")]))
            if rom_start != EXPECTED_START:
                logger.debug("Expected: " + str(EXPECTED_START))
                logger.debug("Found: " + str(rom_start))
                return False
            ap_label: List[bytes] = \
                (await bizhawk.read(ctx.bizhawk_ctx, [(AP_ROM_LABEL_ADDR, len(AP_ROM_LABEL[0]), "PRG ROM")]))
            if ap_label != AP_ROM_LABEL:
                logger.debug("Expected: " + str(AP_ROM_LABEL))
                logger.debug("Found: " + str(ap_label))
                return False
        except bizhawk.RequestFailedError:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True
        ctx.command_processor.commands["deathlink"] = cmd_deathlink
        logger.info(f"Crystalis APWorld Version {CRYSTALIS_APWORLD_VERSION.as_simple_string()}")
        return True


    async def process_flags(self, ctx: "BizHawkClientContext", flags: bytes):
        new_compressed_flags: int = self.compressed_flags
        for bit_index, test_bytes in enumerate(FLAG_ADDRESSES.values()):
            success: bool = False
            for test_byte in test_bytes:
                byte: int = test_byte[0]
                bit: int = test_byte[1]
                if flags[byte] & (1 << bit):
                    success = True
                    break
            if success:
                new_compressed_flags |= (1 << bit_index)
        if new_compressed_flags != self.compressed_flags:
            self.compressed_flags = new_compressed_flags
            await ctx.send_msgs([{
                "cmd": "Set",
                "key": self.formatted_key_cache[COMPRESSED_FLAGS_KEY],
                "default": 0,
                "operations": [{"operation": "or", "value": new_compressed_flags}]
            }])


    def on_package(self, ctx: "BizHawkClientContext", cmd: str, args: dict) -> None:
        if cmd == "Connected":
            # slot_data should be set now
            if "version" not in ctx.slot_data:
                err_string = f"Crystalis APWorld version mismatch. Multiworld generated without versioning; " \
                             f"local install using {CRYSTALIS_APWORLD_VERSION.as_simple_string()}"
                raise VersionException(err_string)
            else:
                generator_version: Version = tuplize_version(ctx.slot_data["version"])
                if generator_version.major != CRYSTALIS_APWORLD_VERSION.major:
                    err_string = f"Crystalis APWorld version mismatch. Multiworld generated with " \
                                 f"{ctx.slot_data['version']}; local install using " \
                                 f"{CRYSTALIS_APWORLD_VERSION.as_simple_string()}"
                    raise VersionException(err_string)
            key_item_names: Dict[str, str] = ctx.slot_data["shuffle_data"]["key_item_names"]
            for original_name, new_name in key_item_names.items():
                # want to map the new item's AP ID to the original item's in-game ID.
                self.unidentified_item_rom_ids[items_data[new_name].ap_id_offset + CRYSTALIS_BASE_ID] = \
                    items_data[original_name].rom_id
            self.formatted_key_cache[ASINA_HINT_KEY] = ASINA_HINT_KEY.format(player=ctx.slot, team=ctx.team)
            self.formatted_key_cache[COMPRESSED_FLAGS_KEY] = COMPRESSED_FLAGS_KEY.format(player=ctx.slot, team=ctx.team)
            self.formatted_key_cache[CURRENT_LOCATION_KEY] = CURRENT_LOCATION_KEY.format(player=ctx.slot, team=ctx.team)
            self.formatted_key_cache[FOUND_ENTRANCES_KEY] = FOUND_ENTRANCES_KEY.format(player=ctx.slot, team=ctx.team)
            async_start(ctx.send_msgs([{"cmd": "Get",
                                        "keys": [self.formatted_key_cache[ASINA_HINT_KEY],
                                                 self.formatted_key_cache[COMPRESSED_FLAGS_KEY],
                                                 self.formatted_key_cache[FOUND_ENTRANCES_KEY]]}]))
            if "death_link" in ctx.slot_data.keys():
                async_start(ctx.update_death_link(ctx.slot_data["death_link"]))
            else:
                async_start(ctx.update_death_link(False))
            if "is_race" in ctx.slot_data.keys():
                self.is_race = ctx.slot_data["is_race"]
        elif cmd == "Retrieved":
            if self.formatted_key_cache[ASINA_HINT_KEY] in args["keys"]:
                if args["keys"][self.formatted_key_cache[ASINA_HINT_KEY]]:
                    self.asina_hint_collected = args["keys"][self.formatted_key_cache[ASINA_HINT_KEY]]
            if self.formatted_key_cache[COMPRESSED_FLAGS_KEY] in args["keys"]:
                if args["keys"][self.formatted_key_cache[COMPRESSED_FLAGS_KEY]]:
                    self.compressed_flags = args["keys"][self.formatted_key_cache[COMPRESSED_FLAGS_KEY]]
            if self.formatted_key_cache[FOUND_ENTRANCES_KEY] in args["keys"]:
                if args["keys"][self.formatted_key_cache[FOUND_ENTRANCES_KEY]]:
                    self.used_entrances = set(args["keys"][self.formatted_key_cache[FOUND_ENTRANCES_KEY]])
        elif cmd == "Bounced":
            tags = args.get("tags", [])
            # we can skip checking "DeathLink" in ctx.tags, as otherwise we wouldn't have been sent this
            if "DeathLink" in tags and self.last_death_link != args["data"]["time"]:
                self.pending_death_link = True
                self.last_death_link = max(args["data"]["time"], self.last_death_link)

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            read_value = await bizhawk.read(ctx.bizhawk_ctx, [(BASE_FLAGS_ADDR, 96, "System Bus"),
                                                              (RECEIVED_INDEX_ADDR, 2, "System Bus"),
                                                              (GET_ITEM_FLAG_ADDR, 2, "System Bus"),
                                                              (GAME_MODE_ADDR, 1, "System Bus"),
                                                              (MAIN_LOOP_MODE_ADDR, 1, "System Bus"),
                                                              (CURRENT_LOCATION_ADDR, 2, "System Bus"),
                                                              (START_OF_CONSUMABLE_INV_ADDR, 8, "System Bus"),
                                                              (START_OF_SWORD_INV_ADDR, 4, "System Bus")])
            if read_value is not None:
                base_flags = read_value[0]
                game_mode = read_value[3][0]
                main_loop_mode = read_value[4][0]
                if main_loop_mode == MAIN_LOOP_GAME and game_mode in [GAME_MODE_NORMAL, GAME_MODE_TRIGGER_TILE]:
                    if self.is_dying:
                        # finished this death, reset the variables
                        self.is_dying = False
                        self.pending_death_link = False
                    elif self.pending_death_link:
                        await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                    [(HP_ADDR, [0], "System Bus")],
                                                    [(MAIN_LOOP_MODE_ADDR, [MAIN_LOOP_GAME], "System Bus")])
                        return  # might as well bail now
                    location_flags = base_flags[0x20:0x30]
                    if base_flags == self.prev_base_flags:
                        self.iterations_matched = min(self.iterations_matched + 1, ITERATIONS_TO_MATCH)
                        if self.iterations_matched >= ITERATIONS_TO_MATCH:
                            locations_to_send: List[int] = []
                            for location_id in ctx.missing_locations:
                                byte, bit = self.loc_id_to_addr[location_id]
                                if location_flags[byte] & (1 << bit):
                                    locations_to_send.append(location_id)
                                    ctx.locations_checked.add(location_id)

                            if locations_to_send:
                                async_start(ctx.send_msgs([{
                                    "cmd": "LocationChecks",
                                    "locations": list(locations_to_send)
                                }]))
                                return  # Bail now to keep this loop short

                            if not self.asina_hint_collected:
                                byte, bit = self.loc_id_to_addr[self.asina_location_id]
                                if location_flags[byte] & (1 << bit):
                                    self.asina_hint_collected = True
                                    async_start(ctx.send_msgs([{
                                        "cmd": "LocationScouts",
                                        "locations": [self.whirlpool_location_id],
                                        "create_as_hint": 2
                                    },
                                        {
                                            "cmd": "Set",
                                            "key": self.formatted_key_cache[ASINA_HINT_KEY],
                                            "default": True,
                                            "want_reply": False,
                                            "operations": [{"operation": "replace", "value": True}]
                                        }]))

                            if self.is_race and not self.has_processed_current_flags:
                                self.has_processed_current_flags = True
                                async_start(self.process_flags(ctx, copy.deepcopy(base_flags)))

                    else:
                        self.iterations_matched = 0
                        self.prev_base_flags = base_flags
                        self.has_processed_current_flags = False

                    get_item_flag: bool = read_value[2][1] != 0
                    item_flags: bytes = base_flags[0x40:0x50]
                    received_crystalis: bool = item_flags[0] & 16 != 0
                    if not get_item_flag and not received_crystalis and location_flags[0] & 16 != 0:
                        await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                    [(GET_ITEM_FLAG_ADDR, [0, 1, CRYSTALIS_SWORD_ITEM_ID], "System Bus")],
                                                    [(MAIN_LOOP_MODE_ADDR, [MAIN_LOOP_GAME], "System Bus")])
                    received_indices: bytes = read_value[1]
                    nonconsumable_index: int = received_indices[0]
                    consumable_index: int = received_indices[1]
                    new_location: int = read_value[5][0]
                    if new_location != self.current_location:
                        self.current_location = new_location
                        async_start(ctx.send_msgs([{
                            "cmd": "Set",
                            "key": self.formatted_key_cache[CURRENT_LOCATION_KEY],
                            "default": 0,
                            "want_reply": False,
                            "operations": [{"operation": "replace", "value": new_location}]
                        }]), name="send current_location")
                    new_entrance: int = (new_location << 8) + read_value[5][1]
                    if new_entrance != self.last_entrance:
                        self.last_entrance = new_entrance
                        if new_entrance not in self.used_entrances:
                            self.used_entrances.add(new_entrance)
                            async_start(ctx.send_msgs([{
                                "cmd": "Set",
                                "key": self.formatted_key_cache[FOUND_ENTRANCES_KEY],
                                "default": 0,
                                "want_reply": False,
                                "operations": [{"operation": "replace", "value": self.used_entrances}]
                            }]), name="send used_entrances")
                    # if we're not already processing an item and we're not in Mezame Shrine...
                    # Prevent receiving items in Mezame Shrine to make reloading saves for asyncs a bit smoother.
                    if not get_item_flag and self.current_location != 0:
                        if nonconsumable_index + consumable_index < len(ctx.items_received):
                            non_consumables = [item for item in ctx.items_received if
                                               "Consumable" not in items_data_by_id[item.item].groups]
                            if nonconsumable_index < len(non_consumables):
                                item_to_write: NetworkItem = non_consumables[nonconsumable_index]
                                unique: bool = items_data_by_id[item_to_write.item].unique
                                item_id: int
                                if item_to_write.item in self.unidentified_item_rom_ids.keys():
                                    item_id = self.unidentified_item_rom_ids[item_to_write.item]
                                else:
                                    item_id = items_data_by_id[item_to_write.item].rom_id
                                item_metadata: int = 0
                                if item_id == SWORD_OF_THUNDER_ITEM_ID:
                                    # manually overriding here instead of in the data files so that it doesn't get
                                    # placed incorrectly under the Eu flag
                                    unique = False
                                    # need to determine warp destination
                                    # get and parse the sword name
                                    try:
                                        item_name: str = items_data_by_id[item_to_write.item].name
                                        town_name: str = item_name.removeprefix("Sword of Thunder (").removesuffix(")")
                                        if town_name == "No Warp":
                                            item_metadata = 0 # the value doesn't matter since the game won't do anything with it
                                        else:
                                            item_metadata = TOWNS.index(town_name)
                                    except ValueError:
                                        # thunder_warp not found, silently ignore the error
                                        if CRYSTALIS_DEBUG:
                                            # ... unless we're debugging
                                            logging.error(f"Could not find town ID for thunder_warp: "
                                                          f"{ctx.slot_data['shuffle_data']['thunder_warp']}")
                                    if read_value[7][0] == CRYSTALIS_SWORD_ITEM_ID or \
                                       read_value[7][3] == SWORD_OF_THUNDER_ITEM_ID:
                                        # the player has already received at least one sword of thunder
                                        # indicate in the metadata that this shouldn't add to scaling
                                        item_metadata |= 0x10
                                byte: int = item_id // 8
                                bit: int = item_id % 8
                                if item_id == 0xFF:
                                    # if we still don't have a real ID, then this is a trap that needs metadata
                                    item_metadata = TRAP_NAME_TO_METADATA_VALUE[items_data_by_id[item_to_write.item].name]
                                    unique = True
                                    byte = 0
                                    bit = 0
                                item_flag_byte: byte = item_flags[byte] if unique \
                                    else item_flags[byte] & (0xFF ^ (1 << bit))
                                await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                            [(RECEIVED_INDEX_ADDR, [nonconsumable_index + 1],
                                                              "System Bus"),
                                                             (GET_ITEM_FLAG_ADDR, [item_metadata, 1, item_id], "System Bus"),
                                                             (ITEM_FLAGS_ADDR + byte, [item_flag_byte], "System Bus")],
                                                            [(MAIN_LOOP_MODE_ADDR, [MAIN_LOOP_GAME], "System Bus"),
                                                             (SCREEN_LOCK_ADDR, [0], "System Bus")])
                            else:
                                consumables = [item for item in ctx.items_received if
                                               "Consumable" in items_data_by_id[item.item].groups]
                                if consumable_index < len(consumables):
                                    item_to_write: NetworkItem = consumables[consumable_index]
                                    item_id: int = items_data_by_id[item_to_write.item].rom_id
                                    byte: int = item_id // 8
                                    bit: int = item_id % 8
                                    item_flag_byte: byte = item_flags[byte] & (0xFF ^ (1 << bit))
                                    await bizhawk.guarded_write(ctx.bizhawk_ctx,
                                                                [(RECEIVED_INDEX_ADDR + 1, [consumable_index + 1],
                                                                  "System Bus"),
                                                                 (GET_ITEM_FLAG_ADDR, [0, 1, item_id], "System Bus"),
                                                                 (ITEM_FLAGS_ADDR + byte, [item_flag_byte],
                                                                  "System Bus")],
                                                                [(END_OF_CONSUMABLE_INV_ADDR, [0xFF], "System Bus"),
                                                                 (MAIN_LOOP_MODE_ADDR, [MAIN_LOOP_GAME], "System Bus"),
                                                                 (SCREEN_LOCK_ADDR, [0], "System Bus")])
                elif game_mode == GAME_MODE_DYNA_DEFEATED and not ctx.finished_game:
                    async_start(ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL
                    }]))
                    ctx.finished_game = True
                elif game_mode == GAME_MODE_DEATH and main_loop_mode == MAIN_LOOP_GAME:
                    if not self.is_dying and "DeathLink" in ctx.tags:
                        self.is_dying = True
                        # check to see if we should send a death link
                        if not (self.pending_death_link or items_data["Opel Statue"].rom_id in read_value[6]):
                            # this is not a linked death, nor are we being saved by an opel; send a death link
                            async_start(ctx.send_death())
                            self.last_death_link = ctx.last_death_link

        except bizhawk.RequestFailedError:
            # Exit handler and return to main loop to reconnect.
            pass
