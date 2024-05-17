
from dataclasses import dataclass
from BaseClasses import ItemClassification
from enum import IntEnum
from typing import List

CRYSTALIS_BASE_ID: int = 2241000


class CrystalisItemCategoryEnum(IntEnum):
    FILLER = 0
    PROGRESSION = 1
    USEFUL = 2
    CONDITONAL = 3
    TRAP = 4

def convert_enum_to_item_classification(enum: CrystalisItemCategoryEnum) -> ItemClassification:
    match enum:
        case CrystalisItemCategoryEnum.FILLER:
            return ItemClassification.filler
        case CrystalisItemCategoryEnum.PROGRESSION:
            return ItemClassification.progression
        case CrystalisItemCategoryEnum.USEFUL:
            return ItemClassification.useful
        case CrystalisItemCategoryEnum.CONDITONAL:
            #TODO: figure this out later
            return ItemClassification.progression
        case CrystalisItemCategoryEnum.TRAP:
            return ItemClassification.trap
        case _:
            #TODO: proper error handling?
            return ItemClassification.filler

class CrystalisEntranceTypeEnum(IntEnum):
    STATIC = 0
    OW_UP = 1
    OW_DOWN = 2
    OW_LEFT = 3
    OW_RIGHT = 4
    CAVE_ENTRANCE = 5
    CAVE_EXIT = 6
    HOUSE_ENTRANCE = 7
    HOUSE_EXIT = 8
    PALACE_ENTRANCE = 9
    PALACE_EXIT = 10
    SHED_ENTRANCE = 11
    SHED_EXIT = 12
    EXT_ENTRANCE = 13
    EXT_EXIT = 14
    GOA_TRANSITION = 15


@dataclass
class CrystalisLocationData:
    name: str
    rom_id: int
    ap_id_offset: int
    unique: bool
    lossy: bool
    prevent_loss: bool
    broken: bool
    pseudologic: str


@dataclass
class CrystalisEntranceData:
    name: str
    entrance_type: CrystalisEntranceTypeEnum
    vanilla_target: str
    pseudologic: str
    notes: str


@dataclass
class CrystalisRegionData:
    name: str
    wildwarpIds: List[int]
    notes: str
    entrances: List[CrystalisEntranceData]
    locations: List[CrystalisLocationData]


@dataclass
class CrystalisItemData:
    name: str
    rom_id: int
    ap_id_offset: int
    unique: bool
    losable: bool
    prevent_loss: bool
    default_count: int
    groups: List[str]
    category: CrystalisItemCategoryEnum
    notes: str
