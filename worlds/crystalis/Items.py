
import orjson
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Tuple, Any, Union
import pkgutil
from BaseClasses import Item, ItemClassification
from .CrystalisTypes import CrystalisItemData


class ItemData(NamedTuple):
    code: Optional[int]
    progression: bool
    quantity: int = 1
    event: bool = False


class CrystalisItem(Item):
    game: str = "Crystalis"

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int):
        super(CrystalisItem, self).__init__(name, classification, code, player)


def load_item_data_from_json() -> Dict[str, CrystalisItemData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/items.json").decode("utf-8-sig"))


items_data = load_item_data_from_json()
#convert to actual type
for key, value in items_data.items():
    items_data[key] = CrystalisItemData(**value)

