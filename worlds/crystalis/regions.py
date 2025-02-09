import logging
from BaseClasses import Region, ItemClassification, EntranceType
from .types import CrystalisRegionData, CrystalisLocationData, CrystalisEntranceData, CrystalisEntranceTypeEnum
from .locations import CrystalisLocation, create_location_from_location_data
from .items import CrystalisItem
import orjson
from typing import Dict, List, Set, NamedTuple
import pkgutil
from worlds.generic.Rules import set_rule

try:
    from entrance_rando import randomize_entrances, EntranceRandomizationError
except ImportError:
    logging.warning("Generic Entrance Randomizer not found in core code; please run this apworld against a version of"
                    "Archipelago greater than 0.5.1 to support shuffle_houses and shuffle_areas. These options will"
                    "be turned off.")


HOUSE_SHUFFLE_TYPES = [CrystalisEntranceTypeEnum.HOUSE_ENTRANCE,
                       CrystalisEntranceTypeEnum.HOUSE_EXIT,
                       CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                       CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                       CrystalisEntranceTypeEnum.SHED_ENTRANCE,
                       CrystalisEntranceTypeEnum.SHED_EXIT,
                       CrystalisEntranceTypeEnum.EXT_ENTRANCE,
                       CrystalisEntranceTypeEnum.EXT_EXIT]
AREA_SHUFFLE_TYPES =  [CrystalisEntranceTypeEnum.OW_UP,
                       CrystalisEntranceTypeEnum.OW_DOWN,
                       CrystalisEntranceTypeEnum.OW_LEFT,
                       CrystalisEntranceTypeEnum.OW_RIGHT,
                       CrystalisEntranceTypeEnum.CAVE_ENTRANCE,
                       CrystalisEntranceTypeEnum.CAVE_EXIT,
                       CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                       CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                       CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE,
                       CrystalisEntranceTypeEnum.PALACE_AREA_EXIT]
SHUFFLE_GROUPING = {
    CrystalisEntranceTypeEnum.OW_UP: [CrystalisEntranceTypeEnum.OW_DOWN],
    CrystalisEntranceTypeEnum.OW_DOWN: [CrystalisEntranceTypeEnum.OW_UP],
    CrystalisEntranceTypeEnum.OW_LEFT: [CrystalisEntranceTypeEnum.OW_RIGHT],
    CrystalisEntranceTypeEnum.OW_RIGHT: [CrystalisEntranceTypeEnum.OW_LEFT],
    CrystalisEntranceTypeEnum.CAVE_ENTRANCE: [CrystalisEntranceTypeEnum.CAVE_EXIT],
    CrystalisEntranceTypeEnum.CAVE_EXIT: [CrystalisEntranceTypeEnum.CAVE_ENTRANCE],
    CrystalisEntranceTypeEnum.HOUSE_ENTRANCE: [CrystalisEntranceTypeEnum.HOUSE_EXIT],
    CrystalisEntranceTypeEnum.HOUSE_EXIT: [CrystalisEntranceTypeEnum.HOUSE_ENTRANCE],
    CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE: [CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                                                CrystalisEntranceTypeEnum.PALACE_AREA_EXIT],
    CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT: [CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                                            CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE],
    CrystalisEntranceTypeEnum.SHED_ENTRANCE: [CrystalisEntranceTypeEnum.SHED_EXIT],
    CrystalisEntranceTypeEnum.SHED_EXIT: [CrystalisEntranceTypeEnum.SHED_ENTRANCE],
    CrystalisEntranceTypeEnum.EXT_ENTRANCE: [CrystalisEntranceTypeEnum.EXT_EXIT],
    CrystalisEntranceTypeEnum.EXT_EXIT: [CrystalisEntranceTypeEnum.EXT_ENTRANCE],
    CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE: [CrystalisEntranceTypeEnum.PALACE_AREA_EXIT,
                                                     CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT],
    CrystalisEntranceTypeEnum.PALACE_AREA_EXIT: [CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE,
                                                 CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE]
}
GBC_CAVE_NAMES = [
    "Cordel Plains - Main - Added Cave",
    "Lime Valley - Added Cave",
    "Goa Valley - Added Cave",
    "Desert 2 - Added Cave",
    "Wind Valley - East Cave",
    "GBC Cave - Free Exit",
    "GBC Cave - Blocked Exit"
]

