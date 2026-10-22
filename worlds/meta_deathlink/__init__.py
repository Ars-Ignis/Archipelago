import sys
from typing import Any
from jinja2 import Template
from inspect import cleandoc
import pkgutil
import yaml
from Options import Range
from worlds.LauncherComponents import Component, components, Type, icon_paths
from Utils import is_kivy_running, local_path, is_frozen, open_file
from settings import get_settings
import os

def main(*cli_args):
    import atexit
    atexit.register(input, "Press enter to close.")

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

    from worlds import AutoWorldRegister
    games: dict[str, dict[str, Any]] = {}
    for game_name, world in AutoWorldRegister.world_types.items():
        if not world.hidden:
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
    settings = get_settings()
    output_path = os.path.join(settings.general_options.output_path, "meta.yaml")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.write(output_data)
    open_file(output_path)

def run_cli(*args):
    if not is_kivy_running():
        main(*args)
        return
    from Launcher import launch as launch_exe
    from worlds.LauncherComponents import get_exe
    if not is_frozen():
        launcher = get_exe("Launcher")
    else:
        launcher = [local_path("ArchipelagoLauncherDebug.exe")]
    if launcher is None:
        raise RuntimeError("Cannot find launcher exe")
    launch_command = [*launcher, "DeathLink Meta.yaml Generator", *args]
    launch_exe(launch_command, in_terminal=True)


components.append(Component("DeathLink Meta.yaml Generator",
                            func=run_cli, component_type=Type.TOOL,
                            description="Create a meta.yaml template that has the DeathLink options for all installed APWorlds."))