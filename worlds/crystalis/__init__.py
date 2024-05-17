import typing

import settings
from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification
from typing import Dict, List
from .Items import CrystalisItem, items_data
from .Locations import CrystalisLocation, aggregate_location_data_from_regions, \
                        create_location_from_location_data
from .Regions import regions_data
from .Options import CrystalisOptions
from .CrystalisTypes import *
#from .Rules import set_rules, set_completion_rules
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


    def create_regions(self) -> None:
        #first make regions and locations
        local_region_cache = {}
        for region_data in regions_data.values():
            region = Region(region_data.name, self.player, self.multiworld)
            local_region_cache[region_data.name] = region
            for location_data in region_data.locations:
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
        for item_data in items_data.values():
            for i in range(item_data.default_count):
                self.multiworld.itempool.append(self.create_item(item_data.name))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
        self.multiworld.itempool.append(self.create_item("Medical Herb"))
