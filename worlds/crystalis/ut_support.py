# Python imports
from collections import defaultdict
import math

# Archipelago imports
from BaseClasses import Entrance, Region
from Options import OptionError
from Utils import VersionException
from worlds.generic.Rules import set_rule, add_rule

# Crystalis imports
from .constants import *
from .items import CrystalisItem, items_data
from .logic import has_any_level_2_sword
from .regions import entrances_data, regions_data
from .utils import *

if TYPE_CHECKING:
    from . import CrystalisWorld


def create_ut_race_regions(self: "CrystalisWorld") -> None:
    self.found_entrances_datastorage_key.append(COMPRESSED_FLAGS_KEY)
    self.created_race_regions = set()
    wall_to_region_map: defaultdict[str, set[str]] = defaultdict(set)
    wall_to_entrance_map: defaultdict[str, list[str]] = defaultdict(list)
    wall_to_location_map: defaultdict[str, list[str]] = defaultdict(list)
    boss_to_region_map: defaultdict[str, set[str]] = defaultdict(set)
    boss_to_entrance_map: defaultdict[str, list[str]] = defaultdict(list)
    boss_to_location_map: defaultdict[str, list[str]] = defaultdict(list)
    key_item_to_region_map: defaultdict[str, list[str]] = defaultdict(list)

    # track all the logic we need to adjust in UT race mode
    for region_data in regions_data.values():
        for key_item in region_data.associated_shuffle_data:
            key_item_to_region_map[key_item].append(region_data.name)
        for entrance_data in region_data.entrances:
            if entrance_data.associated_shuffle_data in WALL_NAMES:
                wall_to_region_map[entrance_data.associated_shuffle_data].add(region_data.name)
                wall_to_entrance_map[entrance_data.associated_shuffle_data].append(entrance_data.name)
            if entrance_data.associated_shuffle_data in BOSS_NAMES:
                boss_to_region_map[entrance_data.associated_shuffle_data].add(region_data.name)
                boss_to_entrance_map[entrance_data.associated_shuffle_data].append(entrance_data.name)
        for location_data in region_data.locations:
            if location_data.associated_shuffle_data in WALL_NAMES:
                wall_to_region_map[location_data.associated_shuffle_data].add(region_data.name)
                wall_to_location_map[location_data.associated_shuffle_data].append(location_data.name)
            if location_data.associated_shuffle_data in BOSS_NAMES:
                boss_to_region_map[location_data.associated_shuffle_data].add(region_data.name)
                boss_to_location_map[location_data.associated_shuffle_data].append(location_data.name)
    if self.options.vanilla_dolphin:
        key_item_to_region_map["Shell Flute"] = ["Fisherman"]

    #   - walls
    if self.options.randomize_wall_elements:
        for wall in WALL_NAMES:
            if wall == "East Cave" and self.options.vanilla_maps.value != self.options.vanilla_maps.option_GBC_cave:
                continue
            # make wall viewing and broken regions
            wall_viewing_region: Region = Region(f"Deferred Region: {wall}", self.player, self.multiworld)
            self.multiworld.regions.append(wall_viewing_region)
            wall_broken_region: Region = Region(f"Event Region: {wall}", self.player, self.multiworld)
            self.multiworld.regions.append(wall_broken_region)
            # make wall broken event
            wall_broken_event_location: CrystalisLocation = \
                CrystalisLocation(self.player, f"Has Broken Wall {wall}", None, wall_broken_region)
            wall_broken_event_item: CrystalisItem = \
                CrystalisItem(f"Has Broken Wall {wall}", ItemClassification.progression, None, self.player)
            wall_broken_event_location.place_locked_item(wall_broken_event_item)
            wall_broken_region.locations.append(wall_broken_event_location)
            # make the dangling entrance that will be deferred
            deferred_wall_entrance: Entrance = wall_viewing_region.create_exit(f"Check {wall} Wall")
            if self.options.orbs_not_required:
                set_rule(deferred_wall_entrance, lambda state: state.has_group("Sword", self.player, 1))
            else:
                set_rule(deferred_wall_entrance, lambda state: has_any_level_2_sword(state, self.player))
            # connect the relevant regions to the wall viewing region
            for region_name in sorted(wall_to_region_map[wall]):
                self.get_region(region_name).connect(wall_viewing_region)
            # rewrite rules
            for location_name in wall_to_location_map[wall]:
                location: Location = self.get_location(location_name)
                set_rule(location, lambda state, wall=wall: state.has(f"Has Broken Wall {wall}", self.player))
            for entrance_name in wall_to_entrance_map[wall]:
                entrance: Entrance = self.get_entrance(entrance_name)
                set_rule(entrance, lambda state, wall=wall: state.has(f"Has Broken Wall {wall}", self.player))
                # two entrances require special handling because they have more than just the wall rule
                if entrance_name == "Mt. Sabre North - Main -> Mt. Sabre North - Upper":
                    add_rule(entrance, lambda state: state.has("Flight", self.player), "or")
                elif entrance_name == "Mt. Sabre North - Upper -> Mt. Sabre North - Interior":
                    if self.options.trigger_skip.value == self.options.trigger_skip.option_in_logic:
                        set_rule(entrance, lambda state: True)
                    else:
                        add_rule(entrance, lambda state: state.has("Flight", self.player)
                                                         or state.has("Rabbit Boots", self.player)
                                                         or state.has("Speed Boots", self.player), "or")
                        if self.options.trigger_skip.value == self.options.trigger_skip.option_out_of_logic:
                            add_rule(entrance, lambda state: state.has(self.glitches_item_name, self.player), "or")
            self.created_race_regions.add(wall)
    #   - boss weaknesses
    if self.options.randomize_monster_weaknesses:
        for boss in BOSS_NAMES:
            # make boss viewing and boss defeated regions
            boss_viewing_region: Region = Region(f"Deferred Region: {boss}", self.player, self.multiworld)
            self.multiworld.regions.append(boss_viewing_region)
            boss_defeated_region: Region = Region(f"Event Region: {boss}", self.player, self.multiworld)
            self.multiworld.regions.append(boss_defeated_region)
            # make UT boss defeated event - put UT in the name to not clash with story mode events
            boss_defeated_event_location: CrystalisLocation = \
                CrystalisLocation(self.player, f"{boss} Defeated (UT)", None, boss_defeated_region)
            boss_defeated_event_item: CrystalisItem = \
                CrystalisItem(f"{boss} Defeated (UT)", ItemClassification.progression, None, self.player)
            boss_defeated_event_location.place_locked_item(boss_defeated_event_item)
            boss_defeated_region.locations.append(boss_defeated_event_location)
            # make the dangling entrance that will be deferred
            deferred_boss_entrance: Entrance = boss_viewing_region.create_exit(f"Check {boss}")
            if boss == "Vampire 2":
                set_rule(deferred_boss_entrance, lambda state: state.has_group("Sword", self.player, 1))
            elif boss == "Giant Insect":
                set_rule(deferred_boss_entrance, \
                         lambda state: state.has_group("Sword", self.player, 1) and
                                       state.has(self.shuffle_data.key_item_names["Insect Flute"], self.player) and
                                       (state.has("Hazmat Suit", self.player) or state.has("Gas Mask", self.player)))
            elif boss == "Karmine":
                # get_tetrarch_fight_logic called with no element will get logic that checks for any correct level sword
                set_rule(deferred_boss_entrance, self.get_tetrarch_fight_logic(level=2))
            else:
                set_rule(deferred_boss_entrance, self.get_tetrarch_fight_logic())
            # connect the appropriate regions to the viewing region
            for region_name in sorted(boss_to_region_map[boss]):
                self.get_region(region_name).connect(boss_viewing_region)
            # rewrite rules
            for location_name in boss_to_location_map[boss]:
                location: Location = self.get_location(location_name)
                set_rule(location, lambda state, boss=boss: state.has(f"{boss} Defeated (UT)", self.player))
            for entrance_name in boss_to_entrance_map[boss]:
                entrance: Entrance = self.get_entrance(entrance_name)
                set_rule(entrance, lambda state, boss=boss: state.has(f"{boss} Defeated (UT)", self.player))
            self.created_race_regions.add(boss)
    #   - key items & trade-ins
    items_to_check: set[str] = set()
    keys: list[str] = [item for item in self.item_name_groups["Key"] if items_data[item].default_count > 0]
    bows: list[str] = [item for item in self.item_name_groups["Bow"] if items_data[item].default_count > 0]
    flutes: list[str] = [item for item in self.item_name_groups["Flute"] if items_data[item].default_count > 0]
    lamps: list[str] = [item for item in self.item_name_groups["Lamp"] if items_data[item].default_count > 0]
    statues: list[str] = [item for item in self.item_name_groups["Statue"] if items_data[item].default_count > 0]
    trade_ins: list[str] = [item for item in self.item_name_groups["Trade-in"] if items_data[item].default_count > 0]
    if self.options.unidentified_key_items:
        items_to_check.update(keys + bows + flutes + lamps + statues)
        self.shuffle_data.trade_in_map["Akahana"] = "Used Statue of Onyx"
        self.shuffle_data.trade_in_map["Fisherman"] = "Used Fog Lamp"
        self.shuffle_data.trade_in_map["Slimed Kensu"] = "Used Ivory Statue"
    if self.options.randomize_tradeins:
        self.shuffle_data.trade_in_map["Akahana"] = "Used Statue of Onyx"
        self.shuffle_data.trade_in_map["Aryllis"] = "Used Kirisa Plant"
        self.shuffle_data.trade_in_map["Fisherman"] = "Used Fog Lamp"
        self.shuffle_data.trade_in_map["Kensu"] = "Used Love Pendant"
        self.shuffle_data.trade_in_map["Slimed Kensu"] = "Used Ivory Statue"
        self.shuffle_data.trade_in_map["Tornel"] = "Has Checked Tornel"
        self.shuffle_data.trade_in_map["Rage"] = "Has Checked Rage"
        items_to_check.update(trade_ins)
    for key_item in sorted(items_to_check):
        # make a can check item and has used item regions
        can_check_item_region: Region = Region(f"Deferred Region: {key_item}", self.player, self.multiworld)
        self.multiworld.regions.append(can_check_item_region)
        has_used_item_region: Region = Region(f"Event Region: {key_item}", self.player, self.multiworld)
        self.multiworld.regions.append(has_used_item_region)
        # make item used event
        has_used_item_event_location: CrystalisLocation = \
            CrystalisLocation(self.player, f"{key_item} Used", None, has_used_item_region)
        has_used_item_event_item: CrystalisItem = \
            CrystalisItem(f"{key_item} Used", ItemClassification.progression, None, self.player)
        has_used_item_event_location.place_locked_item(has_used_item_event_item)
        has_used_item_region.locations.append(has_used_item_event_location)
        # make the dangling entrance that will be deferred
        deferred_key_item_entrance: Entrance = can_check_item_region.create_exit(f"Check {key_item}")
        if self.options.randomize_tradeins and key_item in trade_ins:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Trade-in", self.player))
            if key_item == "Kirisa Plant":
                add_rule(deferred_key_item_entrance, lambda state: state.has("Change", self.player))
            elif key_item == "Love Pendant":
                swan_shed_region: Region = self.get_region("Swan Shed")
                swan_pub_region: Region = self.get_region("Swan Pub")
                add_rule(deferred_key_item_entrance, lambda state: state.has("Paralysis", self.player) and
                                                                   swan_shed_region.can_reach(state) and
                                                                   swan_pub_region.can_reach(state))
                self.multiworld.register_indirect_condition(swan_shed_region, deferred_key_item_entrance)
                self.multiworld.register_indirect_condition(swan_pub_region, deferred_key_item_entrance)
        elif key_item in keys:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Key", self.player))
        elif key_item in bows:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Bow", self.player))
        elif key_item in flutes:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Flute", self.player))
            if key_item == "Insect Flute":
                add_rule(deferred_key_item_entrance, lambda state: state.has("Hazmat Suit", self.player) or
                                                                   state.has("Gas Mask", self.player))
        elif key_item in statues:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Statue", self.player))
            if key_item == "Broken Statue":
                add_rule(deferred_key_item_entrance, lambda state: state.has_group("Lamp", self.player))
        elif key_item in lamps:
            set_rule(deferred_key_item_entrance, lambda state: state.has_group("Lamp", self.player))
            if key_item == "Glowing Lamp":
                add_rule(deferred_key_item_entrance, lambda state: state.has_group("Statue", self.player))
        else:
            raise KeyError(f"Key {key_item} not recognized")
        # connect the appropriate regions to the can check region
        for region_name in key_item_to_region_map[key_item]:
            if region_name == "Waterfall Valley - By Prison" and self.options.shuffle_areas:
                # don't connect the back prison entrance if Wa is on
                continue
            can_check_entrance: Entrance = self.get_region(region_name).connect(can_check_item_region)
            # some of these need special handling
            if key_item == "Alarm Flute" and region_name == "Windmill Cave":
                leaf_elder_region: Region = self.get_region("Leaf Elder's House")
                zebu_student_region: Region = self.get_region("Zebu Student's House")
                zebu_region: Region = self.get_region("Zebu's Cave - Front")
                # need logic to spawn the sleeping windmill guard
                set_rule(can_check_entrance, lambda state: leaf_elder_region.can_reach(state) and
                                                           zebu_student_region.can_reach(state) and
                                                           zebu_region.can_reach(state))
                # also need to register some indirect connections
                self.multiworld.register_indirect_condition(leaf_elder_region, can_check_entrance)
                self.multiworld.register_indirect_condition(zebu_student_region, can_check_entrance)
                self.multiworld.register_indirect_condition(zebu_region, can_check_entrance)
        if key_item in self.shuffle_data.key_item_names:
            self.shuffle_data.key_item_names[key_item] = f"{key_item} Used"
        self.created_race_regions.add(key_item)
    # handle the two weird trade-ins
    if self.options.randomize_tradeins:
        # make can check and has checked regions for Tornel
        can_check_tornel_region: Region = Region("Deferred Region: Tornel", self.player, self.multiworld)
        self.multiworld.regions.append(can_check_tornel_region)
        has_checked_tornel_region: Region = Region(f"Event Region: Tornel", self.player, self.multiworld)
        self.multiworld.regions.append(has_checked_tornel_region)
        # make event item for Tornel
        has_checked_tornel_event_location: CrystalisLocation = \
            CrystalisLocation(self.player, "Has Checked Tornel", None, has_checked_tornel_region)
        has_checked_tornel_event_item: CrystalisItem = \
            CrystalisItem("Has Checked Tornel", ItemClassification.progression, None, self.player)
        has_checked_tornel_event_location.place_locked_item(has_checked_tornel_event_item)
        has_checked_tornel_region.locations.append(has_checked_tornel_event_location)
        # make the dangling entrance that will be deferred
        deferred_tornel_entrance: Entrance = can_check_tornel_region.create_exit("Check Tornel")
        set_rule(deferred_tornel_entrance,
                 lambda state: state.has_group_unique("Wind Upgrades", self.player, 2) or
                               state.has_group_unique("Fire Upgrades", self.player, 2) or
                               state.has_group_unique("Water Upgrades", self.player, 2) or
                               state.has_group_unique("Thunder Upgrades", self.player, 2))
        # connect the real regions to the can check region
        for region_name in key_item_to_region_map["Tornel"]:
            self.get_region(region_name).connect(can_check_tornel_region)
        # because Tornel normally checks a group, we need to just overwrite his rule
        tornel_location: Location = self.get_location("Mt Sabre West Tornel")
        set_rule(tornel_location, lambda state: state.has("Has Checked Tornel", self.player))
        self.created_race_regions.add("Tornel")
        # rinse and repeat for Rage
        # make can check and has checked regions for Rage
        can_check_rage_region: Region = Region("Deferred Region: Rage", self.player, self.multiworld)
        self.multiworld.regions.append(can_check_rage_region)
        has_checked_rage_region: Region = Region(f"Event Region: Rage", self.player, self.multiworld)
        self.multiworld.regions.append(has_checked_rage_region)
        # make event item for Rage
        has_checked_rage_event_location: CrystalisLocation = \
            CrystalisLocation(self.player, "Has Checked Rage", None, has_checked_rage_region)
        has_checked_rage_event_item: CrystalisItem = \
            CrystalisItem("Has Checked Rage", ItemClassification.progression, None, self.player)
        has_checked_rage_event_location.place_locked_item(has_checked_rage_event_item)
        has_checked_rage_region.locations.append(has_checked_rage_event_location)
        # make the dangling entrance that will be deferred
        deferred_rage_entrance: Entrance = can_check_rage_region.create_exit("Check Rage")
        set_rule(deferred_rage_entrance, lambda state: state.has_group("Sword", self.player))
        # connect the real regions to the can check region
        for region_name in key_item_to_region_map["Rage"]:
            self.get_region(region_name).connect(can_check_rage_region)
        self.created_race_regions.add("Rage")


