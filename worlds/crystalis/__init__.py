import logging
from typing import Dict, List, Mapping, Any, ClassVar
from dataclasses import asdict

import settings
from BaseClasses import Item, Tutorial
from .items import CrystalisItem, items_data, unidentify_items
from .locations import CrystalisLocation, create_location_from_location_data
from .regions import regions_data, create_regions
from .options import CrystalisOptions, crystalis_option_groups
from .types import *
from .logic import set_rules
from .output import generate_output
from .client import CrystalisClient  # Unused, but required to register with BizHawkClient
from worlds.AutoWorld import World, WebWorld


class CrystalisWeb(WebWorld):
    game = "Crystalis"
    option_groups = crystalis_option_groups

    tutorials = [

        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Crystalis Randomizer in Archipelago.",
            "English",
            "setup_en.md",
            "setup/en",
            ["CodeGorilla"]
        )
    ]
    #TODO: Add better tutorial


class CrystalisSettings(settings.Group):
    pass
    # TODO: I don't think any settings will be needed here, but confirm


class CrystalisWorld(World):
    """
    TODO: Add Crystalis doc string.
    """


    game = "Crystalis"
    options_dataclass = CrystalisOptions
    options: CrystalisOptions
    settings: ClassVar[CrystalisSettings]
    topology_present = True
    shuffle_data: CrystalisShuffleData
    set_rules = set_rules
    create_regions = create_regions
    generate_output = generate_output
    unidentify_items = unidentify_items
    web = CrystalisWeb()

    #this will get filled out later, while creating regions
    locations_data: List[CrystalisLocationData] = []
    location_name_to_id = {}
    wild_warp_id_to_region: Dict[int, str] = {}
    for region_data in regions_data.values():
        for location_data in region_data.locations:
            location_name_to_id[location_data.name] = location_data.ap_id_offset + CRYSTALIS_BASE_ID
        if not region_data.ban_wildwarp:
            for id in region_data.wildwarpIds:
                wild_warp_id_to_region[id] = region_data.name
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
        wall_names: List[str] = ["Zebu Cave", "East Cave", "Sealed Cave", "Mt Sabre West", "Mt Sabre North",
                                 "Waterfall Cave", "Fog Lamp Cave", "Kirisa Plant Cave", "Evil Spirit Island",
                                 "Mt Hydra", "Goa Fortress - Entrance", "Goa Fortress Basement",
                                 "Goa Fortress - Sabera Item", "Goa Fortress - Sabera Boss", "Goa Fortress - Mado 2",
                                 "Goa Fortress - Karmine 5"]
        elements = ["Wind", "Fire", "Water", "Thunder"]
        wall_weaknesses: List[str]
        if self.options.randomize_wall_elements:
            wall_weaknesses = [self.random.choice(elements) for i in range(len(wall_names))]
        else:
            wall_weaknesses = ["Wind", "Wind", "Wind", "Fire", "Fire", "Fire", "Wind", "Wind", "Wind", "Wind",
                               "Thunder", "Thunder", "Thunder", "Thunder", "Thunder", "Thunder"]
        wall_map: Dict[str, str] = dict(zip(wall_names, wall_weaknesses))
        #then key item names
        key_item_names: Dict[str, str] = unidentify_items(self)
        #then trade-ins
        trade_in_targets = ["Akahana", "Aryllis", "Fisherman", "Kensu", "Slimed Kensu"]
        trade_in_items = [key_item_names["Statue of Onyx"], "Kirisa Plant", key_item_names["Fog Lamp"],
                          "Love Pendant", key_item_names["Ivory Statue"]]
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
            towns = ["Leaf", "Brynmaer", "Oak", "Nadare's", "Portoa", "Amazones", "Joel", "Zombie Town", "Swan",
                     "Shyron", "Goa", "Sahara"]
            thunder_warp = self.random.choice(towns)
        shop_inventories = {
            "Leaf Item Shop":     ["Medical Herb", "Antidote", "Warp Boots"],
            "Brynmaer Item Shop": ["Medical Herb", "Antidote", "Warp Boots"],
            "Oak Item Shop":      ["Medical Herb", "Antidote", "Fruit of Power"],
            "Nadare's Item Shop": ["Medical Herb", "Antidote", "Fruit of Power", "Warp Boots"],
            "Amazones Item Shop": ["Warp Boots", "Lysis Plant", "Fruit of Power"],
            "Portoa Item Shop":   ["Medical Herb", "Warp Boots", "Lysis Plant", "Fruit of Lime"],
            "Joel Item Shop":     ["Medical Herb", "Antidote", "Fruit of Power"],
            "Swan Item Shop":     ["Medical Herb", "Antidote", "Fruit of Power", "Warp Boots"],
            "Goa Item Shop":      ["Medical Herb", "Antidote", "Lysis Plant", "Warp Boots"],
            "Shyron Item Shop":   ["Medical Herb", "Antidote", "Fruit of Lime", "Magic Ring"],
            "Sahara Item Shop":   ["Antidote", "Magic Ring", "Fruit of Repun", "Warp Boots"]
        }
        if not self.options.vanilla_shops:
            shop_inventories = self.randomize_shop_inventories(shop_inventories)
        self.shuffle_data = CrystalisShuffleData(wall_map, key_item_names, trade_in_map, boss_reqs, gbc_cave_exits,
                                                 thunder_warp, shop_inventories)


    def create_items(self) -> None:
        #TODO: proper item fill based on settings
        for item_data in items_data.values():
            if item_data.name in self.shuffle_data.key_item_names.keys():
                self.multiworld.itempool.append(self.create_item(self.shuffle_data.key_item_names[item_data.name]))
            else:
                for i in range(item_data.default_count):
                    self.multiworld.itempool.append(self.create_item(item_data.name))
        if not self.options.vanilla_dolphin:
            #Kensu at the beach house is now a check so add an item to the pool
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
        if self.options.vanilla_maps == self.options.vanilla_maps.option_GBC_cave:
            #GBC Cave has two locations in it
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
            self.multiworld.itempool.append(self.create_item("Mimic"))
        if self.options.shuffle_areas or self.options.shuffle_houses:
            #These settings add two locations to Mezame shrine
            self.multiworld.itempool.append(self.create_item("Medical Herb"))
            self.multiworld.itempool.append(self.create_item("Medical Herb"))


    def get_filler_item_name(self) -> str:
        return "Medical Herb"


    def fill_slot_data(self) -> Mapping[str, Any]:
        #get logic relevant options for tracker purposes
        slot_data: Dict[str, Any] = self.options.as_dict("randomize_maps", "shuffle_areas", "shuffle_houses",
                                                         "randomize_tradeins", "unidentified_key_items", "shuffle_goa",
                                                         "randomize_wild_warp", "story_mode", "no_bow_mode",
                                                         "orbs_not_required", "thunder_warp", "vanilla_dolphin",
                                                         "fake_flight", "statue_glitch", "mt_sabre_skip",
                                                         "statue_gauntlet_skip", "sword_charge_glitch", "trigger_skip",
                                                         "rage_skip", "randomize_monster_weaknesses", "oops_all_mimics",
                                                         "dont_shuffle_mimics",
                                                         "keep_unique_items_and_consumables_separate",
                                                         "guarantee_refresh", "battle_magic_not_guaranteed",
                                                         "tink_mode", "barrier_not_guaranteed",
                                                         "gas_mask_not_guaranteed", "charge_shots_only",
                                                         "dont_buff_bonus_items", "vanilla_maps", "vanilla_wild_warp")
        #get shuffle data for tracker purposes, UT regen, and ids for unidentified items
        slot_data["shuffle_data"] = asdict(self.shuffle_data)
        return slot_data
