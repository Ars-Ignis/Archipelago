import orjson
from typing import Dict, List, Optional
import pkgutil
from BaseClasses import Item, ItemClassification
from .types import CrystalisItemData, CRYSTALIS_BASE_ID, convert_enum_to_item_classification


basic_key_names: List[str] = []
all_key_names: List[str] = []
basic_flute_names: List[str] = []
all_flute_names: List[str] = []
basic_lamp_names: List[str] = []
all_lamp_names: List[str] = []
basic_statue_names: List[str] = []
all_statue_names: List[str] = []
basic_bow_names: List[str] = []
all_bow_names: List[str] = []


def load_item_data_from_json() -> Dict[str, CrystalisItemData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/items.json").decode("utf-8-sig"))


items_data_json = load_item_data_from_json()
items_data: Dict[str, CrystalisItemData] = {}
items_data_by_id: Dict[int, CrystalisItemData] = {}
#convert to actual type
for key, value in items_data_json.items():
    item_data = CrystalisItemData(value["name"], value["rom_id"], value["ap_id_offset"], value["unique"],
                                  value["losable"], value["prevent_loss"], value["community"], value["default_count"],
                                  value["groups"], value["category"])
    items_data[key] = item_data
    items_data_by_id[item_data.ap_id_offset + CRYSTALIS_BASE_ID] = item_data
    if item_data.default_count == 0 and "Key Item" in item_data.groups:
        if "Key" in item_data.groups:
            all_key_names.append(item_data.name)
            if not item_data.community:
                basic_key_names.append(item_data.name)
        elif "Flute" in item_data.groups:
            all_flute_names.append(item_data.name)
            if not item_data.community:
                basic_flute_names.append(item_data.name)
        elif "Lamp" in item_data.groups:
            all_lamp_names.append(item_data.name)
            if not item_data.community:
                basic_lamp_names.append(item_data.name)
        elif "Statue" in item_data.groups:
            all_statue_names.append(item_data.name)
            if not item_data.community:
                basic_statue_names.append(item_data.name)
        elif "Bow" in item_data.groups:
            all_bow_names.append(item_data.name)
            if not item_data.community:
                basic_bow_names.append(item_data.name)

class CrystalisItem(Item):
    game: str = "Crystalis"

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int):
        super(CrystalisItem, self).__init__(name, classification, code, player)


def unidentify_items(self) -> Dict[str, str]:
    keys: List[str] = []
    flutes: List[str] = []
    lamps: List[str] = []
    statues: List[str] = []
    bows: List[str] = []
    for item in items_data.values():
        if "Key" in item.groups and item.default_count > 0:
            keys.append(item.name)
        elif "Flute" in item.groups and item.default_count > 0:
            flutes.append(item.name)
        elif "Lamp" in item.groups and item.default_count > 0:
            lamps.append(item.name)
        elif "Statue" in item.groups and item.default_count > 0:
            statues.append(item.name)
        elif "Bow" in item.groups and item.default_count > 0:
            bows.append(item.name)
    all_key_items: List[str] = keys + flutes + lamps + statues + bows
    if not self.options.unidentified_key_items:
        return dict(zip(all_key_items, all_key_items))
    key_choices: List[str]
    flute_choices: List[str]
    lamp_choices: List[str]
    statue_choices: List[str]
    bow_choices: List[str]
    if self.options.no_community_jokes:
        key_choices = self.random.sample(basic_key_names, k=len(keys))
        flute_choices = self.random.sample(basic_flute_names, k=len(flutes))
        lamp_choices = self.random.sample(basic_lamp_names, k=len(lamps))
        statue_choices = self.random.sample(basic_statue_names, k=len(statues))
        bow_choices = self.random.sample(basic_bow_names, k=len(bows))
    else:
        key_choices = self.random.sample(all_key_names, k=len(keys))
        flute_choices = self.random.sample(all_flute_names, k=len(flutes))
        lamp_choices = self.random.sample(all_lamp_names, k=len(lamps))
        statue_choices = self.random.sample(all_statue_names, k=len(statues))
        bow_choices = self.random.sample(all_bow_names, k=len(bows))
    all_choices: List[str] = key_choices + flute_choices + lamp_choices + statue_choices + bow_choices
    return dict(zip(all_key_items, all_choices))


def create_item(self, name: str) -> "Item":
    item_data: CrystalisItemData = items_data[name]
    return CrystalisItem(name, convert_enum_to_item_classification(item_data.category), item_data.ap_id_offset +
                         CRYSTALIS_BASE_ID, self.player)


def create_items(self) -> None:
    swords: List[CrystalisItem] = []
    for item_data in items_data.values():
        if item_data.name in self.shuffle_data.key_item_names.keys():
            self.multiworld.itempool.append(self.create_item(self.shuffle_data.key_item_names[item_data.name]))
        elif "Sword" in item_data.groups:
            swords.append(self.create_item(item_data.name))
        else:
            for i in range(item_data.default_count):
                self.multiworld.itempool.append(self.create_item(item_data.name))
    if self.options.guarantee_starting_sword:
        fixed_sword = self.random.choice(swords)
        swords.remove(fixed_sword)
        #technically stand-alone doesn't do this... but I think it fits the spirit of the flag
        if self.options.shuffle_areas or self.options.shuffle_houses:
            mezame_left_location = self.get_location("Mezame Left Chest")
            mezame_left_location.place_locked_item(fixed_sword)
        else:
            leaf_elder_location = self.get_location("Leaf Elder")
            leaf_elder_location.place_locked_item(fixed_sword)
    #put the three or four swords in the itempool
    for sword in swords:
        self.multiworld.itempool.append(sword)
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


