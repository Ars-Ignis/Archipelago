import os
import orjson
import zipfile
from typing import Dict, List, Any
from worlds.Files import APPatch
from .items import items_data
from .options import CrystalisOptions
from .regions import regions_data
from .types import CrystalisRegionData, CrystalisShuffleData, CrystalisElementEnum, convert_text_to_elem_enum


boss_ids: Dict[str, int] = {
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


def generate_flag_string(options: CrystalisOptions) -> str:
    flag_dict: Dict[str, List[str]] = {}
    #this feels cursed? maybe I'm just not used to langauges with good reflection lmao
    for attr in dir(options):
        option = getattr(options, attr)
        if hasattr(option, "flag_name"):
            cat, flag = option.flag_name()
            if cat != "":
                if cat not in flag_dict.keys():
                    flag_dict[cat] = [flag]
                else:
                    flag_dict[cat].append(flag)
    flag_string: str = ""
    for cat, flags in flag_dict.items():
        cat_string: str = cat
        bang_string: str = ""
        for flag in flags:
            if flag.startswith("!"):
                bang_string = bang_string + flag.strip("!")
            else:
                cat_string = cat_string + flag
        flag_string = flag_string + cat_string + (("!" + bang_string) if bang_string != "" else "")
    return flag_string


def convert_shuffle_data(shuffle_data: CrystalisShuffleData) -> Dict[str, Any]:
    wall_map: Dict[str, int] = {}
    for wall, elem in shuffle_data.wall_map.items():
        elem_enum = convert_text_to_elem_enum(elem)
        wall_map[wall] = elem_enum.value
    key_item_names: Dict[str, str] = shuffle_data.key_item_names
    trade_in_map: Dict[str, str] = {}
    for recipient, trade in shuffle_data.trade_in_map.items():
        if recipient != "Rage" and recipient != "Tornel":
            trade_in_map[trade] = recipient
    tornel_trade: int = convert_text_to_elem_enum(shuffle_data.trade_in_map["Tornel"]).value * 2 + 6
    rage_trade: int = items_data[shuffle_data.trade_in_map["Rage"]].rom_id
    boss_weaknesses: Dict[str, int] = {}
    for boss, weakness in shuffle_data.boss_reqs.items():
        boss_id = boss_ids[boss]
        if boss == "Giant Insect" or boss == "Vampire 2":
            boss_weaknesses[str(boss_id)] = 1 << convert_text_to_elem_enum(weakness).value
        else:
            boss_weaknesses[str(boss_id)] = ~(1 << convert_text_to_elem_enum(weakness).value) & 15
    gbc_cave_exits: List[int]
    if len(shuffle_data.gbc_cave_exits) >= 2:
        possible_gbc_cave_exits: List[str] = ["Cordel Plains - Main", "Lime Valley", "Goa Valley", "Desert 2"]
        gbc_cave_exits = [
            possible_gbc_cave_exits.index(shuffle_data.gbc_cave_exits[0]),
            possible_gbc_cave_exits.index(shuffle_data.gbc_cave_exits[1])
        ]
    else:
        gbc_cave_exits = []
    shop_inventories: Dict[str, List[int]] = {}
    for shop, inventory in shuffle_data.shop_inventories.items():
        inv_ids: List[int] = []
        for stock in inventory:
            inv_ids.append(items_data[stock].rom_id)
        shop_inventories[str(regions_data[shop].wildwarpIds[0])] = inv_ids
    thunder_warp: int
    if shuffle_data.thunder_warp is not None:
        thunder_warp = regions_data[shuffle_data.thunder_warp].wildwarpIds[0]
    else:
        thunder_warp = -1

    output: Dict[str, Any] = {
        "wall_map": wall_map,
        "key_item_names": key_item_names,
        "trade_in_map": trade_in_map,
        "tornel_trade": tornel_trade,
        "rage_trade": rage_trade,
        "boss_weaknesses": boss_weaknesses,
        "gbc_cave_exits": gbc_cave_exits,
        "shop_inventories": shop_inventories,
        "thunder_warp": thunder_warp,
        "wildwarps": shuffle_data.wildwarps
    }
    return output


def generate_output(self, output_directory: str) -> None:
    flag_string: str = generate_flag_string(self.options)
    #need to convert shuffle_data to the format it will be consumed in
    converted_data = convert_shuffle_data(self.shuffle_data)
    output_dict = {
        "seed": self.multiworld.seed_name,
        "flag_string": flag_string,
        "shuffle_data": converted_data
    }
    file_path = os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}.apcrys")
    ap_crys = CrystalisFile(file_path, player=self.player, player_name=self.multiworld.player_name[self.player])
    with zipfile.ZipFile(file_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        json_output = orjson.dumps(output_dict, option=orjson.OPT_INDENT_2)
        zf.writestr("patch_data.json", json_output)
        ap_crys.write_contents(zf)


class CrystalisFile(APPatch):
    game = "Crystalis"


    def get_manifest(self):
        manifest = super().get_manifest()
        manifest["patch_file_ending"] = ".apcrys"
        return manifest
