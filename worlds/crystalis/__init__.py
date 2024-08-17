import logging
from typing import Dict, List, Mapping, Any, ClassVar
from dataclasses import asdict

import settings
from BaseClasses import Item, Tutorial
from .items import CrystalisItem, items_data, unidentify_items, create_item, create_items
from .locations import CrystalisLocation, create_location_from_location_data
from .regions import regions_data, create_regions, shuffle_goa
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


#class CrystalisSettings(settings.Group):
    #pass
    # TODO: I don't think any settings will be needed here, but confirm


class CrystalisWorld(World):
    """
    TODO: Add Crystalis doc string.
    """


    game = "Crystalis"
    options_dataclass = CrystalisOptions
    options: CrystalisOptions
    #settings: ClassVar[CrystalisSettings]
    topology_present = True
    shuffle_data: CrystalisShuffleData
    set_rules = set_rules
    create_regions = create_regions
    generate_output = generate_output
    unidentify_items = unidentify_items
    shuffle_goa = shuffle_goa
    create_item = create_item
    create_items = create_items
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

        if hasattr(self.multiworld, "re_gen_passthrough"):
            if "Crystalis" in self.multiworld.re_gen_passthrough:
                passthrough = self.multiworld.re_gen_passthrough["Crystalis"]
                self.options.randomize_maps.value = passthrough["randomize_maps"]
                self.options.shuffle_areas.value = passthrough["shuffle_areas"]
                self.options.shuffle_houses.value = passthrough["shuffle_houses"]
                self.options.randomize_tradeins.value = passthrough["randomize_tradeins"]
                self.options.unidentified_key_items.value = passthrough["unidentified_key_items"]
                self.options.shuffle_goa.value = passthrough["shuffle_goa"]
                self.options.randomize_wild_warp.value = passthrough["randomize_wild_warp"]
                self.options.story_mode.value = passthrough["story_mode"]
                self.options.no_bow_mode.value = passthrough["no_bow_mode"]
                self.options.orbs_not_required.value = passthrough["orbs_not_required"]
                self.options.thunder_warp.value = passthrough["thunder_warp"]
                self.options.vanilla_dolphin.value = passthrough["vanilla_dolphin"]
                self.options.fake_flight.value = passthrough["fake_flight"]
                self.options.statue_glitch.value = passthrough["statue_glitch"]
                self.options.mt_sabre_skip.value = passthrough["mt_sabre_skip"]
                self.options.statue_gauntlet_skip.value = passthrough["statue_gauntlet_skip"]
                self.options.sword_charge_glitch.value = passthrough["sword_charge_glitch"]
                self.options.trigger_skip.value = passthrough["trigger_skip"]
                self.options.rage_skip.value = passthrough["rage_skip"]
                self.options.randomize_monster_weaknesses.value = passthrough["randomize_monster_weaknesses"]
                self.options.oops_all_mimics.value = passthrough["oops_all_mimics"]
                self.options.dont_shuffle_mimics.value = passthrough["dont_shuffle_mimics"]
                self.options.keep_unique_items_and_consumables_separate.value = \
                    passthrough["keep_unique_items_and_consumables_separate"]
                self.options.guarantee_refresh.value = passthrough["guarantee_refresh"]
                self.options.battle_magic_not_guaranteed.value = passthrough["battle_magic_not_guaranteed"]
                self.options.tink_mode.value = passthrough["tink_mode"]
                self.options.barrier_not_guaranteed.value = passthrough["barrier_not_guaranteed"]
                self.options.gas_mask_not_guaranteed.value = passthrough["gas_mask_not_guaranteed"]
                self.options.charge_shots_only.value = passthrough["charge_shots_only"]
                self.options.dont_buff_bonus_items.value = passthrough["dont_buff_bonus_items"]
                self.options.vanilla_maps.value = passthrough["vanilla_maps"]
                self.options.vanilla_wild_warp.value = passthrough["vanilla_wild_warp"]
                shuffle_dict: Dict[str, Any] = passthrough["shuffle_data"]
                self.shuffle_data = CrystalisShuffleData(shuffle_dict["wall_map"], shuffle_dict["key_item_names"],
                                                         shuffle_dict["trade_in_map"], shuffle_dict["boss_reqs"],
                                                         shuffle_dict["gbc_cave_exits"], shuffle_dict["thunder_warp"],
                                                         shuffle_dict["shop_inventories"], shuffle_dict["wildwarps"],
                                                         shuffle_dict["goa_connection_map"])
                return #bail early, we don't need the rest of this lmao


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
        key_item_names: Dict[str, str] = self.unidentify_items()
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
        thunder_warp: str = ""
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
        #wildwarps
        wildwarps: List[int] = []
        if self.options.vanilla_wild_warp:
            #this technically has some tweaks over true vanilla - no Leaf warp (to leave room for a Mezame warp)
            #and replace Portoa Waterway with ESI's entrance (because Portoa Waterway's spawn is pointless).
            wildwarps = [0x03, 0x04, 0x14, 0x1a, 0x20, 0x40, 0x42, 0x60, 0x69, 0x72, 0x78, 0x7c, 0x90, 0xa8, 0x98]
        elif self.options.randomize_wild_warp:
            wildwarps = self.random.sample(list(self.wild_warp_id_to_region.keys()), k=15)
        wildwarps.append(0) #always have a warp for Mezame Shrine at the end
        #shuffle goa if necessary
        goa_connection_map: Dict[str, str]
        if self.options.shuffle_goa:
            goa_connection_map = self.shuffle_goa()
        else:
            goa_connection_map = {
                "Goa Entrance - Stairs": "Kelbesque's Floor - Front",
                "Kelbesque's Floor - Entrance": "Goa Entrance - Behind Wall",
                "Kelbesque's Floor - Exit": "Sabera's Floor - Front",
                "Sabera's Floor - Entrance": "Kelbesque's Floor - Back",
                "Sabera's Floor - Exit": "Mado's Floor - Front",
                "Mado's Floor - Entrance": "Sabera's Floor - Back",
                "Mado's Floor - Exit": "Karmine's Floor - Front",
                "Karmine's Floor - Entrance": "Mado's Floor - Back",
                "Karmine's Floor - Exit": "Goa Exit",
                "Goa Exit - Upstairs": "Karmine's Floor - Back"
            }
        self.shuffle_data = CrystalisShuffleData(wall_map, key_item_names, trade_in_map, boss_reqs, gbc_cave_exits,
                                                 thunder_warp, shop_inventories, wildwarps, goa_connection_map)


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

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        # returning slot_data so it regens, giving it back in multiworld.re_gen_passthrough
        return slot_data
