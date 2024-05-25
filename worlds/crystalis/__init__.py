import typing

import settings
from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification
from typing import Dict, List
from .items import CrystalisItem, items_data
from .locations import CrystalisLocation, aggregate_location_data_from_regions, \
                        create_location_from_location_data
from .regions import regions_data
from .options import CrystalisOptions
from .types import *
#from .logic import set_rules
from worlds.AutoWorld import World, WebWorld


class CrystalisWeb(WebWorld):
    pass
    # TODO: add tutorial


class CrystalisSettings(settings.Group):
    pass
    # TODO: I don't think any settings will be needed here, but confirm


class CrystalisWorld(World):
    """
    TODO: Add Crystalis doc string.
    """


    game: str = "Crystalis"
    options_dataclass = CrystalisOptions
    options: CrystalisOptions
    settings: typing.ClassVar[CrystalisSettings]
    topology_present = True
    shuffle_data: CrystalisShuffleData

    locations_data: List[CrystalisLocationData] = aggregate_location_data_from_regions(regions_data)
    location_name_to_id = {}
    wild_warp_id_to_region: Dict[int, str] = {}
    for region_data in regions_data.values():
        new_locations_data: List[CrystalisLocationData] = []
        for location_data in region_data.locations:
            new_locations_data.append(CrystalisLocationData(**location_data))
        region_data.locations = new_locations_data
        new_entrance_data: List[CrystalisEntranceData] = []
        for entrance_data in region_data.entrances:
            new_entrance_data.append(CrystalisEntranceData(**entrance_data))
        region_data.entrances = new_entrance_data
        for id in region_data.wildwarpIds:
            wild_warp_id_to_region[id] = region_data.name
    for location in locations_data:
        location_name_to_id[location.name] = location.ap_id_offset + CRYSTALIS_BASE_ID
    item_name_to_id = {}
    item_name_groups = {}
    for item in items_data.values():
        item_name_to_id[item.name] = item.ap_id_offset + CRYSTALIS_BASE_ID
        for group in item.groups:
            if group in item_name_groups.keys():
                item_name_groups[group].add(item.name)
            else:
                item_name_groups[group] = {item.name}


    def create_item(self, name: str) -> "Item":
        item_data: CrystalisItemData = items_data[name]
        return CrystalisItem(name, convert_enum_to_item_classification(item_data.category), item_data.ap_id_offset + CRYSTALIS_BASE_ID, self.player)


    def generate_early(self) -> None:
        #walls first
        wall_names: List[str] = ["Zebu's Cave", "GBC Cave", "Sealed Cave", "Mt. Sabre West", "Mt. Sabre North",
                                 "Waterfall Cave", "Fog Lamp Cave", "Kirisa Plant Cave", "Evil Spirit Island",
                                 "Mt. Hydra", "Goa Entrance", "Power Ring Basement", "Sabera Item", "Sabera Boss",
                                 "Mado", "Karmine"]
        elements = ["Wind", "Fire", "Water", "Thunder"]
        wall_weaknesses: List[str]
        if self.options.randomize_wall_elements:
            wall_weaknesses = [self.random.choice(elements) for i in range(len(wall_names))]
        else:
            wall_weaknesses = ["Wind", "Wind", "Wind", "Fire", "Fire", "Fire", "Wind", "Wind", "Wind", "Wind",
                               "Thunder", "Thunder", "Thunder", "Thunder", "Thunder", "Thunder"]
        wall_map: Dict[str, List[str]] = dict(zip(wall_names, wall_weaknesses))
        #then key item names
        #TODO randomize these based on settings
        key_item_names: Dict[str, str] = {}
        for item in items_data.values():
            if "Key Item" in item.groups:
                key_item_names[item.name] = item.name
        #then trade-ins
        trade_in_targets = ["Akahana", "Aryllis", "Fisherman", "Tag Kensu", "Slime Kensu"]
        trade_in_items = [key_item_names["Statue of Onyx"], key_item_names["Kirisa Plant"], key_item_names["Fog Lamp"],
                          key_item_names["Love Pendant"], key_item_names["Ivory Statue"]]
        if self.options.randomize_tradeins:
            self.random.shuffle(trade_in_items)
        trade_in_map: Dict[str, str] = dict(zip(trade_in_targets, trade_in_items))
        if self.options.randomize_tradeins:
            trade_in_map["Tornel"] = self.random.choice(elements)
            trade_in_map["Rage"] = self.random.choice(elements)
        else:
            trade_in_map["Tornel"] = "Wind"
            trade_in_map["Rage"] = "Water"
        #bosses!
        boss_names: List[str] = ["Giant Insect", "Vampire 2", "Kelbesque 1", "Sabera 1", "Mado 1", "Kelbesque 2",
                                 "Sabera 2", "Mado 2", "Karmine"]
        boss_weaknesses: List[str]
        if self.options.randomize_monster_weaknesses:
            boss_weaknesses = [self.random.choice(elements) for i in range(len(boss_names))]
        else:
            boss_weaknesses = ["Wind", "Fire", "Wind", "Fire", "Water", "Wind", "Fire", "Water", "Thunder"]
        boss_reqs: Dict[str, str] = dict(zip(boss_names, boss_weaknesses))
        self.shuffle_data = CrystalisShuffleData(wall_map, key_item_names, trade_in_map, boss_reqs)


    def create_regions(self) -> None:
        #first make regions and locations
        local_region_cache = {}
        for region_data in regions_data.values():
            region = Region(region_data.name, self.player, self.multiworld)
            local_region_cache[region_data.name] = region
            for location_data in region_data.locations:
                if not self.options.shuffle_areas and not self.options.shuffle_houses and \
                        "Mezame Shrine" in location_data.name:
                    #Mezame Shrine chests only exist if areas or houses are shuffled, to grow sphere 1
                    continue
                region.locations.append(create_location_from_location_data(self.player, location_data, region))
        #then make entrances
        for region_data in regions_data.values():
            region = local_region_cache[region_data.name]
            for entrance_data in region_data.entrances:
                if entrance_data.vanilla_target in local_region_cache:
                    connecting_region = local_region_cache[entrance_data.vanilla_target]
                    if entrance_data.entrance_type == CrystalisEntranceTypeEnum.STATIC:
                        region.connect(connecting_region)
                    else:
                        region.connect(connecting_region, entrance_data.name)
            self.multiworld.regions.append(region)
        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")


    def create_items(self) -> None:
        #TODO: proper item fill based on settings
        for item_data in items_data.values():
            for i in range(item_data.default_count):
                self.multiworld.itempool.append(self.create_item(item_data.name))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
