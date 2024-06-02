
import orjson
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Tuple, Any, Union
import pkgutil
from BaseClasses import Item, ItemClassification
from .types import CrystalisItemData


class CrystalisItem(Item):
    game: str = "Crystalis"

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int):
        super(CrystalisItem, self).__init__(name, classification, code, player)


def load_item_data_from_json() -> Dict[str, CrystalisItemData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/items.json").decode("utf-8-sig"))


items_data_json = load_item_data_from_json()
items_data: Dict[str, CrystalisItemData] = {}
#convert to actual type
for key, value in items_data_json.items():
    items_data[key] = CrystalisItemData(value["name"], value["rom_id"], value["ap_id_offset"], value["unique"], \
                                        value["losable"], value["prevent_loss"], value["default_count"], \
                                        value["groups"], value["category"])