def defer_entrances(self: "CrystalisWorld"):
    # set up the variables to connect entrances later
    self.found_entrances_datastorage_key.append(FOUND_ENTRANCES_KEY)
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
    if key.startswith(FOUND_ENTRANCES_KEY.removesuffix("{team}_{player}")):
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
    elif key.startswith(COMPRESSED_FLAGS_KEY.removesuffix("{team}_{player}")):
        def bit_iterator(bits):
            while bits:
                bit = bits & (~bits + 1)
                yield int(math.log2(bit))
                bits ^= bit
        flag_names: list[str] = list(FLAG_ADDRESSES.keys())
        for bit_index in bit_iterator(value):
            current_flag: str = flag_names[bit_index]
            if current_flag in self.created_race_regions:
                deferred_region: Region = self.get_region(f"Deferred Region: {current_flag}")
                deferred_entrance: Entrance = deferred_region.exits[0]
                if deferred_entrance.connected_region is None:
                    event_region: Region = self.get_region(f"Event Region: {current_flag}")
                    deferred_entrance.connect(event_region)
    if CRYSTALIS_DEBUG:
        visualize_regions(self, "Crystalis Visualized.puml")
    return


def setup_from_slot_data(self: "CrystalisWorld", slot_data: dict[str, Any]):
    self.using_ut = True
    self.found_entrances_datastorage_key = []
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
    shuffle_dict: Dict[str, Any] = slot_data["shuffle_data"]
    self.shuffle_data = CrystalisShuffleData(shuffle_dict["wall_map"], shuffle_dict["key_item_names"],
                                                 shuffle_dict["trade_in_map"], shuffle_dict["boss_reqs"],
                                                 shuffle_dict["gbc_cave_exits"], shuffle_dict["thunder_warp"],
                                                 shuffle_dict["shop_inventories"], shuffle_dict["wildwarps"],
                                                 shuffle_dict["goa_connection_map"], shuffle_dict["er_pairings"])
    # goa upper floors vs. goa lower floors doesn't matter for UT, so use default values
    self.goa_lower_floors = {"Kelbesque", "Sabera"}
    self.goa_upper_floors = {"Mado", "Karmine"}