def load_region_data_from_json() -> Dict[str, CrystalisRegionData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/regions.json").decode("utf-8-sig"))


regions_data_json = load_region_data_from_json()
regions_data: Dict[str, CrystalisRegionData] = {}
entrances_data: Dict[str, CrystalisEntranceData] = {}
#convert to actual type
for key, value in regions_data_json.items():
    region_locations_data: List[CrystalisLocationData] = []
    for location_data in value["locations"]:
        new_loc = CrystalisLocationData(location_data["name"], location_data["rom_id"],
                                        location_data["ap_id_offset"], location_data["unique"],
                                        location_data["lossy"], location_data["prevent_loss"],
                                        location_data["is_chest"])
        region_locations_data.append(new_loc)
    new_entrance_data: List[CrystalisEntranceData] = []
    for entrance_data in value["entrances"]:
        name: str = entrance_data["name"]
        if name == "":
            name = key + " -> " + entrance_data["vanilla_target"]
        new_ent = CrystalisEntranceData(name, entrance_data["entrance_type"], entrance_data["vanilla_target"],
                                        entrance_data["exit_key"], entrance_data["house_key"],
                                        entrance_data["related_entrance"], entrance_data["house_type"],
                                        entrance_data["can_lock"])
        new_entrance_data.append(new_ent)
        entrances_data[name] = new_ent
    regions_data[key] = CrystalisRegionData(value["name"], value["wildwarpIds"], new_entrance_data,
                                            region_locations_data, value["ban_wildwarp"])


def create_regions(self) -> None:
    #first make regions and locations
    #need to cache while still creating regions before appending them to the multiworld
    local_region_cache = {}
    self.locations_data = []
    for region_data in regions_data.values():
        if self.options.vanilla_maps != self.options.vanilla_maps.option_GBC_cave and "GBC" in region_data.name:
            # don't add GBC cave regions, locations, and entrances
            continue
        region = Region(region_data.name, self.player, self.multiworld)
        local_region_cache[region_data.name] = region
        for location_data in region_data.locations:
            if not self.options.shuffle_areas and not self.options.shuffle_houses and "Mezame" in location_data.name:
                # Mezame Shrine chests only exist if areas or houses are shuffled, to grow sphere 1
                continue
            if (self.options.shuffle_houses or self.options.shuffle_areas) and location_data.name == "Zebu Student":
                # Zebu's student doesn't grant an item if houses or areas are shuffled
                continue
            if self.options.vanilla_dolphin and "Kensu In Cabin" == location_data.name:
                # Kensu in Cabin just activates the flute if vanilla dolphin is on
                continue
            # now that we know the location exists, add it to the multiworld
            self.locations_data.append(location_data)
            location: CrystalisLocation = create_location_from_location_data(self.player, location_data, region)
            region.locations.append(location)
            if self.options.dont_shuffle_mimics and "Mimic" in location_data.name:
                location.place_locked_item(self.create_item("Mimic"))
    # then make entrances
    self.shared_icon_houses = []
    self.houses_by_type = {}
    self.tunnel_map = {}
    self.cave_entrances = []
    self.cave_exits = []
    for region_data in regions_data.values():
        if region_data.name in local_region_cache.keys():
            region = local_region_cache[region_data.name]
            for entrance_data in region_data.entrances:
                if entrance_data.vanilla_target in local_region_cache:
                    if entrance_data.entrance_type == CrystalisEntranceTypeEnum.STATIC:
                        connecting_region = local_region_cache[entrance_data.vanilla_target]
                        region.connect(connecting_region, entrance_data.name)
                    elif entrance_data.entrance_type == CrystalisEntranceTypeEnum.GOA_TRANSITION and \
                         self.options.shuffle_goa:
                        #connect according to the shuffle
                        connecting_region_name = self.shuffle_data.goa_connection_map[entrance_data.name]
                        connecting_region = local_region_cache[connecting_region_name]
                        region.connect(connecting_region, entrance_data.name)
                    else:
                        if (self.options.shuffle_houses and entrance_data.entrance_type in HOUSE_SHUFFLE_TYPES) or \
                           (self.options.shuffle_areas and entrance_data.entrance_type in AREA_SHUFFLE_TYPES):
                            exit = region.create_exit(entrance_data.name)
                            exit.randomization_group = entrance_data.entrance_type
                            exit.randomization_type = EntranceType.TWO_WAY
                            er_target = region.create_er_target(entrance_data.name)
                            er_target.randomization_group = entrance_data.entrance_type
                            er_target.randomization_type = EntranceType.TWO_WAY
                            # track the entrance for later if necessary
                            if entrance_data.entrance_type == CrystalisEntranceTypeEnum.CAVE_ENTRANCE:
                                self.cave_entrances.append([exit, er_target])
                            if entrance_data.entrance_type == CrystalisEntranceTypeEnum.CAVE_EXIT:
                                self.cave_exits.append([exit, er_target])
                            if entrance_data.related_entrance != "":
                                if entrance_data.entrance_type == CrystalisEntranceTypeEnum.HOUSE_ENTRANCE:
                                    self.shared_icon_houses.append([exit, er_target])
                                elif entrance_data.entrance_type == CrystalisEntranceTypeEnum.CAVE_EXIT:
                                    self.tunnel_map[entrance_data.name] = [entrance_data.related_entrance]
                            if entrance_data.house_type != "":
                                if entrance_data.house_type in self.houses_by_type:
                                    self.houses_by_type[entrance_data.house_type].append([exit, er_target])
                                else:
                                    self.houses_by_type[entrance_data.house_type] = [[exit, er_target]]
                        else:
                            connecting_region = local_region_cache[entrance_data.vanilla_target]
                            region.connect(connecting_region, entrance_data.name)
            self.multiworld.regions.append(region)
    #add conditional entrances
    if self.options.no_bow_mode:
        #tower shortcut for Rb
        #technically the normal path to Tower should be removed, but it should be redundant in all cases
        #famous last words lmao
        mezame_shrine = local_region_cache["Mezame Shrine"]
        pre_draygon = local_region_cache["Crypt - Pre-Draygon"]
        mezame_shrine.connect(pre_draygon, "Draygon 2 Shortcut")
    if self.options.vanilla_maps == self.options.vanilla_maps.option_GBC_cave:
        wind_valley = local_region_cache["Wind Valley"]
        gbc_main = local_region_cache["GBC Cave - Main"]
        gbc_blocked = local_region_cache["GBC Cave - Past Block"]
        free_region = local_region_cache[self.shuffle_data.gbc_cave_exits[0]]
        blocked_region = local_region_cache[self.shuffle_data.gbc_cave_exits[1]]
        if self.options.shuffle_areas:
            wind_valley_exit = wind_valley.create_exit("Wind Valley - East Cave")
            wind_valley_exit.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            wind_valley_exit.randomization_type = EntranceType.TWO_WAY
            wind_valley_er_target = wind_valley.create_er_target("Wind Valley - East Cave")
            wind_valley_er_target.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            wind_valley_er_target.randomization_type = EntranceType.TWO_WAY
            self.cave_entrances.append([wind_valley_exit, wind_valley_er_target])
            gbc_main_exit = gbc_main.create_exit("GBC Cave - Free Exit")
            gbc_main_exit.randomization_group = CrystalisEntranceTypeEnum.CAVE_EXIT
            gbc_main_exit.randomization_type = EntranceType.TWO_WAY
            gbc_main_er_target = gbc_main.create_er_target("GBC Cave - Free Exit")
            gbc_main_er_target.randomization_group = CrystalisEntranceTypeEnum.CAVE_EXIT
            gbc_main_er_target.randomization_type = EntranceType.TWO_WAY
            self.cave_exits.append([gbc_main_exit, gbc_main_er_target])
            gbc_blocked_exit = gbc_blocked.create_exit("GBC Cave - Blocked Exit")
            gbc_blocked_exit.randomization_group = CrystalisEntranceTypeEnum.CAVE_EXIT
            gbc_blocked_exit.randomization_type = EntranceType.TWO_WAY
            gbc_blocked_er_target = gbc_blocked.create_er_target("GBC Cave - Blocked Exit")
            gbc_blocked_er_target.randomization_group = CrystalisEntranceTypeEnum.CAVE_EXIT
            gbc_blocked_er_target.randomization_type = EntranceType.TWO_WAY
            self.cave_exits.append([gbc_blocked_exit, gbc_blocked_er_target])
            free_region_exit = free_region.create_exit(self.shuffle_data.gbc_cave_exits[0] + " - Added Cave")
            free_region_exit.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            free_region_exit.randomization_type = EntranceType.TWO_WAY
            free_region_er_tgt = free_region.create_er_target(self.shuffle_data.gbc_cave_exits[0] + " - Added Cave")
            free_region_er_tgt.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            free_region_er_tgt.randomization_type = EntranceType.TWO_WAY
            self.cave_entrances.append([free_region_exit, free_region_er_tgt])
            blocked_region_exit = blocked_region.create_exit(self.shuffle_data.gbc_cave_exits[1] + " - Added Cave")
            blocked_region_exit.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            blocked_region_exit.randomization_type = EntranceType.TWO_WAY
            blkd_reg_er_tgt = blocked_region.create_er_target(self.shuffle_data.gbc_cave_exits[1] + " - Added Cave")
            blkd_reg_er_tgt.randomization_group = CrystalisEntranceTypeEnum.CAVE_ENTRANCE
            blkd_reg_er_tgt.randomization_type = EntranceType.TWO_WAY
            self.cave_entrances.append([blocked_region_exit, blkd_reg_er_tgt])
            self.tunnel_map["GBC Cave Entrance"] = ["GBC Cave - Free Exit", "GBC Cave - Blocked Exit"]
            self.tunnel_map["GBC Cave - Free Exit"] = ["GBC Cave Entrance", "GBC Cave - Blocked Exit"]
            self.tunnel_map["GBC Cave - Blocked Exit"] = ["GBC Cave - Free Exit", "GBC Cave Entrance"]
        else:
            wind_valley.connect(gbc_main, "Wind Valley - East Cave") #reverse connection already exists in data
            gbc_main.connect(free_region, "GBC Cave - Free Exit")
            gbc_blocked.connect(blocked_region, "GBC Cave - Blocked Exit")
            free_region.connect(gbc_main, self.shuffle_data.gbc_cave_exits[0] + " - Added Cave")
            blocked_region.connect(gbc_blocked, self.shuffle_data.gbc_cave_exits[1] + " - Added Cave")
    elif self.options.vanilla_maps == self.options.vanilla_maps.option_lime_passage:
        wind_valley = local_region_cache["Wind Valley"]
        lime_valley = local_region_cache["Lime Valley"]
        if self.options.shuffle_areas:
            wind_valley_exit = wind_valley.create_exit("Wind Valley - East")
            wind_valley_exit.randomization_group = CrystalisEntranceTypeEnum.OW_RIGHT
            wind_valley_exit.randomization_type = EntranceType.TWO_WAY
            wind_valley_er_target = wind_valley.create_er_target("Wind Valley - East")
            wind_valley_er_target.randomization_group = CrystalisEntranceTypeEnum.OW_RIGHT
            wind_valley_er_target.randomization_type = EntranceType.TWO_WAY
            lime_valley_exit = lime_valley.create_exit("Lime Valley - West")
            lime_valley_exit.randomization_group = CrystalisEntranceTypeEnum.OW_LEFT
            lime_valley_exit.randomization_type = EntranceType.TWO_WAY
            lime_valley_er_target = lime_valley.create_er_target("Lime Valley - West")
            lime_valley_er_target.randomization_group = CrystalisEntranceTypeEnum.OW_LEFT
            lime_valley_er_target.randomization_type = EntranceType.TWO_WAY
        else:
            wind_valley.connect(lime_valley, "Wind Valley - East")
            lime_valley.connect(wind_valley, "Lime Valley - West")
    # no new entrances needed for the third option
    # add shop "entrances" to Buy Healing and Buy Warp Boots "regions"
    buy_healing_region = local_region_cache["Buy Healing"]
    buy_warp_boots_region = local_region_cache["Buy Warp Boots"]
    for shop, inventory in self.shuffle_data.shop_inventories.items():
        if shop == "Shyron Item Shop":
            # Shyron shop becomes unavailable after the massacre, so don't rely on it for logic
            continue
        shop_region = local_region_cache[shop]
        if "Medical Herb" in inventory:
            shop_region.connect(buy_healing_region, "Buy Healing: " + shop)
        if "Warp Boots" in inventory:
            shop_region.connect(buy_warp_boots_region, "Buy Warp Boots: " + shop)
    # add Thunder Warp entrance
    menu_region = local_region_cache["Menu"]
    if self.shuffle_data.thunder_warp != "":
        thunder_warp_region = local_region_cache[self.shuffle_data.thunder_warp]
        menu_region.connect(thunder_warp_region, "Thunder Warp")

    # add wild warp entrances
    if self.options.vanilla_wild_warp != self.options.vanilla_wild_warp.option_out_of_logic:
        warp_names: Set[str] = set()
        for warp in self.shuffle_data.wildwarps:
            if warp == 0: continue # no need for an entrance to Mezame
            warp_name = self.wild_warp_id_to_region[warp]
            if warp_name not in warp_names:
                warp_region = local_region_cache[warp_name]
                menu_region.connect(warp_region, "Wild Warp to " + warp_name)
                #avoid making redundant entrances
                warp_names.add(warp_name)

    # make some events
    player = self.player
    tower_region = self.get_region("Tower")
    dyna_defeated_location = CrystalisLocation(player, "Dyna Defeated", None, tower_region)
    dyna_defeated_location.place_locked_item(CrystalisItem("Victory!", ItemClassification.progression,
                                                           None, player))
    tower_region.locations.append(dyna_defeated_location)
    self.multiworld.completion_condition[player] = lambda state: state.has("Victory!", player)
    buy_healing_region = self.get_region("Buy Healing")
    buy_healing_location = CrystalisLocation(player, "Buy Healing", None, buy_healing_region)
    buy_healing_location.place_locked_item(CrystalisItem("Buy Healing", ItemClassification.progression,
                                                         None, player))
    buy_healing_region.locations.append(buy_healing_location)
    buy_warp_boots_region = self.get_region("Buy Warp Boots")
    buy_warp_boots_location = CrystalisLocation(player, "Buy Warp Boots", None, buy_warp_boots_region)
    buy_warp_boots_location.place_locked_item(CrystalisItem("Buy Warp Boots", ItemClassification.progression, None,
                                                            player))
    buy_warp_boots_region.locations.append(buy_warp_boots_location)
    mesia_region = self.get_region("Mesia")
    mesia_location = CrystalisLocation(player, "Mesia", None, mesia_region)
    mesia_location.place_locked_item(CrystalisItem("Mesia's Message", ItemClassification.progression, None, player))
    mesia_region.locations.append(mesia_location)
    boat_access_location = CrystalisLocation(player, "Fisherman", None, local_region_cache["Fisherman House"])
    boat_access_location.place_locked_item(CrystalisItem("Boat Access", ItemClassification.progression, None,
                                                         player))
    fisherman_house = self.get_region("Fisherman House")
    fisherman_house.locations.append(boat_access_location)
    region_for_flute_activation: Region
    if not self.options.vanilla_dolphin:
        region_for_flute_activation = self.get_region("Menu")
    else:
        region_for_flute_activation = self.get_region("Beach House")
    activate_shell_flute_location = CrystalisLocation(player, "Activate Shell Flute", None,
                                                      region_for_flute_activation)
    activate_shell_flute_location.place_locked_item(CrystalisItem("Active Shell Flute",
                                                                ItemClassification.progression, None, player))
    region_for_flute_activation.locations.append(activate_shell_flute_location)

        # Story Mode Events
    if self.options.story_mode:
        # getting to these regions means you've beaten the boss
        kelby_1_region = self.get_region("Mt. Sabre North - Boss Arena")
        kelby_1_victory = CrystalisLocation(player, "Kelbesque 1 Defeated", None, kelby_1_region)
        kelby_1_flag = CrystalisItem("Kelbesque 1 Defeated", ItemClassification.progression, None, player)
        kelby_1_victory.place_locked_item(kelby_1_flag)
        kelby_1_region.locations.append(kelby_1_victory)
        sabera_1_region = self.get_region("Sabera's Fortress - Post-Boss")
        sabera_1_victory = CrystalisLocation(player, "Sabera 1 Defeated", None, sabera_1_region)
        sabera_1_flag = CrystalisItem("Sabera 1 Defeated", ItemClassification.progression, None, player)
        sabera_1_victory.place_locked_item(sabera_1_flag)
        sabera_1_region.locations.append(sabera_1_victory)
        mado_1_region = self.get_region("Shyron Temple - Post-Boss")
        mado_1_victory = CrystalisLocation(player, "Mado 1 Defeated", None, mado_1_region)
        mado_1_flag = CrystalisItem("Mado 1 Defeated", ItemClassification.progression, None, player)
        mado_1_victory.place_locked_item(mado_1_flag)
        mado_1_region.locations.append(mado_1_victory)
        kelby_2_region = self.get_region("Kelbesque's Floor - Boss Arena")
        kelby_2_victory = CrystalisLocation(player, "Kelbesque 2 Defeated", None, kelby_2_region)
        kelby_2_flag = CrystalisItem("Kelbesque 2 Defeated", ItemClassification.progression, None, player)
        kelby_2_victory.place_locked_item(kelby_2_flag)
        kelby_2_region.locations.append(kelby_2_victory)
        sabera_2_region = self.get_region("Sabera's Floor - Boss Arena")
        sabera_2_victory = CrystalisLocation(player, "Sabera 2 Defeated", None, sabera_2_region)
        sabera_2_flag = CrystalisItem("Sabera 2 Defeated", ItemClassification.progression, None, player)
        sabera_2_victory.place_locked_item(sabera_2_flag)
        sabera_2_region.locations.append(sabera_2_victory)
        mado_2_region = self.get_region("Mado's Floor - Boss Arena")
        mado_2_victory = CrystalisLocation(player, "Mado 2 Defeated", None, mado_2_region)
        mado_2_flag = CrystalisItem("Mado 2 Defeated", ItemClassification.progression, None, player)
        mado_2_victory.place_locked_item(mado_2_flag)
        mado_2_region.locations.append(mado_2_victory)
        karmine_region = self.get_region("Karmine's Floor - Post-Boss")
        karmine_victory = CrystalisLocation(player, "Karmine Defeated", None, karmine_region)
        karmine_flag = CrystalisItem("Karmine Defeated", ItemClassification.progression, None, player)
        karmine_victory.place_locked_item(karmine_flag)
        karmine_region.locations.append(karmine_victory)
        draygon_1_region = self.get_region("Pyramid - Post-Draygon")
        draygon_1_victory = CrystalisLocation(player, "Draygon 1 Defeated", None, draygon_1_region)
        draygon_1_flag = CrystalisItem("Draygon 1 Defeated", ItemClassification.progression, None, player)
        draygon_1_victory.place_locked_item(draygon_1_flag)
        draygon_1_region.locations.append(draygon_1_victory)

def shuffle_goa(self) -> Dict[str, str]:
    #not every Goa Transition can point to every other Goa transition, so we have this complicated algorithm
    class GoaEntranceData(NamedTuple):
        entrance_name: str
        region_name: str
        is_up: bool
        can_flip: bool

    floor_indicies: List[int] = [0, 1, 2, 3]
    self.random.shuffle(floor_indicies)

    original_entrances: List[GoaEntranceData] = [
        GoaEntranceData("Kelbesque's Floor - Entrance", "Kelbesque's Floor - Front", False, False),
        GoaEntranceData("Sabera's Floor - Entrance", "Sabera's Floor - Front", False, True),
        GoaEntranceData("Mado's Floor - Entrance", "Mado's Floor - Front", False, False),
        GoaEntranceData("Karmine's Floor - Entrance", "Karmine's Floor - Front", False, True)
    ]
    original_exits: List[GoaEntranceData] = [
        GoaEntranceData("Kelbesque's Floor - Exit", "Kelbesque's Floor - Back", True, True),
        GoaEntranceData("Sabera's Floor - Exit", "Sabera's Floor - Back", True, True),
        GoaEntranceData("Mado's Floor - Exit", "Mado's Floor - Back", True, True),
        GoaEntranceData("Karmine's Floor - Exit", "Karmine's Floor - Back", False, True)
    ]
    shuffled_entrances: List[GoaEntranceData] = []
    shuffled_exits: List[GoaEntranceData] = [GoaEntranceData("Goa Entrance - Stairs", "Goa Entrance - Behind Wall", True, False)]
    previous_exit: GoaEntranceData = shuffled_exits[0]
    for floor in floor_indicies:
        is_flexible: bool = previous_exit.is_up or original_entrances[floor].can_flip or previous_exit.can_flip
        should_flip: bool = True if not is_flexible else self.random.choice([True, False])
        current_entrance: GoaEntranceData = original_exits[floor] if should_flip else original_entrances[floor]
        shuffled_entrances.append(current_entrance)
        previous_exit = original_entrances[floor] if should_flip else original_exits[floor]
        shuffled_exits.append(previous_exit)
    shuffled_entrances.append(GoaEntranceData("Goa Exit - Upstairs", "Goa Exit", True, False))
    connection_map: Dict[str, str] = {}
    for transition_index in range(5):
        upward_entrance_name: str = shuffled_exits[transition_index].entrance_name
        downward_entrance_name: str = shuffled_entrances[transition_index].entrance_name
        upper_floor_region_name: str = shuffled_entrances[transition_index].region_name
        lower_floor_region_name: str = shuffled_exits[transition_index].region_name
        connection_map[upward_entrance_name] = upper_floor_region_name
        connection_map[downward_entrance_name] = lower_floor_region_name
    return connection_map


# this will get changed to a new multiworld step later, but for now put it here
def generate_basic(self):
    if self.options.shuffle_houses:
        # a couple of house entrances share icons with each other, so manually shuffle those to make sure the entrances
        # that share an icon lead to the same place
        for outside_exit, outside_er_target in self.shared_icon_houses:
            if outside_exit.connected_region is not None:
                # these come in pairs, so this just means we already hit the other half
                continue
            # find two matching insides to pair
            icon_type = self.random.choice(list(self.houses_by_type.keys()))
            eligible_insides = self.houses_by_type[icon_type]
            chosen_insides = self.random.sample(eligible_insides, k=2)
            # connect the first inside
            inside_exit_1, inside_er_target_1 = chosen_insides[0]
            inside_region_1 = inside_er_target_1.connected_region
            inside_region_1.entrances.remove(inside_er_target_1)
            outside_exit.connect(inside_region_1)
            outside_region = outside_er_target.connected_region
            outside_region.entrances.remove(outside_er_target)
            inside_exit_1.connect(outside_region)
            # find the paired outside
            outside_entrance_data = entrances_data[outside_exit.name]
            paired_outside_name = outside_entrance_data.related_entrance
            paired_outside_exit = self.get_entrance(paired_outside_name)
            paired_outside_region = paired_outside_exit.parent_region
            for paired_outside_er_target in paired_outside_region.entrances:
                if paired_outside_er_target.name == paired_outside_name:
                    break
            else:
                raise EntranceRandomizationError(f"Couldn't find ER target for entrance {paired_outside_name}")
            # connect the second inside
            inside_exit_2, inside_er_target_2 = chosen_insides[1]
            inside_region_2 = inside_er_target_2.connected_region
            inside_region_2.entrances.remove(inside_er_target_2)
            paired_outside_exit.connect(inside_region_2)
            paired_outside_region.entrances.remove(paired_outside_er_target)
            inside_exit_2.connect(paired_outside_region)
            # clean up houses_by_type
            if len(eligible_insides) > 3:
                eligible_insides.remove(chosen_insides[0])
                eligible_insides.remove(chosen_insides[1])
                self.houses_by_type[icon_type] = eligible_insides
            else:
                # there aren't enough houses for another pair, so remove the key
                del self.houses_by_type[icon_type]
            # add these connections to the list of pairings
            self.shuffle_data.er_pairings[outside_exit.name] = inside_exit_1.name
            self.shuffle_data.er_pairings[inside_exit_1.name] = outside_exit.name
            self.shuffle_data.er_pairings[paired_outside_exit.name] = inside_exit_2.name
            self.shuffle_data.er_pairings[inside_exit_2.name] = paired_outside_exit.name
    if self.options.shuffle_areas:
        # need to pre-emptively handle Mt. Sabre North's Prison Exit and Wind Valley's North West Cave Entrance
        # because logic gets added to the reverse of those entrances, and we want GER to account for that
        # start with Mt. Sabre North
        sabre_north_prison_exit = self.get_entrance("Mt. Sabre North - Exit")
        sabre_north_prison_region = sabre_north_prison_exit.parent_region
        for sabre_north_prison_er_target in sabre_north_prison_region.entrances:
            if sabre_north_prison_er_target.name == "Mt. Sabre North - Exit":
                break
        else:
            raise EntranceRandomizationError("Couldn't find ER target for entrance Mt. Sabre North - Exit")
        # pick a random cave entrance
        cave_outside_exit, cave_outside_er_target = self.random.choice(self.cave_entrances)
        cave_outside_region = cave_outside_exit.parent_region
        # connect the regions
        sabre_north_prison_region.entrances.remove(sabre_north_prison_er_target)
        sabre_north_prison_exit.connect(cave_outside_region)
        cave_outside_region.entrances.remove(cave_outside_er_target)
        cave_outside_exit.connect(sabre_north_prison_region)
        # add to ER pairings
        self.shuffle_data.er_pairings["Mt. Sabre North - Exit"] = cave_outside_exit.name
        self.shuffle_data.er_pairings[cave_outside_exit.name] = "Mt. Sabre North - Exit"
        # see if we need to add logic
        if cave_outside_exit.name in GBC_CAVE_NAMES or entrances_data[cave_outside_exit.name].can_lock:
            # add logic for Key to Prison
            set_rule(cave_outside_exit, lambda state: state.has(self.shuffle_data.key_item_names["Key to Prison"],
                                                                self.player))
        # clean up cave entrances/exits
        self.cave_entrances.remove([cave_outside_exit, cave_outside_er_target])
        self.cave_exits.remove([sabre_north_prison_exit, sabre_north_prison_er_target])
        # now do Wind Valley
        windmill_locked_cave_exit = self.get_entrance("Wind Valley - North West Cave")
        windmill_locked_cave_reverse_name: str
        wind_valley_region = windmill_locked_cave_exit.parent_region
        # first make sure we didn't just connect it to Sabre North
        if windmill_locked_cave_exit.connected_region is None:
            for windmill_locked_cave_er_target in wind_valley_region.entrances:
                if windmill_locked_cave_er_target.name == "Wind Valley - North West Cave":
                    break
            else:
                raise EntranceRandomizationError("Couldn't find ER target for entrance Wind Valley - North West Cave")
            # remove this from the list of cave entrances so we don't get tripped up later
            self.cave_entrances.remove([windmill_locked_cave_exit, windmill_locked_cave_er_target])
            if not self.options.shuffle_houses:
                # also remove the windmill exterior as a place to connect to, to prevent broken geometry
                windmill_exterior_cave_exit = self.get_entrance("Windmill Exterior - Windmill Cave")
                if windmill_exterior_cave_exit.connected_region is None:
                    windmill_exterior_region = windmill_exterior_cave_exit.parent_region
                    for windmill_exterior_er_target in windmill_exterior_region.entrances:
                        if windmill_exterior_er_target.name == "Windmill Exterior - Windmill Cave":
                            break
                    else:
                        raise EntranceRandomizationError("Couldn't find ER target for entrance Windmill Exterior - "
                                                         "Windmill Cave")
                    self.cave_entrances.remove([windmill_exterior_cave_exit, windmill_exterior_er_target])
            # pick a random cave exit to connect it to
            cave_inside_exit, cave_inside_er_target = self.random.choice(self.cave_exits)
            cave_inside_region = cave_inside_exit.parent_region
            # connect the regions
            wind_valley_region.entrances.remove(windmill_locked_cave_er_target)
            windmill_locked_cave_exit.connect(cave_inside_region)
            cave_inside_region.entrances.remove(cave_inside_er_target)
            cave_inside_exit.connect(wind_valley_region)
            # add to ER pairings
            self.shuffle_data.er_pairings["Wind Valley - North West Cave"] = cave_inside_exit.name
            self.shuffle_data.er_pairings[cave_inside_exit.name] = "Wind Valley - North West Cave"
            windmill_locked_cave_reverse_name = cave_inside_exit.name
        else:
            for reverse_entrance in windmill_locked_cave_exit.connected_region.exits:
                if reverse_entrance.connected_region == wind_valley_region:
                    break
            else:
                raise EntranceRandomizationError("Couldn't find reverse entrance for Wind Valley - North West Cave in"
                                                 f" region {windmill_locked_cave_exit.connected_region.name}")
            windmill_locked_cave_reverse_name = reverse_entrance.name
        # now the complicated stuff: check to see if this is a tunnel
        if windmill_locked_cave_reverse_name in self.tunnel_map:
            # connect and lock the other ends of the tunnel if appropriate
            for opposite_tunnel_exit_name in self.tunnel_map[windmill_locked_cave_reverse_name]:
                opposite_tunnel_exit = self.get_entrance(opposite_tunnel_exit_name)
                opposite_tunnel_region = opposite_tunnel_exit.parent_region
                entrance_to_lock = None
                if opposite_tunnel_exit.connected_region is None:
                    # find the ER target
                    for opposite_tunnel_er_target in opposite_tunnel_region.entrances:
                        if opposite_tunnel_er_target.name == opposite_tunnel_exit.name:
                            break
                    else:
                        raise EntranceRandomizationError(f"Couldn't find ER target for entrance "
                                                         f"{opposite_tunnel_exit.name}")
                    # find a random cave entrance to connect this to
                    opposite_outside_exit, opposite_outside_er_target = self.random.choice(self.cave_entrances)
                    opposite_outside_region = opposite_outside_exit.parent_region
                    # connect the regions
                    opposite_tunnel_region.entrances.remove(opposite_tunnel_er_target)
                    opposite_tunnel_exit.connect(opposite_outside_region)
                    opposite_outside_region.entrances.remove(opposite_outside_er_target)
                    opposite_outside_exit.connect(opposite_tunnel_region)
                    # add to ER pairings
                    self.shuffle_data.er_pairings[opposite_outside_exit.name] = opposite_tunnel_exit.name
                    self.shuffle_data.er_pairings[opposite_tunnel_exit.name] = opposite_outside_exit.name
                    # clean up cave entrances
                    self.cave_entrances.remove([opposite_outside_exit, opposite_outside_er_target])
                    # track the entrance to lock
                    entrance_to_lock = opposite_outside_exit
                else:
                    # the other end of this tunnel is already connected, so just find the entrance to lock
                    for entrance_to_lock in opposite_tunnel_exit.connected_region.exits:
                        if entrance_to_lock.connected_region == opposite_tunnel_region:
                            break
                    else:
                        raise EntranceRandomizationError("Couldn't find reverse entrance for "
                                                         f"{opposite_tunnel_exit.name} in region "
                                                         f"{opposite_tunnel_exit.connected_region.name}")
                # check to see if the entrance can be locked
                if entrance_to_lock.name in GBC_CAVE_NAMES or entrances_data[entrance_to_lock.name].can_lock:
                    # lock it up
                    windmill_reg = self.get_region("Windmill")
                    set_rule(entrance_to_lock, lambda state: state.has(self.shuffle_data.key_item_names["Windmill Key"],
                                                                       self.player) and windmill_reg.can_reach(state))
                    self.multiworld.register_indirect_condition(windmill_reg, entrance_to_lock)
    # now that all the prep is done, let GER handle the rest
    if self.options.shuffle_areas or self.options.shuffle_houses:
        er_state = randomize_entrances(self, True, SHUFFLE_GROUPING)
        self.shuffle_data.er_pairings |= er_state.pairings
        # if self.player == 1:
        #     from Utils import visualize_regions
        #     visualize_regions(self.multiworld.get_region("Menu", self.player), f"World {self.player}.puml",
        #                       show_entrance_names=False, show_other_regions=True)
        #     logging.info(self.shuffle_data.er_pairings)
