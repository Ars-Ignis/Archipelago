import logging
import typing

import settings
from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification
from typing import Dict, List
from .items import CrystalisItem, items_data
from .locations import CrystalisLocation, create_location_from_location_data
from .regions import regions_data
from .options import CrystalisOptions
from .types import *
from .logic import set_rules
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
    set_rules = set_rules

    locations_data: List[CrystalisLocationData] = []
    location_name_to_id = {}
    wild_warp_id_to_region: Dict[int, str] = {}
    for region_data in regions_data.values():
        region_locations_data: List[CrystalisLocationData] = []
        for location_data in region_data.locations:
            new_loc = CrystalisLocationData(location_data["name"], location_data["rom_id"], \
                                            location_data["ap_id_offset"], location_data["unique"], \
                                            location_data["lossy"], location_data["prevent_loss"], \
                                            location_data["is_chest"])
            region_locations_data.append(new_loc)
            locations_data.append(new_loc)
        region_data.locations = region_locations_data
        new_entrance_data: List[CrystalisEntranceData] = []
        for entrance_data in region_data.entrances:
            new_ent = CrystalisEntranceData(entrance_data["name"], entrance_data["entrance_type"], \
                                            entrance_data["vanilla_target"])
            new_entrance_data.append(new_ent)
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


    def randomize_shop_inventories(self, starting_inventories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        total_inventory: Dict[str, int] = {}
        shuffled_shops: Dict[str, List[str]] = {}
        unfilled_shops: List[str] = list(starting_inventories.keys())
        self.random.shuffle(unfilled_shops)
        for shop, inventory in starting_inventories.items():
            shuffled_shops[shop] = []
            for stock in inventory:
                if stock in total_inventory.keys():
                    total_inventory[stock] = total_inventory[stock] + 1
                else:
                    total_inventory[stock] = 1
        print(f"Total Inventory: {total_inventory}")
        #while we have inventory to put into shops
        while len(total_inventory) > 0 and len(unfilled_shops) > 0:
            filled_a_shop: bool = False
            #go through the list of items
            out_of_stock: List[str] = []
            for stock, count in total_inventory.items():
                #if there are as many copies (or more) of this item as there are shops remaining
                if count >= len(unfilled_shops):
                    if count > len(unfilled_shops):
                        logging.warning(f"Not enough unfilled shops to place {stock}, placing {len(unfilled_shops)}")
                    #we need to add one to every remaining shop
                    filled_shops: List[str] = []
                    for shop_to_fill in unfilled_shops:
                        shuffled_shops[shop_to_fill].append(stock)
                        #check to see if the shop is now full
                        if len(shuffled_shops[shop_to_fill]) == 4:
                            filled_shops.append(shop_to_fill)
                    filled_a_shop = True
                    for full_shop in filled_shops:
                        unfilled_shops.remove(full_shop)
                    out_of_stock.append(stock)
            for stock in out_of_stock:
                total_inventory.pop(stock)
            if filled_a_shop:
                #go back to the top of the while loop in case more items need to be forced
                continue
            #if we made it here, pick a specific shop to fill with random unique stock
            shop_to_fill: str = unfilled_shops.pop()
            existing_inventory: List[str] = shuffled_shops[shop_to_fill]
            fill_count: int = min(len(total_inventory), 4-len(existing_inventory))
            new_inventory: List[str] = self.random.sample(list(total_inventory.keys()), k=fill_count)
            for stock in new_inventory:
                total_inventory[stock] = total_inventory[stock] - 1
                if total_inventory[stock] == 0:
                    total_inventory.pop(stock)
            shuffled_shops[shop_to_fill] = existing_inventory + new_inventory
        if len(total_inventory) > 0:
            #if we somehow didn't place every item, log a warning
            logging.warning("Filled all shops without placing all stock!")
            logging.warning(f"Shop inventories: {str(shuffled_shops)}")
        return shuffled_shops

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
            trade_in_map["Rage"] = "Sword of " + self.random.choice(elements)
        else:
            trade_in_map["Tornel"] = "Wind"
            trade_in_map["Rage"] = "Sword of Water"
        #bosses!
        boss_names: List[str] = ["Giant Insect", "Vampire 2", "Kelbesque 1", "Sabera 1", "Mado 1", "Kelbesque 2",
                                 "Sabera 2", "Mado 2", "Karmine"]
        boss_weaknesses: List[str]
        if self.options.randomize_monster_weaknesses:
            boss_weaknesses = [self.random.choice(elements) for i in range(len(boss_names))]
        else:
            boss_weaknesses = ["Wind", "Fire", "Wind", "Fire", "Water", "Wind", "Fire", "Water", "Thunder"]
        boss_reqs: Dict[str, str] = dict(zip(boss_names, boss_weaknesses))
        gbc_cave_exits: List[str] = []
        if self.options.vanilla_maps == self.options.vanilla_maps.option_GBC_cave:
            possible_gbc_cave_exits = ["Cordel Plains - Main", "Lime Valley", "Goa Valley", "Desert 2"]
            gbc_cave_exits = self.random.sample(possible_gbc_cave_exits, k=2)
        thunder_warp: Optional[str] = None
        if self.options.thunder_warp == self.options.thunder_warp.option_vanilla:
            thunder_warp = "Shyron"
        elif self.options.thunder_warp == self.options.thunder_warp.option_shuffled:
            towns = ["Leaf", "Brynmaer", "Oak", "Nadare's", "Portoa", "Amazones", "Joel", "Zombie Town", "Swan", \
                     "Shyron", "Goa", "Sahara"]
            thunder_warp = self.random.choice(towns)
        shop_inventories = {}
        shop_inventories["Leaf Item Shop"] = ["Medical Herb", "Antidote", "Warp Boots"]
        shop_inventories["Brynmaer Item Shop"] = ["Medical Herb", "Antidote", "Warp Boots"]
        shop_inventories["Oak Item Shop"] = ["Medical Herb", "Antidote", "Fruit of Power"]
        shop_inventories["Nadare's Item Shop"] = ["Medical Herb", "Antidote", "Fruit of Power", "Warp Boots"]
        shop_inventories["Amazones Item Shop"] = ["Warp Boots", "Lysis Plant", "Fruit of Power"]
        shop_inventories["Portoa Item Shop"] = ["Medical Herb", "Warp Boots", "Lysis Plant", "Fruit of Lime"]
        shop_inventories["Joel Item Shop"] = ["Medical Herb", "Antidote", "Fruit of Power"]
        shop_inventories["Swan Item Shop"] = ["Medical Herb", "Antidote", "Fruit of Power", "Warp Boots"]
        shop_inventories["Goa Item Shop"] = ["Medical Herb", "Antidote", "Lysis Plant", "Warp Boots"]
        shop_inventories["Shyron Item Shop"] = ["Medical Herb", "Antidote", "Fruit of Lime", "Magic Ring"]
        shop_inventories["Sahara Item Shop"] = ["Antidote", "Magic Ring", "Fruit of Repun", "Warp Boots"]
        if not self.options.vanilla_shops:
            shop_inventories = self.randomize_shop_inventories(shop_inventories)
        self.shuffle_data = CrystalisShuffleData(wall_map, key_item_names, trade_in_map, boss_reqs, gbc_cave_exits, \
                                                 thunder_warp, shop_inventories)



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
                    #TODO: Make an event here for activating the flute
                    continue
                region.locations.append(create_location_from_location_data(self.player, location_data, region))
        #then make entrances
        for region_data in regions_data.values():
            if region_data.name in local_region_cache.keys():
                region = local_region_cache[region_data.name]
                for entrance_data in region_data.entrances:
                    if entrance_data.vanilla_target in local_region_cache:
                        connecting_region = local_region_cache[entrance_data.vanilla_target]
                        if entrance_data.entrance_type == CrystalisEntranceTypeEnum.STATIC:
                            region.connect(connecting_region)
                        else:
                            region.connect(connecting_region, entrance_data.name)
                self.multiworld.regions.append(region)
        #add conditional entrances
        if self.options.no_bow_mode:
            #tower shortcut for Rb
            #technically the normal path to Tower should be removed, but it should be redundant in all cases
            #famous last words lmao
            mezame_shrine = local_region_cache["Mezame Shrine"]
            tower = local_region_cache["Tower"]
            mezame_shrine.connect(tower, "Tower Shortcut")
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
        if self.shuffle_data.thunder_warp is not None:
            menu_region = local_region_cache["Menu"]
            thunder_warp_region = local_region_cache[self.shuffle_data.thunder_warp]
            menu_region.connect(thunder_warp_region, "Thunder Warp")
        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")


    def create_items(self) -> None:
        #TODO: proper item fill based on settings
        for item_data in items_data.values():
            for i in range(item_data.default_count):
                self.multiworld.itempool.append(self.create_item(item_data.name))
        if not self.options.vanilla_dolphin:
            #Kensu at the beach house is now a check so add an item to the pool
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
        if self.options.vanilla_maps == self.options.vanilla_maps.option_GBC_cave:
            #GBC Cave has two locations in it
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
            self.multiworld.itempool.append(self.create_item("Mimic"))
        if self.options.shuffle_areas or self.options.shuffle_areas:
            #These settings add two locations to Mezame shrine
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
            self.multiworld.itempool.append(self.create_item("Medical Herb"))


