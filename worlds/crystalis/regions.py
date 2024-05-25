

from BaseClasses import Region
from .types import CrystalisRegionData
import orjson
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Tuple, Any, Union
import pkgutil


def load_region_data_from_json() -> Dict[str, CrystalisRegionData]:
    return orjson.loads(pkgutil.get_data(__name__, "data/regions.json").decode("utf-8-sig"))


regions_data = load_region_data_from_json()
#convert to actual type
for key, value in regions_data.items():
    regions_data[key] = CrystalisRegionData(**value)
