# What is this tool?

This tool will create a meta.yaml file for you with the DeathLink-related options for every APWorld you have installed. Specifically, it will pull out every option that has the word `death` and the word `link` in the option name (case-insensitive). As such, it will pick up options like `death_link`, `deathlink`, `DeathLink`, `death_link_amnesty`, `death_link_effect`, etc. This may result in some false positives, but those should be easy enough to spot. The resulting meta.yaml will have a section for each game that has one or more applicable options, with each relevant option displayed as it would be in the template YAML.

# How do I use it?
## The Basic Way

1. Download and install meta_deathlink.apworld from the link below.
2. Open up your AP Launcher, and look for this button, and press it. It should make the meta.yaml in your output folder and open it in whatever your default program is for .yaml files.
<img width="603" height="89" alt="image" src="https://github.com/user-attachments/assets/8c1a98e7-8557-4596-affe-4efe50f70daa" />


## The Advanced Way

This can also be run from CLI, which provides two additional options: `--skip_open_file` will skip opening the generated file at the end of the process, and `--only_player_yamls` will only produce entries for games in the YAMLs in your Players folder. To use the CLI:

1. Download and install meta_deathlink.apworld from the link below.
2. From the command line where you have Archipelago installed, run the Archipelago Launcher with the argument `"DeathLink Meta.yaml Generator"`, followed by ` -- `, followed by the additional arguments you want to use (e.g. on Windows it would be `ArchipelagoLauncher.exe "DeathLink Meta.yaml Generator" -- --only_player_yamls`).