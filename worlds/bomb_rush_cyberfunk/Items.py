from typing import TypedDict, List, Dict, Set
from enum import Enum


class BRCType(Enum):
    Music = 0
    GraffitiM = 1
    GraffitiL = 2
    GraffitiXL = 3
    Skateboard = 4
    InlineSkates = 5
    BMX = 6
    Character = 7
    Outfit = 8
    REP = 9
    Camera = 10


class ItemDict(TypedDict, total=False):
    name: str
    count: int
    type: BRCType


base_id = 2308000


item_table: List[ItemDict] = [
    # Music
    {'name': "Music (GET ENUF)",
        'type': BRCType.Music},
    {'name': "Music (Chuckin Up)",
        'type': BRCType.Music},
    {'name': "Music (Spectres)",
        'type': BRCType.Music},
    {'name': "Music (You Can Say Hi)",
        'type': BRCType.Music},
    {'name': "Music (JACK DA FUNK)",
        'type': BRCType.Music},
    {'name': "Music (Feel The Funk (Computer Love))",
        'type': BRCType.Music},
    {'name': "Music (Big City Life)",
        'type': BRCType.Music},
    {'name': "Music (I Wanna Kno)",
        'type': BRCType.Music},
    {'name': "Music (Plume)",
        'type': BRCType.Music},
    {'name': "Music (Two Days Off)",
        'type': BRCType.Music},
    {'name': "Music (Scraped On The Way Out)",
        'type': BRCType.Music},
    {'name': "Music (Last Hoorah)",
        'type': BRCType.Music},
    {'name': "Music (State of Mind)",
        'type': BRCType.Music},
    {'name': "Music (AGUA)",
        'type': BRCType.Music},
    {'name': "Music (Condensed milk)",
        'type': BRCType.Music},
    {'name': "Music (Light Switch)",
        'type': BRCType.Music},
    {'name': "Music (Hair Dun Nails Dun)",
        'type': BRCType.Music},
    {'name': "Music (Precious Thing)",
        'type': BRCType.Music},
    {'name': "Music (Next To Me)",
        'type': BRCType.Music},
    {'name': "Music (Refuse)",
        'type': BRCType.Music},
    {'name': "Music (Iridium)",
        'type': BRCType.Music},
    {'name': "Music (Funk Express)",
        'type': BRCType.Music},
    {'name': "Music (In The Pocket)",
        'type': BRCType.Music},
    {'name': "Music (Bounce Upon A Time)",
        'type': BRCType.Music},
    {'name': "Music (hwbouths)",
        'type': BRCType.Music},
    {'name': "Music (Morning Glow)",
        'type': BRCType.Music},
    {'name': "Music (Chromebies)",
        'type': BRCType.Music},
    {'name': "Music (watchyaback!)",
        'type': BRCType.Music},
    {'name': "Music (Anime Break)",
        'type': BRCType.Music},
    {'name': "Music (DA PEOPLE)",
        'type': BRCType.Music},
    {'name': "Music (Trinitron)",
        'type': BRCType.Music},
    {'name': "Music (Operator)",
        'type': BRCType.Music},
    {'name': "Music (Sunshine Popping Mixtape)",
        'type': BRCType.Music},
    {'name': "Music (House Cats Mixtape)",
        'type': BRCType.Music},
    {'name': "Music (Breaking Machine Mixtape)",
        'type': BRCType.Music},
    {'name': "Music (Beastmode Hip Hop Mixtape)",
        'type': BRCType.Music},

    # Graffiti
    {'name': "Graffiti (M - OVERWHELMME)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - QUICK BING)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - BLOCKY)",
        'type': BRCType.GraffitiM},
    #{'name': "Graffiti (M - Flow)",
    #    'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Pora)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Teddy 4)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - BOMB BEATS)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - SPRAYTANICPANIC!)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - SHOGUN)",
        'type': BRCType.GraffitiM},
    #{'name': "Graffiti (M - EVIL DARUMA)",
    #    'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - TeleBinge)",
        'type': BRCType.GraffitiM},
    #{'name': "Graffiti (M - All Screws Loose)",
    #    'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - 0m33)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Vom'B)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Street classic)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Thick Candy)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - colorBOMB)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Zona Leste)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Stacked Symbols)",
        'type': BRCType.GraffitiM},
    #{'name': "Graffiti (M - Constellation Circle)",
    #    'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - B-boy Love)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - Devil 68)",
        'type': BRCType.GraffitiM},
    {'name': "Graffiti (M - pico pow)",
        'type': BRCType.GraffitiM},
    #{'name': "Graffiti (M - 8 MINUTES OF LEAN MEAN)",
    #    'type': BRCType.GraffitiM},
    {'name': "Graffiti (L - WHOLE SIXER)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - INFINITY)",
        'type': BRCType.GraffitiL},
    #{'name': "Graffiti (L - Dynamo)",
    #    'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - VoodooBoy)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Fang It Up!)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - FREAKS)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Graffo Le Fou)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Lauder)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - SpawningSeason)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Moai Marathon)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Tius)",
        'type': BRCType.GraffitiL},
    #{'name': "Graffiti (L - KANI-BOZU)",
    #    'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - NOISY NINJA)",
        'type': BRCType.GraffitiL},
    #{'name': "Graffiti (L - Dinner On The Court)",
    #    'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Campaign Trail)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - skate or di3)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Jd Vila Formosa)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Messenger Mural)",
        'type': BRCType.GraffitiL},
    #{'name': "Graffiti (L - Solstice Script)",
    #    'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - RECORD.HEAD)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - Boom)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - wild rush)",
        'type': BRCType.GraffitiL},
    {'name': "Graffiti (L - buttercup)",
        'type': BRCType.GraffitiL},
    #{'name': "Graffiti (L - DIGITAL BLOCKBUSTER)",
    #    'type': BRCType.GraffitiL},
    {'name': "Graffiti (XL - Gold Rush)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - WILD STRUXXA)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - VIBRATIONS)",
        'type': BRCType.GraffitiXL},
    #{'name': "Graffiti (XL - Bevel)",
    #    'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - SECOND SIGHT)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Bomb Croc)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - FATE)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Web Spitter)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - MOTORCYCLE GANG)",
        'type': BRCType.GraffitiXL},
    #{'name': "Graffiti (XL - CYBER TENGU)",
    #    'type': BRCType.GraffitiXL},
    #{'name': "Graffiti (XL - Don't Screw Around)",
    #    'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Deep Dive)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - MegaHood)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Gamex UPA ABL)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - BiGSHiNYBoMB)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Bomb Burner)",
        'type': BRCType.GraffitiXL},
    #{'name': "Graffiti (XL - Astrological Augury)",
    #    'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Pirate's Life 4 Me)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Bombing by FireMan)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - end 2 end)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - Raver Funk)",
        'type': BRCType.GraffitiXL},
    {'name': "Graffiti (XL - headphones on Helmet on)",
        'type': BRCType.GraffitiXL},
    #{'name': "Graffiti (XL - HIGH TECH WS)",
    #    'type': BRCType.GraffitiXL},

    # Skateboards
    {'name': "Skateboard (Devon)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Terrence)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Maceo)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Lazer Accuracy)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Death Boogie)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Sylk)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Taiga)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Just Swell)",
        'type': BRCType.Skateboard},
    {'name': "Skateboard (Mantra)",
        'type': BRCType.Skateboard},

    # Inline Skates
    {'name': "Inline Skates (Glaciers)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Sweet Royale)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Strawberry Missiles)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Ice Cold Killers)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Red Industry)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Mech Adversary)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Orange Blasters)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (ck)",
        'type': BRCType.InlineSkates},
    {'name': "Inline Skates (Sharpshooters)",
        'type': BRCType.InlineSkates},

    # BMX
    {'name': "BMX (Mr. Taupe)",
        'type': BRCType.BMX},
    {'name': "BMX (Gum)",
        'type': BRCType.BMX},
    {'name': "BMX (Steel Wheeler)",
        'type': BRCType.BMX},
    {'name': "BMX (oyo)",
        'type': BRCType.BMX},
    {'name': "BMX (Rigid No.6)",
        'type': BRCType.BMX},
    {'name': "BMX (Ceremony)",
        'type': BRCType.BMX},
    {'name': "BMX (XXX)",
        'type': BRCType.BMX},
    {'name': "BMX (Terrazza)",
        'type': BRCType.BMX},
    {'name': "BMX (Dedication)",
        'type': BRCType.BMX},

    # Outfits
    {'name': "Outfit (Red - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Red - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Tryce - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Tryce - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Bel - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Bel - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Vinyl - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Vinyl - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Solace - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Solace - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Felix - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Felix - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Rave - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Rave - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Mesh - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Mesh - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Shine - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Shine - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Rise - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Rise - Winter)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Coil - Autumn)",
        'type': BRCType.Outfit},
    {'name': "Outfit (Coil - Winter)",
        'type': BRCType.Outfit},

    # Characters
    {'name': "Tryce",
        'type': BRCType.Character},
    {'name': "Bel",
        'type': BRCType.Character},
    {'name': "Vinyl",
        'type': BRCType.Character},
    {'name': "Solace",
        'type': BRCType.Character},
    {'name': "Rave",
        'type': BRCType.Character},
    {'name': "Mesh",
        'type': BRCType.Character},
    {'name': "Shine",
        'type': BRCType.Character},
    {'name': "Rise",
        'type': BRCType.Character},
    {'name': "Coil",
        'type': BRCType.Character},
    {'name': "Frank",
        'type': BRCType.Character},
    {'name': "Rietveld",
        'type': BRCType.Character},
    {'name': "DJ Cyber",
        'type': BRCType.Character},
    {'name': "Eclipse",
        'type': BRCType.Character},
    {'name': "DOT.EXE",
        'type': BRCType.Character},
    {'name': "Devil Theory",
        'type': BRCType.Character},
    {'name': "Flesh Prince",
        'type': BRCType.Character},
    {'name': "Futurism",
        'type': BRCType.Character},
    {'name': "Oldhead",
        'type': BRCType.Character},

    # REP
    {'name': "8 REP",
        'type': BRCType.REP},
    {'name': "16 REP",
        'type': BRCType.REP},
    {'name': "24 REP",
        'type': BRCType.REP},
    {'name': "32 REP",
        'type': BRCType.REP},
    {'name': "48 REP",
        'type': BRCType.REP},

    # App
    {'name': "Camera App",
        'type': BRCType.Camera}
]


