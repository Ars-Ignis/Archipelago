from typing import Any
from BaseClasses import Entrance, Region
from Options import OptionError
from Utils import VersionException
from .constants import *
from .regions import entrances_data
from .utils import *

if TYPE_CHECKING:
    from . import CrystalisWorld


def create_ut_race_regions(self: "CrystalisWorld") -> None:
    # things to cover:
    #   - walls
    #       - get a list of entrances representing walls
    #       - disconnect them
    #       - rewrite the logic - might be a separate function?
    #   - boss weaknesses
    #       - Bosses are entrances? disconnect them
    #       - rewrite logic - probably need get_tetrarch_fight_logic
    #   - key items
    #       - create new regions for each spot a key item can be used?
    #           -
    #   - trade-ins
    pass


def defer_entrances(self: "CrystalisWorld"):
    # set up the variables to connect entrances later
    self.found_entrances_datastorage_key = "Slot_{player}_found_entrances"
    self.found_entrances = set()
    self.found_towns = set()
    self.in_game_id_to_entrance_name = {}
    for entrance_data in list(entrances_data.values()):
        if entrance_data.in_game_id != -1:
            self.in_game_id_to_entrance_name[entrance_data.in_game_id] = entrance_data.name
    # a couple of entrances shift based on map settings; all the ones stored above assume vanilla or GBC cave maps
    if self.options.vanilla_maps == self.options.vanilla_maps.option_lime_passage:
        self.in_game_id_to_entrance_name[0x0306] = "Wind Valley - East"
        self.in_game_id_to_entrance_name[0x4202] = "Lime Valley - West"
    elif self.options.vanilla_maps == self.options.vanilla_maps.option_GBC_cave:
        # Lime Valley and Desert 2 are consistent
        if "Cordel Plains - Main" in self.shuffle_data.gbc_cave_exits:
            # Cordel Plains gets weird because of the seamless transition across the bridge
            del self.in_game_id_to_entrance_name[0x1405]  # unused
            self.in_game_id_to_entrance_name[0x1406] = "Cordel Plains - South West"
            self.in_game_id_to_entrance_name[0x1407] = "Cordel Plains - South"
            del self.in_game_id_to_entrance_name[0x1503]  # unused
            self.in_game_id_to_entrance_name[0x1504] = "Cordel Plains - East"
        if "Goa Valley" in self.shuffle_data.gbc_cave_exits:
            self.in_game_id_to_entrance_name[0x7801] = "Goa Valley - Added Cave"
            self.in_game_id_to_entrance_name[0x7802] = "Goa Valley - Palace"
            self.in_game_id_to_entrance_name[0x7803] = "Goa Valley - Left"
            self.in_game_id_to_entrance_name[0x7804] = "Goa Valley - Down"

    for entrance_name_a, entrance_name_b in self.shuffle_data.er_pairings.items():
        entrance_a: Entrance = self.get_entrance(entrance_name_a)
        entrance_a.connected_region = None
        entrance_b: Entrance = self.get_entrance(entrance_name_b)
        entrance_b.connected_region = None
    if self.options.shuffle_goa:
        for goa_entrance_name in self.shuffle_data.goa_connection_map.keys():
            goa_entrance: Entrance = self.get_entrance(goa_entrance_name)
            goa_entrance.connected_region = None
    if CRYSTALIS_DEBUG:
        visualize_regions(self, "Crystalis Visualized.puml")


def reconnect_found_entrances(self: "CrystalisWorld", key: str, value: Any) -> None:
    if value is None or key is None:
        return
    for in_game_id in value:
        if in_game_id not in self.found_entrances:
            self.found_entrances.add(in_game_id)
            if in_game_id in self.in_game_id_to_entrance_name:
                entrance_name_to_connect = self.in_game_id_to_entrance_name[in_game_id]
                # if the entrance is one that was shuffled, connect it
                if entrance_name_to_connect in self.shuffle_data.er_pairings:
                    entrance_to_connect: Entrance = self.get_entrance(entrance_name_to_connect)
                    connected_entrance_name = self.shuffle_data.er_pairings[entrance_name_to_connect]
                    connected_entrance: Entrance = self.get_entrance(connected_entrance_name)
                    entrance_to_connect.connected_region = connected_entrance.parent_region
                    connected_entrance.connected_region = entrance_to_connect.parent_region
                elif entrance_name_to_connect in self.shuffle_data.goa_connection_map:
                    entrance_to_connect: Entrance = self.get_entrance(entrance_name_to_connect)
                    connected_region_name: str = self.shuffle_data.goa_connection_map[entrance_name_to_connect]
                    connected_region: Region = self.get_region(connected_region_name)
                    entrance_to_connect.connected_region = connected_region
                    connected_entrance: Entrance
                    for connected_entrance in connected_region.exits:
                        if not connected_entrance.connected_region:
                            break
                    else:
                        continue
                    connected_entrance.connected_region = entrance_to_connect.parent_region
            # connect a warp entrance for found towns
            screen_id: int = 0xFF00 & in_game_id
            if screen_id in TOWNS_WITH_IDS and screen_id not in self.found_towns:
                self.found_towns.add(screen_id)
                town_name: str = TOWNS_WITH_IDS[screen_id]
                town_region: Region = self.get_region(town_name)
                menu_region: Region = self.get_region("Menu")
                menu_region.connect(town_region, f"Teleport to {town_name}",
                                    lambda state: state.has("Teleport", self.player) or
                                                  state.has("Buy Warp Boots", self.player))
    if CRYSTALIS_DEBUG:
        visualize_regions(self, "Crystalis Visualized.puml")
    return


