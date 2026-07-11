# Python Imports
import orjson
import pkgutil
from typing import Any

# Archipelago Imports
from Utils import Version, tuplize_version

# Crystalis Imports
from .types import *


def load_world_version_from_json() -> Version:
    manifest: dict[str, Any] = orjson.loads(pkgutil.get_data(__name__, "archipelago.json").decode("utf-8-sig"))
    version_string: str = manifest["world_version"]
    return tuplize_version(version_string)

########################################################
#   Overall Constants                                  #
########################################################


CRYSTALIS_DEBUG: bool = True if __debug__ else False
CRYSTALIS_BASE_ID: int = 2241000
CRYSTALIS_APWORLD_VERSION: Version = load_world_version_from_json() # used in client because world_version isn't available


########################################################
#   Generation Constants                               #
########################################################

BOSS_NAMES: List[str] = ["Giant Insect",
                         "Vampire 2",
                         "Kelbesque 1",
                         "Sabera 1",
                         "Mado 1",
                         "Kelbesque 2",
                         "Sabera 2",
                         "Mado 2",
                         "Karmine"]

BOSS_IDS: Dict[str, int] = {
    "Giant Insect": 0x5e,
    "Vampire 2": 0xa5,
    "Kelbesque 1": 0x68,
    "Sabera 1": 0x7d,
    "Mado 1": 0x88,
    "Kelbesque 2": 0x8b,
    "Sabera 2": 0x90,
    "Mado 2": 0x93,
    "Karmine": 0x97
}

ELEMENTS: List[str] = [
    "Wind",
    "Fire",
    "Water",
    "Thunder"
]

WALL_NAMES: List[str] = [
    "Zebu Cave",
    "East Cave",
    "Sealed Cave",
    "Mt Sabre West",
    "Mt Sabre North",
    "Waterfall Cave",
    "Fog Lamp Cave",
    "Kirisa Plant Cave",
    "Evil Spirit Island",
    "Mt Hydra",
    "Goa Fortress - Entrance",
    "Goa Fortress Basement",
    "Goa Fortress - Sabera Item",
    "Goa Fortress - Sabera Boss",
    "Goa Fortress - Mado 2",
    "Goa Fortress - Karmine 5"
]

TRADE_IN_NPCS: List[str] = [
    "Akahana",
    "Aryllis",
    "Fisherman",
    "Kensu",
    "Slimed Kensu"
]

