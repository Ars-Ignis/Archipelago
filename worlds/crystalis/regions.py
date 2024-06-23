

from BaseClasses import Region
from .types import CrystalisRegionData, CrystalisLocationData, CrystalisEntranceData
import orjson
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Tuple, Any, Union
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
