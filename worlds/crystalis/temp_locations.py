from typing import Dict, List
from BaseClasses import Location, Region
from .CrystalisTypes import CrystalisLocationData, CrystalisRegionData, CRYSTALIS_BASE_ID


class CrystalisLocation(Location):
    game: str = "Crystalis"

    def __init__(self, player: int, name="", code=None, parent=None, unique=False, lossy=False) -> None:
        super(CrystalisLocation, self).__init__(player, name, code, parent)
        self.event = code is None


def aggregate_location_data_from_regions(regions: Dict[str, CrystalisRegionData]) -> List[CrystalisLocationData]:
    location_data_list: List[CrystalisLocationData] = []
    for region_data in regions.values():
        for location in region_data.locations:
            location_data_list.append(CrystalisLocationData(**location))
    return location_data_list


def create_location_from_location_data(player: int, location_data: CrystalisLocationData, region: Region) \
        -> CrystalisLocation:
    return CrystalisLocation(player,
                             location_data.name,
                             location_data.ap_id_offset + CRYSTALIS_BASE_ID,
                             region,
                             location_data.unique,
                             location_data.lossy
                             )
