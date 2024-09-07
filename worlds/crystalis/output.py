import os
import orjson
import zipfile
from typing import Dict, List, Any, Tuple, TextIO
from worlds.Files import APPatch
from .items import items_data
from .options import CrystalisOptions
from .regions import regions_data
from .types import CrystalisRegionData, CrystalisShuffleData, CrystalisElementEnum, convert_text_to_elem_enum


DEBUG: bool = False
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
        boss_id = BOSS_IDS[boss]
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
    if shuffle_data.thunder_warp != '':
        thunder_warp = regions_data[shuffle_data.thunder_warp].wildwarpIds[0]
    else:
        thunder_warp = -1
    goa_floors: List[Tuple[int, bool]] = []
    previous_exit: str = "Goa Entrance - Stairs"
    for i in range(4):
        current_floor_entrance_region_name = shuffle_data.goa_connection_map[previous_exit]
        current_floor_name = current_floor_entrance_region_name.split('\'')[0]
        current_floor_index: int
        if current_floor_name == "Kelbesque":
            current_floor_index = 0
        elif current_floor_name == "Sabera":
            current_floor_index = 1
        elif current_floor_name == "Mado":
            current_floor_index = 2
        elif current_floor_name == "Karmine":
            current_floor_index = 3
        else:
            raise KeyError(f"Unrecognized Goa floor in Goa connection map: {current_floor_name}")
        is_flipped: bool = False
        if current_floor_entrance_region_name.endswith("Back"):
            is_flipped = True
        goa_floors.append((current_floor_index, is_flipped))
        previous_exit = f"{current_floor_name}'s Floor - " + ("Entrance" if is_flipped else "Exit")

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
        "wildwarps": shuffle_data.wildwarps,
        "goa_floors": goa_floors
    }
    return output


def generate_output(self, output_directory: str) -> None:
    if DEBUG:
        # turn this into a test when it's time to write tests
        if self.options.keep_unique_items_and_consumables_separate:
            for location_data in self.locations_data:
                if not location_data.unique:
                    non_unique_location = self.get_location(location_data.name)
                    item = non_unique_location.item
                    if item.player != self.player:
                        raise RuntimeError(f"Non-unique location has another player's item: Location: "
                                           f"{non_unique_location.name} Item: {item.name} Player: {item.player}")
                    else:
                        item_data = items_data[item.name]
                        if item_data.unique:
                            raise RuntimeError(f"Non-unique location has unique item: Location: "
                                               f"{non_unique_location.name} Item: {item.name}")

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


def write_spoiler_header(self, spoiler_handle: TextIO) -> None:
    if self.options.randomize_wall_elements:
        spoiler_handle.write("\nWall Elements:\n")
        for area, element in self.shuffle_data.wall_map.items():
            spoiler_handle.write(f"{area}: {element}\n")
    if self.options.unidentified_key_items:
        spoiler_handle.write("\nKey Item Names:\n")
        for key_item, name in self.shuffle_data.key_item_names.items():
            spoiler_handle.write(f"{key_item}: {name}\n")
    if self.options.randomize_tradeins:
        spoiler_handle.write("\nTrade-Ins:\n")
        for trader, trade_in in self.shuffle_data.trade_in_map.items():
            spoiler_handle.write(f"{trader}: {trade_in}\n")
    if self.options.randomize_monster_weaknesses:
        spoiler_handle.write("\nBoss Weaknesses:\n")
        for boss, weakness in self.shuffle_data.boss_reqs.items():
            if boss == "Giant Insect" or boss == "Vampire 2":
                spoiler_handle.write(f"{boss}: Not {weakness}\n")
            else:
                spoiler_handle.write(f"{boss}: {weakness}\n")
    if self.options.vanilla_maps.value == self.options.vanilla_maps.option_GBC_cave:
        spoiler_handle.write(f"\nGBC Cave Exits: {self.shuffle_data.gbc_cave_exits[0]}, "
                             f"{self.shuffle_data.gbc_cave_exits[1]}\n")
    if self.options.thunder_warp.value == self.options.thunder_warp.option_shuffled:
        spoiler_handle.write(f"\nSword of Thunder Warp: {self.shuffle_data.thunder_warp}\n")
    if not self.options.vanilla_shops:
        spoiler_handle.write("\nShop Inventories:\n")
        for town, inventory in self.shuffle_data.shop_inventories.items():
            spoiler_handle.write(f"{town}: ")
            first = True
            for item in inventory:
                if not first:
                    spoiler_handle.write(", ")
                first = False
                spoiler_handle.write(item)
            spoiler_handle.write("\n")
    if self.options.randomize_wild_warp:
        spoiler_handle.write("\nWild Warps: ")
        first = True
        for warp in self.shuffle_data.wildwarps:
            if not first:
                spoiler_handle.write(", ")
            first = False
            if warp == 0:
                spoiler_handle.write("Mezame Shrine")
            else:
                spoiler_handle.write(self.wild_warp_id_to_region[warp])
        spoiler_handle.write("\n")
    if self.options.shuffle_goa:
        spoiler_handle.write("\nGoa Order: ")
        previous_exit: str = "Goa Entrance - Stairs"
        first = True
        for i in range(4):
            if not first:
                spoiler_handle.write(", ")
            first = False
            current_floor_entrance_region_name = self.shuffle_data.goa_connection_map[previous_exit]
            current_floor_name = current_floor_entrance_region_name.split('\'')[0]
            spoiler_handle.write(current_floor_name)
            if current_floor_entrance_region_name.endswith("Back"):
                spoiler_handle.write(" Flipped")
                previous_exit = f"{current_floor_name}'s Floor - Entrance"
            else:
                previous_exit = f"{current_floor_name}'s Floor - Exit"
        spoiler_handle.write("\n")


class CrystalisFile(APPatch):
    game = "Crystalis"


    def get_manifest(self):
        manifest = super().get_manifest()
        manifest["patch_file_ending"] = ".apcrys"
        return manifest