def setup_from_slot_data(self: "CrystalisWorld", slot_data: dict[str, Any]):
    self.using_ut = True
    if "version" not in slot_data:
        err_string = f"Crystalis APWorld version mismatch. Multiworld generated without versioning; " \
                     f"local install using {self.world_version.as_simple_string()}"
        raise VersionException(err_string)
    else:
        generator_version: Version = tuplize_version(slot_data["version"])
        if generator_version.major != self.world_version.major:
            err_string = f"Crystalis APWorld version mismatch. Multiworld generated with " \
                         f"{slot_data['version']}; local install using " \
                         f"{self.world_version.as_simple_string()}"
            raise VersionException(err_string)
    self.is_race = slot_data["is_race"]
    self.using_ut_deferred_entrances = self.multiworld.enforce_deferred_connections in ("on", "default") or self.is_race
    if self.is_race and self.multiworld.enforce_deferred_connections in ["off"]:
        err_string = "Crystalis: enforce_deferred_entrances must be set to 'on' or 'default' when in race mode. " \
                     "Please change the setting in the universal_tracker section of host.yaml and restart UT."
        raise OptionError(err_string)
    self.options.randomize_maps.value = slot_data["randomize_maps"]
    self.options.shuffle_areas.value = slot_data["shuffle_areas"]
    self.options.shuffle_houses.value = slot_data["shuffle_houses"]
    self.options.randomize_tradeins.value = slot_data["randomize_tradeins"]
    self.options.unidentified_key_items.value = slot_data["unidentified_key_items"]
    self.options.randomize_wall_elements = slot_data["randomize_wall_elements"]
    self.options.shuffle_goa.value = slot_data["shuffle_goa"]
    self.options.randomize_wild_warp.value = slot_data["randomize_wild_warp"]
    self.options.story_mode.value = slot_data["story_mode"]
    self.options.no_bow_mode.value = slot_data["no_bow_mode"]
    self.options.orbs_not_required.value = slot_data["orbs_not_required"]
    self.options.thunder_warp.value = slot_data["thunder_warp"]
    self.options.vanilla_dolphin.value = slot_data["vanilla_dolphin"]
    self.options.fake_flight.value = slot_data["fake_flight"]
    self.options.statue_glitch.value = slot_data["statue_glitch"]
    self.options.mt_sabre_skip.value = slot_data["mt_sabre_skip"]
    self.options.statue_gauntlet_skip.value = slot_data["statue_gauntlet_skip"]
    self.options.sword_charge_glitch.value = slot_data["sword_charge_glitch"]
    self.options.trigger_skip.value = slot_data["trigger_skip"]
    self.options.rage_skip.value = slot_data["rage_skip"]
    self.options.randomize_monster_weaknesses.value = slot_data["randomize_monster_weaknesses"]
    self.options.oops_all_mimics.value = slot_data["oops_all_mimics"]
    self.options.dont_shuffle_mimics.value = slot_data["dont_shuffle_mimics"]
    self.options.keep_unique_items_and_consumables_separate.value = \
        slot_data["keep_unique_items_and_consumables_separate"]
    self.options.guarantee_refresh.value = slot_data["guarantee_refresh"]
    self.options.battle_magic_not_guaranteed.value = slot_data["battle_magic_not_guaranteed"]
    self.options.tink_mode.value = slot_data["tink_mode"]
    self.options.barrier_not_guaranteed.value = slot_data["barrier_not_guaranteed"]
    self.options.gas_mask_not_guaranteed.value = slot_data["gas_mask_not_guaranteed"]
    self.options.charge_shots_only.value = slot_data["charge_shots_only"]
    self.options.dont_buff_bonus_items.value = slot_data["dont_buff_bonus_items"]
    self.options.vanilla_maps.value = slot_data["vanilla_maps"]
    self.options.vanilla_wild_warp.value = slot_data["vanilla_wild_warp"]
    if not self.is_race: # not convinced of this, may be removed
        shuffle_dict: Dict[str, Any] = slot_data["shuffle_data"]
        self.shuffle_data = CrystalisShuffleData(shuffle_dict["wall_map"], shuffle_dict["key_item_names"],
                                                 shuffle_dict["trade_in_map"], shuffle_dict["boss_reqs"],
                                                 shuffle_dict["gbc_cave_exits"], shuffle_dict["thunder_warp"],
                                                 shuffle_dict["shop_inventories"], shuffle_dict["wildwarps"],
                                                 shuffle_dict["goa_connection_map"], shuffle_dict["er_pairings"])
    # goa upper floors vs. goa lower floors doesn't matter for UT, so use default values
    self.goa_lower_floors = {"Kelbesque", "Sabera"}
    self.goa_upper_floors = {"Mado", "Karmine"}