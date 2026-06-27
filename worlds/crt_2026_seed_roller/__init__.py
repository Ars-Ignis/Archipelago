from tempfile import TemporaryDirectory

from worlds.LauncherComponents import Component, components, Type, icon_paths
from Main import main as create_multiworld
from Generate import main as parse_yamls, mystery_argparse
from Utils import tuplize_version, VersionException, is_kivy_running, local_path, is_frozen, open_file
from Launcher import get_exe, launch as launch_exe
import pkgutil
import tempfile
from settings import get_settings

SIMEA_FILE_NAME = "CRT 2026 - Combat.yaml"
MESIA_FILE_NAME = "CRT 2026 - Exploration.yaml"
MINIMUM_CRYSTALIS_VERSION = tuplize_version("2.0.4")

def main(*cli_args):
    print(cli_args)
    import atexit
    atexit.register(input, "Press enter to close.")
    try:
        from worlds.crystalis.constants import CRYSTALIS_APWORLD_VERSION
        if CRYSTALIS_APWORLD_VERSION.major < MINIMUM_CRYSTALIS_VERSION.major:
            err_string = (f"Insufficient Crystalis APWorld Version. Minimum required version: "
                         f"{MINIMUM_CRYSTALIS_VERSION.as_simple_string()} " 
                         f"Installed version: {CRYSTALIS_APWORLD_VERSION.as_simple_string()}")
            raise VersionException(err_string)
    except ImportError:
        raise Exception("Crystalis APWorld not installed; please install it and restart the launcher, then try again.")
    temp_dir: TemporaryDirectory = tempfile.TemporaryDirectory()
    with temp_dir as player_dir:
        # copy yamls to temporary directory
        simea_temp_file = open(player_dir + "\\" + SIMEA_FILE_NAME, 'wb')
        simea_yaml_contents: bytes = pkgutil.get_data(__name__, SIMEA_FILE_NAME)
        simea_temp_file.write(simea_yaml_contents)
        simea_temp_file.close()
        mesia_temp_file = open(player_dir + "\\" + MESIA_FILE_NAME, 'wb')
        mesia_yaml_contents: bytes = pkgutil.get_data(__name__, MESIA_FILE_NAME)
        mesia_temp_file.write(mesia_yaml_contents)
        mesia_temp_file.close()

        # set up generation settings
        args = mystery_argparse(list(cli_args))
        args.player_files_path = player_dir
        args.spoiler = 0
        args.race = 1
        args.spoiler_only = False
        args.skip_output = False

        # parse yamls for options
        generation_args, seed = parse_yamls(args)

        # get server settings to prebake into generation, and modify accordingly
        baked_server_options = get_settings().server_options.as_dict()
        baked_server_options["password"] = None
        baked_server_options["server_password"] = None
        baked_server_options["disable_item_cheat"] = True
        baked_server_options["hint_cost"] = 1000
        baked_server_options["release_mode"] = "disabled"
        baked_server_options["collect_mode"] = "disabled"
        baked_server_options["remaining_mode"] = "disabled"
        baked_server_options["compatibility"] = 0

        # generate
        multiworld = create_multiworld(generation_args, seed, baked_server_options=baked_server_options)
        if multiworld:
            open_file(args.outputpath)

def run_cli(*args):
    if not is_kivy_running():
        main(*args)
        return

    if not is_frozen():
        launcher = get_exe("Launcher")
    else:
        launcher = [local_path("ArchipelagoLauncherDebug.exe")]
    if launcher is None:
        raise RuntimeError("Cannot find launcher exe")
    launch_command = [*launcher, "Crystalis Randomizer 2026 Tournament Seed Roller", *args]
    launch_exe(launch_command, in_terminal=True)


components.append(Component("Crystalis Randomizer 2026 Tournament Seed Roller",
                            func=run_cli, component_type=Type.TOOL, icon='crystalis',
                            description="Press button, get tournament seed. Opens the output folder to find the result."))

icon_paths['crystalis'] = "ap:worlds.crt_2026_seed_roller/icon.png"