group_table: Dict[str, Set[str]] = {
    "graffitim": {"Graffiti (M - OVERWHELMME)",
                  "Graffiti (M - QUICK BING)",
                  "Graffiti (M - BLOCKY)",
                  "Graffiti (M - Pora)",
                  "Graffiti (M - Teddy 4)",
                  "Graffiti (M - BOMB BEATS)",
                  "Graffiti (M - SPRAYTANICPANIC!)",
                  "Graffiti (M - SHOGUN)",
                  "Graffiti (M - TeleBinge)",
                  "Graffiti (M - 0m33)",
                  "Graffiti (M - Vom'B)",
                  "Graffiti (M - Street classic)",
                  "Graffiti (M - Thick Candy)",
                  "Graffiti (M - colorBOMB)",
                  "Graffiti (M - Zona Leste)",
                  "Graffiti (M - Stacked Symbols)",
                  "Graffiti (M - B-boy Love)",
                  "Graffiti (M - Devil 68)",
                  "Graffiti (M - pico pow)"},
    "graffitil": {"Graffiti (L - WHOLE SIXER)",
                  "Graffiti (L - INFINITY)",
                  "Graffiti (L - VoodooBoy)",
                  "Graffiti (L - Fang It Up!)",
                  "Graffiti (L - FREAKS)",
                  "Graffiti (L - Graffo Le Fou)",
                  "Graffiti (L - Lauder)",
                  "Graffiti (L - SpawningSeason)",
                  "Graffiti (L - Moai Marathon)",
                  "Graffiti (L - Tius)",
                  "Graffiti (L - NOISY NINJA)",
                  "Graffiti (L - Campaign Trail)",
                  "Graffiti (L - skate or di3)",
                  "Graffiti (L - Jd Vila Formosa)",
                  "Graffiti (L - Messenger Mural)",
                  "Graffiti (L - RECORD.HEAD)",
                  "Graffiti (L - Boom)",
                  "Graffiti (L - wild rush)",
                  "Graffiti (L - buttercup)"},
    "graffitixl": {"Graffiti (XL - Gold Rush)",
                   "Graffiti (XL - WILD STRUXXA)",
                   "Graffiti (XL - VIBRATIONS)",
                   "Graffiti (XL - SECOND SIGHT)",
                   "Graffiti (XL - Bomb Croc)",
                   "Graffiti (XL - FATE)",
                   "Graffiti (XL - Web Spitter)",
                   "Graffiti (XL - MOTORCYCLE GANG)",
                   "Graffiti (XL - Deep Dive)",
                   "Graffiti (XL - MegaHood)",
                   "Graffiti (XL - Gamex UPA ABL)",
                   "Graffiti (XL - BiGSHiNYBoMB)",
                   "Graffiti (XL - Bomb Burner)",
                   "Graffiti (XL - Pirate's Life 4 Me)",
                   "Graffiti (XL - Bombing by FireMan)",
                   "Graffiti (XL - end 2 end)",
                   "Graffiti (XL - Raver Funk)",
                   "Graffiti (XL - headphones on Helmet on)"},
    "skateboard": {"Skateboard (Devon)",
                   "Skateboard (Terrence)",
                   "Skateboard (Maceo)",
                   "Skateboard (Lazer Accuracy)",
                   "Skateboard (Death Boogie)",
                   "Skateboard (Sylk)",
                   "Skateboard (Taiga)",
                   "Skateboard (Just Swell)",
                   "Skateboard (Mantra)"},
    "inline skates": {"Inline Skates (Glaciers)",
                      "Inline Skates (Sweet Royale)",
                      "Inline Skates (Strawberry Missiles)",
                      "Inline Skates (Ice Cold Killers)",
                      "Inline Skates (Red Industry)",
                      "Inline Skates (Mech Adversary)",
                      "Inline Skates (Orange Blasters)",
                      "Inline Skates (ck)",
                      "Inline Skates (Sharpshooters)"},
    "skates": {"Inline Skates (Glaciers)",
               "Inline Skates (Sweet Royale)",
               "Inline Skates (Strawberry Missiles)",
               "Inline Skates (Ice Cold Killers)",
               "Inline Skates (Red Industry)",
               "Inline Skates (Mech Adversary)",
               "Inline Skates (Orange Blasters)",
               "Inline Skates (ck)",
               "Inline Skates (Sharpshooters)"},
    "inline": {"Inline Skates (Glaciers)",
               "Inline Skates (Sweet Royale)",
               "Inline Skates (Strawberry Missiles)",
               "Inline Skates (Ice Cold Killers)",
               "Inline Skates (Red Industry)",
               "Inline Skates (Mech Adversary)",
               "Inline Skates (Orange Blasters)",
               "Inline Skates (ck)",
               "Inline Skates (Sharpshooters)"},
    "bmx": {"BMX (Mr. Taupe)",
            "BMX (Gum)",
            "BMX (Steel Wheeler)",
            "BMX (oyo)",
            "BMX (Rigid No.6)",
            "BMX (Ceremony)",
            "BMX (XXX)",
            "BMX (Terrazza)",
            "BMX (Dedication)"},
    "bike": {"BMX (Mr. Taupe)",
             "BMX (Gum)",
             "BMX (Steel Wheeler)",
             "BMX (oyo)",
             "BMX (Rigid No.6)",
             "BMX (Ceremony)",
             "BMX (XXX)",
             "BMX (Terrazza)",
             "BMX (Dedication)"},
    "bicycle": {"BMX (Mr. Taupe)",
                "BMX (Gum)",
                "BMX (Steel Wheeler)",
                "BMX (oyo)",
                "BMX (Rigid No.6)",
                "BMX (Ceremony)",
                "BMX (XXX)",
                "BMX (Terrazza)",
                "BMX (Dedication)"},
    "characters": {"Tryce",
                   "Bel",
                   "Vinyl",
                   "Solace",
                   "Rave",
                   "Mesh",
                   "Shine",
                   "Rise",
                   "Coil",
                   "Frank",
                   "Rietveld",
                   "DJ Cyber",
                   "Eclipse",
                   "DOT.EXE",
                   "Devil Theory",
                   "Flesh Prince",
                   "Futurism",
                   "Oldhead"},
    "girl": {"Bel",
             "Vinyl",
             "Rave",
             "Shine",
             "Rise",
             "Futurism"}
}