SHOP_INVENTORIES: Dict[str, List[str]] = {
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

SCREEN_NAMES_TO_IDS: Dict[str, int] = {
    "Leaf - Outside Start": 0x1,
    "Leaf": 0x2,
    "Valley of Wind": 0x3,
    "Sealed Cave 1": 0x4,
    "Sealed Cave 2": 0x5,
    "Sealed Cave 6": 0x6,
    "Sealed Cave 4": 0x7,
    "Sealed Cave 5": 0x8,
    "Sealed Cave 3": 0x9,
    "Sealed Cave 7": 0xA,
    "East Cave 1": 0xB,
    "Sealed Cave 8": 0xC,
    "East Cave 2": 0xD,
    "Windmill Cave": 0xE,
    "Windmill": 0xF,
    "Zebu Cave": 0x10,
    "Mt Sabre West - Cave 1": 0x11,
    "East Cave 3": 0x12,
    "Cordel Plain West": 0x14,
    "Cordel Plain East": 0x15,
    "Brynmaer": 0x18,
    "Outside Stom House": 0x19,
    "Swamp": 0x1A,
    "Amazones": 0x1B,
    "Oak": 0x1C,
    "Stom House": 0x1E,
    "Mt Sabre West - Lower": 0x20,
    "Mt Sabre West - Upper": 0x21,
    "Mt Sabre West - Cave 2": 0x22,
    "Mt Sabre West - Cave 3": 0x23,
    "Mt Sabre West - Cave 4": 0x24,
    "Mt Sabre West - Cave 5": 0x25,
    "Mt Sabre West - Cave 6": 0x26,
    "Mt Sabre West - Cave 7": 0x27,
    "Mt Sabre North - Main": 0x28,
    "Mt Sabre North - Middle": 0x29,
    "Mt Sabre North - Cave 2": 0x2A,
    "Mt Sabre North - Cave 3": 0x2B,
    "Mt Sabre North - Cave 4": 0x2C,
    "Mt Sabre North - Cave 5": 0x2D,
    "Mt Sabre North - Cave 6": 0x2E,
    "Mt Sabre North - Prison Hall": 0x2F,
    "Mt Sabre North - Left Cell": 0x30,
    "Mt Sabre North - Left Cell 2": 0x31,
    "Mt Sabre North - Right Cell": 0x32,
    "Mt Sabre North - Cave 8": 0x33,
    "Mt Sabre North - Cave 9": 0x34,
    "Mt Sabre North - Summit Cave": 0x35,
    "Mt Sabre North - Cave 1": 0x38,
    "Mt Sabre North - Cave 7": 0x39,
    "Nadare - Back Room": 0x3E,
    "Waterfall Valley North": 0x40,
    "Waterfall Valley South": 0x41,
    "Lime Tree Valley": 0x42,
    "Kirisa Plant Cave 1": 0x44,
    "Kirisa Plant Cave 2": 0x45,
    "Kirisa Plant Cave 3": 0x46,
    "Kirisa Meadow": 0x47,
    "Fog Lamp Cave 1": 0x48,
    "Fog Lamp Cave 2": 0x49,
    "Fog Lamp Cave 3": 0x4A,
    "Fog Lamp Cave Dead End": 0x4B,
    "Fog Lamp Cave 4": 0x4C,
    "Fog Lamp Cave 5": 0x4D,
    "Fog Lamp Cave 6": 0x4E,
    "Fog Lamp Cave 7": 0x4F,
    "Portoa": 0x50,
    "Portoa - Fisherman Island": 0x51,
    "Waterfall Cave 1": 0x54,
    "Waterfall Cave 2": 0x55,
    "Waterfall Cave 3": 0x56,
    "Waterfall Cave 4": 0x57,
    "Angry Sea": 0x60,
    "Boat House": 0x61,
    "Joel Lighthouse": 0x62,
    "Zombie Town": 0x65,
    "Evil Spirit Island 2": 0x69,
    "Evil Spirit Island 3": 0x6A,
    "Evil Spirit Island 4": 0x6B,
    "Sabera Palace 1": 0x6C,
    "Sabera Palace 2": 0x6D,
    "Sabera Palace 3": 0x6E,
    "Sabera Palace 2 - West": 0x6F,
    "Joel Secret Passage": 0x70,
    "Joel": 0x71,
    "Swan": 0x72,
    "Swan Gate": 0x73,
    "Goa Valley": 0x78,
    "Mt Hydra": 0x7C,
    "Mt Hydra - Cave 1": 0x7D,
    "Mt Hydra - Outside Shyron": 0x7E,
    "Mt Hydra - Cave 2": 0x7F,
    "Mt Hydra - Cave 3": 0x80,
    "Mt Hydra - Cave 4": 0x81,
    "Mt Hydra - Cave 5": 0x82,
    "Mt Hydra - Cave 6": 0x83,
    "Mt Hydra - Cave 7": 0x84,
    "Mt Hydra - Cave 8": 0x85,
    "Mt Hydra - Cave 9": 0x86,
    "Mt Hydra - Cave 10": 0x87,
    "Styx 1": 0x88,
    "Styx 2": 0x89,
    "Styx 3": 0x8A,
    "Shyron": 0x8C,
    "Goa": 0x8E,
    "Goa Fortress Basement": 0x8F,
    "Desert 1": 0x90,
    "Oasis Cave Main": 0x91,
    "Desert Cave 1": 0x92,
    "Sahara": 0x93,
    "Sahara Outside Cave": 0x94,
    "Desert Cave 2": 0x95,
    "Sahara Meadow": 0x96,
    "Desert 2": 0x98,
    "Pyramid - Entrance": 0x9C,
    "Pyramid - Branch": 0x9D,
    "Pyramid - Main": 0x9E,
    "Pyramid - Draygon": 0x9F,
    "Crypt - Entrance": 0xA0,
    "Crypt - Hall 1": 0xA1,
    "Crypt - Branch": 0xA2,
    "Crypt - Dead End Left": 0xA3,
    "Crypt - Dead End Right": 0xA4,
    "Crypt - Hall 2": 0xA5,
    "Goa Fortress - Entrance": 0xA8,
    "Goa Fortress - Kelbesque": 0xA9,
    "Goa Fortress - Zebu": 0xAA,
    "Goa Fortress - Sabera": 0xAB,
    "Goa Fortress - Tornel": 0xAC,
    "Goa Fortress - Mado 1": 0xAD,
    "Goa Fortress - Mado 2": 0xAE,
    "Goa Fortress - Mado 3": 0xAF,
    "Goa Fortress - Karmine 1": 0xB0,
    "Goa Fortress - Karmine 2": 0xB1,
    "Goa Fortress - Karmine 3": 0xB2,
    "Goa Fortress - Karmine 4": 0xB3,
    "Goa Fortress - Karmine 5": 0xB4,
    "Goa Fortress - Karmine 6": 0xB5,
    "Goa Fortress - Karmine 7": 0xB6,
    "Goa Fortress - Exit": 0xB7,
    "Oasis Cave - Entrance": 0xB8,
    "Goa Fortress - Asina": 0xB9,
    "Goa Fortress - Kensu": 0xBA,
    "Goa - House": 0xBB,
    "Goa - Tavern": 0xBF,
    "Leaf - Elder House": 0xC0,
    "Leaf - Rabbit Hut": 0xC1,
    "Leaf - Student House": 0xC5,
    "Brynmaer - Tavern": 0xC6,
    "Oak - Elder House": 0xCD,
    "Oak - Mother House": 0xCE,
    "Amazones - Elder": 0xD4,
    "Nadare": 0xD5,
    "Portoa - Fisherman House": 0xD6,
    "Portoa - Palace Entrance": 0xD7,
    "Portoa - Fortune Teller": 0xD8,
    "Portoa Palace - Left": 0xDE,
    "Portoa Palace - Throne Room": 0xDF,
    "Portoa Palace - Right": 0xE0,
    "Portoa - Asina Room": 0xE1,
    "Amazones - Elder Downstairs": 0xE2,
    "Joel - Elder House": 0xE3,
    "Joel - Shed": 0xE4,
    "Zombie Town - House": 0xE8,
    "Zombie Town - House Basement": 0xE9,
    "Swan - Stom Hut": 0xEC,
    "Swan - Tavern": 0xEF,
    "Swan - Dance Hall": 0xF1,
    "Shyron - Temple": 0xF2,
    "Shyron - Training Hall": 0xF3,
    "Shyron - Hospital": 0xF4,
    "Sahara - Elder House": 0xFA,
}

ENTRANCE_COLORINGS: Dict[int, int] = {
    CrystalisEntranceTypeEnum.STATIC: 0x000000,
    CrystalisEntranceTypeEnum.OW_UP: 0x00FFFF,
    CrystalisEntranceTypeEnum.OW_DOWN: 0x00AAAA,
    CrystalisEntranceTypeEnum.OW_LEFT: 0xFF00FF,
    CrystalisEntranceTypeEnum.OW_RIGHT: 0xAA00AA,
    CrystalisEntranceTypeEnum.CAVE_ENTRANCE: 0xFF0000,
    CrystalisEntranceTypeEnum.CAVE_EXIT: 0xAA0000,
    CrystalisEntranceTypeEnum.HOUSE_ENTRANCE: 0x00FF00,
    CrystalisEntranceTypeEnum.HOUSE_EXIT: 0x00AA00,
    CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE: 0x0000FF,
    CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT: 0x0000AA,
    CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE: 0x0000FF,
    CrystalisEntranceTypeEnum.PALACE_AREA_EXIT: 0x0000AA,
    CrystalisEntranceTypeEnum.SHED_ENTRANCE: 0xFFFF00,
    CrystalisEntranceTypeEnum.SHED_EXIT: 0xAAAA00,
    CrystalisEntranceTypeEnum.EXT_ENTRANCE: 0xF0F0F0,
    CrystalisEntranceTypeEnum.EXT_EXIT: 0xA0A0A0,
    CrystalisEntranceTypeEnum.GOA_TRANSITION: 0x000000
}

HOUSE_SHUFFLE_TYPES = frozenset([CrystalisEntranceTypeEnum.HOUSE_ENTRANCE,
                                 CrystalisEntranceTypeEnum.HOUSE_EXIT,
                                 CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                                 CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                                 CrystalisEntranceTypeEnum.SHED_ENTRANCE,
                                 CrystalisEntranceTypeEnum.SHED_EXIT,
                                 CrystalisEntranceTypeEnum.EXT_ENTRANCE,
                                 CrystalisEntranceTypeEnum.EXT_EXIT])

AREA_SHUFFLE_TYPES = frozenset([CrystalisEntranceTypeEnum.OW_UP,
                                CrystalisEntranceTypeEnum.OW_DOWN,
                                CrystalisEntranceTypeEnum.OW_LEFT,
                                CrystalisEntranceTypeEnum.OW_RIGHT,
                                CrystalisEntranceTypeEnum.CAVE_ENTRANCE,
                                CrystalisEntranceTypeEnum.CAVE_EXIT,
                                CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                                CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                                CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE,
                                CrystalisEntranceTypeEnum.PALACE_AREA_EXIT])

SHUFFLE_GROUPING = {
    CrystalisEntranceTypeEnum.OW_UP: [CrystalisEntranceTypeEnum.OW_DOWN],
    CrystalisEntranceTypeEnum.OW_DOWN: [CrystalisEntranceTypeEnum.OW_UP],
    CrystalisEntranceTypeEnum.OW_LEFT: [CrystalisEntranceTypeEnum.OW_RIGHT],
    CrystalisEntranceTypeEnum.OW_RIGHT: [CrystalisEntranceTypeEnum.OW_LEFT],
    CrystalisEntranceTypeEnum.CAVE_ENTRANCE: [CrystalisEntranceTypeEnum.CAVE_EXIT],
    CrystalisEntranceTypeEnum.CAVE_EXIT: [CrystalisEntranceTypeEnum.CAVE_ENTRANCE],
    CrystalisEntranceTypeEnum.HOUSE_ENTRANCE: [CrystalisEntranceTypeEnum.HOUSE_EXIT],
    CrystalisEntranceTypeEnum.HOUSE_EXIT: [CrystalisEntranceTypeEnum.HOUSE_ENTRANCE],
    CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE: [CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT,
                                                      CrystalisEntranceTypeEnum.PALACE_AREA_EXIT],
    CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT: [CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE,
                                                  CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE],
    CrystalisEntranceTypeEnum.SHED_ENTRANCE: [CrystalisEntranceTypeEnum.SHED_EXIT],
    CrystalisEntranceTypeEnum.SHED_EXIT: [CrystalisEntranceTypeEnum.SHED_ENTRANCE],
    CrystalisEntranceTypeEnum.EXT_ENTRANCE: [CrystalisEntranceTypeEnum.EXT_EXIT],
    CrystalisEntranceTypeEnum.EXT_EXIT: [CrystalisEntranceTypeEnum.EXT_ENTRANCE],
    CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE: [CrystalisEntranceTypeEnum.PALACE_AREA_EXIT,
                                                     CrystalisEntranceTypeEnum.PALACE_HOUSE_EXIT],
    CrystalisEntranceTypeEnum.PALACE_AREA_EXIT: [CrystalisEntranceTypeEnum.PALACE_AREA_ENTRANCE,
                                                 CrystalisEntranceTypeEnum.PALACE_HOUSE_ENTRANCE]
}

GBC_CAVE_NAMES = [
    "Cordel Plains - Main - Added Cave",
    "Lime Valley - Added Cave",
    "Goa Valley - Added Cave",
    "Desert 2 - Added Cave",
    "Wind Valley - East Cave",
    "GBC Cave - Free Exit",
    "GBC Cave - Blocked Exit",
    "GBC Cave Entrance"
]

LIME_PASSAGE_NAMES = [
    "Wind Valley - East",
    "Lime Valley - West"
]

CRYSTALIS_MAX_GER_ATTEMPTS: int = 10
WARP_MINIMUM = 4
WARP_MAXIMUM = 15

TOWNS_WITH_IDS: dict[int, str] = {
    0x0200: "Leaf",
    0x1800: "Brynmaer",
    0x1c00: "Oak",
    0xd500: "Nadare's",
    0x5000: "Portoa",
    0x1b00: "Amazones",
    0x7100: "Joel",
    0x6500: "Zombie Town",
    0x7200: "Swan",
    0x8c00: "Shyron",
    0x8e00: "Goa",
    0x9300: "Sahara"
}

TOWNS: list[str] = [
    "Leaf",
    "Brynmaer",
    "Oak",
    "Nadare's",
    "Portoa",
    "Amazones",
    "Joel",
    "Zombie Town",
    "Swan",
    "Shyron",
    "Goa",
    "Sahara"
]

########################################################
#   Client Constants                                   #
########################################################

# Addresses
MAIN_LOOP_MODE_ADDR: int = 0x40
GAME_MODE_ADDR: int = 0x41
CURRENT_LOCATION_ADDR: int = 0x6C
HP_ADDR: int = 0x3C1
SCREEN_LOCK_ADDR: int = 0x07D7
START_OF_SWORD_INV_ADDR: int = 0x6430
START_OF_CONSUMABLE_INV_ADDR: int = 0x6440
END_OF_CONSUMABLE_INV_ADDR: int = 0x6447
LOCATION_FLAGS_ADDR: int = 0x64A0
ITEM_FLAGS_ADDR: int = 0x64C0
GET_ITEM_FLAG_ADDR: int = 0x657A # metadata byte, status byte, item ID byte
RECEIVED_INDEX_ADDR: int = 0x657D
AP_ROM_LABEL_ADDR: int = 0x25715

# In-Game Data
SWORD_OF_THUNDER_ITEM_ID: int = 0x03
CRYSTALIS_SWORD_ITEM_ID: int = 0x04
EXPECTED_START: List[bytes] = [bytes([0xD9, 0xD9, 0xD9, 0xD9, 0xD9, 0xD9, 0xD9, 0xD9])]
AP_ROM_LABEL: List[bytes] = [bytes([0x41, 0x52, 0x43, 0x48, 0x49, 0x50, 0x45, 0x4C, 0x41, 0x47, 0x4F])]
GAME_MODE_DEATH: int = 3
GAME_MODE_NORMAL: int = 8
GAME_MODE_DYNA_DEFEATED: int = 0x1E
MAIN_LOOP_GAME: int = 1
TRAP_NAME_TO_METADATA_VALUE: dict[str, int] = {
    "Wild Warp Trap": 0,
    "Paralysis Trap": 1,
    "Petrify Trap": 2,
    "Poison Trap": 3,
    "Nuper Trap": 4
}

# APWorld Data
ASINA_LOCATION_NAME: str = "Asina In Back Room"
WHIRLPOOL_LOCATION_NAME: str = "Behind Whirlpool"
ITERATIONS_TO_MATCH: int = 1
