import sys
from typing import Any
from jinja2 import Template
from inspect import cleandoc
import pkgutil
import yaml
from Options import Range
from worlds.LauncherComponents import Component, components, Type, icon_paths
from Utils import is_kivy_running, local_path, is_frozen, open_file, get_all_causes
from settings import get_settings
from Generate import read_weights_yamls
import logging
import os

def main(*cli_args):
    from worlds import AutoWorldRegister
    import argparse
    import atexit

    parser = argparse.ArgumentParser(description="Generate DeathLink Meta.yaml", usage="[-h] [--skip_open_folder] [--only_player_yamls]")
    parser.add_argument("--skip_open_folder", action="store_true")
    parser.add_argument("--only_player_yamls", action="store_true")
    args = parser.parse_args(cli_args)

    atexit.register(input, "Press enter to close.")

    settings = get_settings()
    valid_games: set[str] = set()
    if args.only_player_yamls:
        player_files_path = settings.generator.player_files_path
        for file in os.scandir(player_files_path):
            fname = file.name
            if file.is_file() and not fname.startswith(".") and not fname.lower().endswith(".ini") and \
                    os.path.join(player_files_path, fname) not in {settings.generator.meta_file_path}:
                path = os.path.join(player_files_path, fname)
                try:
                    for doc_idx, yaml_data in enumerate(read_weights_yamls(path)):
                        if yaml_data is None:
                            logging.warning(f"Ignoring empty yaml document #{doc_idx + 1} in {fname}")
                        else:
                            if "game" not in yaml_data:
                                logging.error(f"Missing game value in document {doc_idx} in {fname}")
                            elif isinstance(yaml_data["game"], str):
                                valid_games.add(yaml_data["game"])
                            elif isinstance(yaml_data["game"], dict):
                                valid_games.update(set(yaml_data["game"].keys()))
                except Exception as e:
                    logging.exception(f"Exception reading weights in file {fname}")
                    logging.exception(
                        f"File {fname} is invalid. Please fix your yaml.\n{get_all_causes(e)}"
                    )
    else:
        valid_games.update(set(AutoWorldRegister.world_types.keys()))

    def dictify_range(option: Range, option_val: int | str):
        data = {option_val: 50}
        for sub_option in ["random", "random-low", "random-high",
                           f"random-range-{option.range_start}-{option.range_end}"]:
            if sub_option != option_val:
                data[sub_option] = 0
        notes = {
            "random-low": "random value weighted towards lower values",
            "random-high": "random value weighted towards higher values",
            f"random-range-{option.range_start}-{option.range_end}": f"random value between "
                                                                     f"{option.range_start} and {option.range_end}"
        }
        for name, number in getattr(option, "special_range_names", {}).items():
            notes[name] = f"equivalent to {number}"
            if number in data:
                data[name] = data[number]
                del data[number]
            elif name in data:
                pass
            else:
                data[name] = 0

        return data, notes

    def yaml_dump_scalar(scalar) -> str:
        # yaml dump may add end of document marker and newlines.
        return yaml.dump(scalar).replace("...\n", "").strip()

    games: dict[str, dict[str, Any]] = {}
    for game_name, world in AutoWorldRegister.world_types.items():
        if not world.hidden and game_name in valid_games:
            link_options: dict[str, Any] = {}
            for option_name, option in world.options_dataclass.type_hints.items():
                if "death" in option_name.lower() and "link" in option_name.lower():
                    link_options[option_name] = option
            if link_options:
                games[game_name] = link_options

    template_data = pkgutil.get_data(__name__, "meta_deathlink_template.yaml").decode()
    template = Template(template_data)
    output_data: str = template.render(
        games=games,
        yaml_dump=yaml_dump_scalar,
        dictify_range=dictify_range,
        cleandoc=cleandoc)
    output_path = os.path.join(settings.general_options.output_path, "meta.yaml")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(output_data)
    if not args.skip_open_folder:
        open_file(output_path)

def run_cli(*cli_args):
    if not is_kivy_running():
        main(*cli_args)
        return
    from Launcher import launch as launch_exe
    from worlds.LauncherComponents import get_exe
    if not is_frozen():
        launcher = get_exe("Launcher")
    else:
        launcher = [local_path("ArchipelagoLauncherDebug.exe")]
    if launcher is None:
        raise RuntimeError("Cannot find launcher exe")
    launch_command = [*launcher, "DeathLink Meta.yaml Generator", *cli_args]
    launch_exe(launch_command, in_terminal=True)


components.append(Component("DeathLink Meta.yaml Generator",
                            func=run_cli, component_type=Type.TOOL,
                            description="Create a meta.yaml template that has the DeathLink options for all installed APWorlds."))