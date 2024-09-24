import logging
from dataclasses import dataclass
from BaseClasses import ItemClassification
from enum import IntEnum
from typing import List, Dict, Optional, Tuple

CRYSTALIS_BASE_ID: int = 2241000
CRYSTALIS_APWORLD_VERSION = "0.1.0"


class CrystalisElementEnum(IntEnum):
    WIND = 0
    FIRE = 1
    WATER = 2
    THUNDER = 3


def convert_text_to_elem_enum(text: str):
    if text == "Wind":
        return CrystalisElementEnum.WIND
    if text == "Fire":
        return CrystalisElementEnum.FIRE
    if text == "Water":
        return CrystalisElementEnum.WATER
    if text == "Thunder":
        return CrystalisElementEnum.THUNDER
    logging.warning("Unregonized element: " + text)
    return CrystalisElementEnum.WIND


class CrystalisItemCategoryEnum(IntEnum):
    FILLER = 0
    PROGRESSION = 1
    USEFUL = 2
    CONDITIONAL = 3
    TRAP = 4


def convert_enum_to_item_classification(enum: CrystalisItemCategoryEnum) -> ItemClassification:
    if enum == CrystalisItemCategoryEnum.FILLER:
        return ItemClassification.filler
    if enum ==  CrystalisItemCategoryEnum.PROGRESSION:
        return ItemClassification.progression
    if enum ==  CrystalisItemCategoryEnum.USEFUL:
        return ItemClassification.useful
    if enum ==  CrystalisItemCategoryEnum.CONDITIONAL:
        logging.warning("Unhandled conditional progression item in Crystalis. Defaulting to progression.")
        return ItemClassification.progression
    if enum ==  CrystalisItemCategoryEnum.TRAP:
        return ItemClassification.trap
    raise ValueError(f"Crystalis: Unrecognized value in convert_enum_to_item_classification: {enum}")
    return ItemClassification.filler


class CrystalisItemPaletteEnum(IntEnum):
    WIND_EQUIP = 0
    FIRE_EQUIP = 1
    WATER_EQUIP = 2
    THUNDER_EQUIP = 3
    WIND_CONSUMABLE = 4
    FIRE_CONSUMABLE = 5
    WATER_CONSUMABLE = 6
    THUNDER_CONSUMABLE = 7
    MIMIC = 8
    RANDOM = 9


def convert_enum_to_palette(enum: CrystalisItemPaletteEnum) -> Tuple[int, int]:
    if enum == CrystalisItemPaletteEnum.WIND_EQUIP:
        return [0x19,0x03]
    if enum == CrystalisItemPaletteEnum.FIRE_EQUIP:
        return [0x27,0x16]
    if enum == CrystalisItemPaletteEnum.WATER_EQUIP:
        return [0x2C,0x12]
    if enum == CrystalisItemPaletteEnum.THUNDER_EQUIP:
        return [0x37,0x0C]
    if enum == CrystalisItemPaletteEnum.WIND_CONSUMABLE:
        return [0x2A,0x03]
    if enum == CrystalisItemPaletteEnum.FIRE_CONSUMABLE:
        return [0x27,0x05]
    if enum == CrystalisItemPaletteEnum.WATER_CONSUMABLE:
        return [0x2C,0x12]
    if enum == CrystalisItemPaletteEnum.THUNDER_CONSUMABLE:
        return [0x28,0x00]
    if enum == CrystalisItemPaletteEnum.MIMIC:
        return [0x36,0x14]
    raise ValueError(f"Crystalis: Unrecognized value in convert_enum_to_palette: {enum}")
    return [0,0]


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
    is_chest: bool


@dataclass
class CrystalisEntranceData:
    name: str
    entrance_type: CrystalisEntranceTypeEnum
    vanilla_target: str


@dataclass
class CrystalisRegionData:
    name: str
    wildwarpIds: List[int]
    entrances: List[CrystalisEntranceData]
    locations: List[CrystalisLocationData]
    ban_wildwarp: bool


@dataclass
class CrystalisItemData:
    name: str
    rom_id: int
    ap_id_offset: int
    unique: bool
    losable: bool
    prevent_loss: bool
    community: bool
    default_count: int
    groups: List[str]
    palette: CrystalisItemPaletteEnum
    category: CrystalisItemCategoryEnum


@dataclass
class CrystalisShuffleData:
    wall_map: Dict[str, str]
    key_item_names: Dict[str, str]
    trade_in_map: Dict[str, str]
    boss_reqs: Dict[str, str]
    gbc_cave_exits: List[str]
    thunder_warp: str
    shop_inventories: Dict[str, List[str]]
    wildwarps: List[int]
    goa_connection_map: Dict[str, str]
