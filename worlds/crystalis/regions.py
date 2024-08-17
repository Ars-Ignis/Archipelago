

from BaseClasses import Region, ItemClassification
from .types import CrystalisRegionData, CrystalisLocationData, CrystalisEntranceData, CrystalisEntranceTypeEnum
from .locations import CrystalisLocation, create_location_from_location_data
from .items import CrystalisItem
import orjson
from typing import Dict, List, Set, NamedTuple
import pkgutil


def load_region_data_from_json() -> Dict[str, CrystalisRegionData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/regions.json").decode("utf-8-sig"))


regions_data_json = load_region_data_from_json()
regions_data: Dict[str, CrystalisRegionData] = {}
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
        new_ent = CrystalisEntranceData(entrance_data["name"], entrance_data["entrance_type"],
                                        entrance_data["vanilla_target"])
        new_entrance_data.append(new_ent)
    regions_data[key] = CrystalisRegionData(value["name"], value["wildwarpIds"], new_entrance_data,
                                            region_locations_data, value["ban_wildwarp"])


    def create_regions(self) -> None:
        #first make regions and locations
        #need to cache while still creating regions before appending them to the multiworld
        local_region_cache = {}
        for region_data in regions_data.values():
            if self.options.vanilla_maps != self.options.vanilla_maps.option_GBC_cave and \
                "GBC" in region_data.name:
                #don't add GBC cave regions, locations, and entrances
                continue
            region = Region(region_data.name, self.player, self.multiworld)
            local_region_cache[region_data.name] = region
            for location_data in region_data.locations:
                if not self.options.shuffle_areas and not self.options.shuffle_houses and \
                        "Mezame" in location_data.name:
                    #Mezame Shrine chests only exist if areas or houses are shuffled, to grow sphere 1
                    continue
                if self.options.vanilla_dolphin and "Kensu In Cabin" in location_data.name:
                    #Kensu in Cabin just activates the flute if vanilla dolphin is on
                    continue
                #now that we know the location exists, add it to the multiworld
                self.locations_data.append(location_data)
                region.locations.append(create_location_from_location_data(self.player, location_data, region))
        #then make entrances
        for region_data in regions_data.values():
            if region_data.name in local_region_cache.keys():
                region = local_region_cache[region_data.name]
                for entrance_data in region_data.entrances:
                    if entrance_data.vanilla_target in local_region_cache:
                        if entrance_data.entrance_type == CrystalisEntranceTypeEnum.STATIC:
                            connecting_region = local_region_cache[entrance_data.vanilla_target]
                            region.connect(connecting_region)
                        elif entrance_data.entrance_type == CrystalisEntranceTypeEnum.GOA_TRANSITION and \
                             self.options.shuffle_goa:
                            #connect according to the shuffle
                            connecting_region_name = self.shuffle_data.goa_connection_map[entrance_data.name]
                            connecting_region = local_region_cache[connecting_region_name]
                            region.connect(connecting_region, entrance_data.name)
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
            wind_valley.connect(gbc_main, "Wind Valley - East Cave") #reverse connection already exists in data
            gbc_main.connect(free_region, "GBC Cave - Free Exit")
            gbc_blocked.connect(blocked_region, "GBC Cave - Blocked Exit")
            free_region.connect(gbc_main, self.shuffle_data.gbc_cave_exits[0] + " - Added Cave")
            blocked_region.connect(gbc_blocked, self.shuffle_data.gbc_cave_exits[1] + " - Added Cave")
        elif self.options.vanilla_maps == self.options.vanilla_maps.option_lime_passage:
            wind_valley = local_region_cache["Wind Valley"]
            lime_valley = local_region_cache["Lime Valley"]
            wind_valley.connect(lime_valley, "Wind Valley - East")
            lime_valley.connect(wind_valley, "Lime Valley - West")
        #no new entrances needed for the third option
        #add shop "entrances" to Buy Healing and Buy Warp Boots "regions"
        buy_healing_region = local_region_cache["Buy Healing"]
        buy_warp_boots_region = local_region_cache["Buy Warp Boots"]
        for shop, inventory in self.shuffle_data.shop_inventories.items():
            if shop == "Shyron Item Shop":
                #Shyron shop becomes unavailable after the massacre, so don't rely on it for logic
                continue
            shop_region = local_region_cache[shop]
            if "Medical Herb" in inventory:
                shop_region.connect(buy_healing_region, "Buy Healing: " + shop)
            if "Warp Boots" in inventory:
                shop_region.connect(buy_warp_boots_region, "Buy Warp Boots: " + shop)
        #add Thunder Warp entrance
        menu_region = local_region_cache["Menu"]
        if self.shuffle_data.thunder_warp != "":
            thunder_warp_region = local_region_cache[self.shuffle_data.thunder_warp]
            menu_region.connect(thunder_warp_region, "Thunder Warp")

        #add wild warp entrances
        warp_names: Set[str] = set()
        for warp in self.shuffle_data.wildwarps:
            if warp == 0: continue #no need for an entrance to Mezame
            warp_name = self.wild_warp_id_to_region[warp]
            if warp_name not in warp_names:
                warp_region = local_region_cache[warp_name]
                menu_region.connect(warp_region, "Wild Warp to " + warp_name)
                #avoid making redundant entrances
                warp_names.add(warp_name)

        #make some events
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

            #Story Mode Events
        if self.options.story_mode:
            #getting to these regions means you've beaten the boss
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

        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", player), "my_world.puml")

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
