#Crystalis Setup Guide

## Required Software

- Bizhawk: [Bizhawk Releases from TASVideos](https://tasvideos.org/BizHawk/ReleaseHistory)
  - Version 2.7.0 and later are supported.
  - Detailed installation instructions for Bizhawk can be found at the above link.
  - Windows users must run the prereq installer first, which can also be found at the above link.
- The built-in Archipelago client, which can be installed [here](https://github.com/ArchipelagoMW/Archipelago/releases).
- A legally acquired US NES Crystalis ROM (Note: JP's God Slayer is _not_ supported.)

## Configuring Bizhawk

Once Bizhawk has been installed, open Bizhawk and change the following settings:

- **If you are using a version of BizHawk older than 2.9**, you will need to modify the Lua Core.
  Go to Config > Customize. Switch to the Advanced tab, then switch the Lua Core from "NLua+KopiLua" to
  "Lua+LuaInterface". This is required for the Lua script to function correctly.  
  **NOTE:** Even if "Lua+LuaInterface" is already selected, toggle between the two options and reselect it. Fresh installs 
  of newer versions of Bizhawk have a tendency to show "Lua+LuaInterface" as the default selected option but still load 
  "NLua+KopiLua" until this step is done.
- Under Config > Customize > Advanced, make sure the box for AutoSaveRAM is checked, and click the 5s button.
  This reduces the possibility of losing save data in emulator crashes.
- Under Config > Customize, check the "Run in background" and "Accept background input" boxes. This will allow you to
  continue playing in the background, even if another window is selected, such as the Client.
- Under Config > Hotkeys, many hotkeys are listed, with many bound to common keys on the keyboard. You will likely want
  to disable most of these, which you can do quickly using `Esc`.

It is strongly recommended to associate NES rom extensions (\*.nes) to the Bizhawk we've just installed.
To do so, we simply have to search any NES rom we happened to own, right click and select "Open with...", unfold
the list that appears and select the bottom option "Look for another application", then browse to the Bizhawk folder
and select EmuHawk.exe.

## Configuring your YAML file

### What is a YAML file and why do I need one?

Your YAML file contains a set of configuration options which provide the generator with information about how it should
generate your game. Each player of a multiworld will provide their own YAML file. This setup allows each player to enjoy
an experience customized for their taste, and different players in the same multiworld can all have different options.

### Where do I get a YAML file?

You can customize your options by visiting the 
[Crystalis Player Options Page](/games/Crystalis/player-options)

## Joining a MultiWorld Game

### Obtain your .apcrys patch file

When you join a multiworld game, you will be asked to provide your YAML file to whoever is hosting. Once that is done,
the host will provide you with either a link to download your data file, or with a zip file containing everyone's data
files. Your data file should have a `.apcrys` extension.

Go to the [Crystalis Randomizer Archipelago Page](https://crystalisrandomizer.com/ap/) and first click the button that says Select 
Crystalis ROM File, and navigate to your Crystalis.nes ROM in the file selection dialog. Then click on the **Archipelago**
heading that appears, and click on the Select Archipelago Patch File button. Navigate to your .apcrys patch file 
obtained above in the file selection dialog and select it. A Patch heading should appear, with a Patch button beneath
it. Click the Patch button to patch your ROM to the modified version for the multiworld.

### Connect to the Multiserver

Use the Archipelago Launcher to open the BizHawk Client. Then open your patched ROM in BizHawk. In BizHawk, select Tools
from the menu, and under Tools select Lua Console. Click the folder button or press Ctrl+O to open a Lua script. In 
the Open Lua Script file select dialog, to your Archipelago install folder and open 
`data/lua/connector_bizhawk_generic.lua`. You should see a message in the BizHawk Client that says "Running handler for
Crystalis". Once you see that message, you can enter the server URL and port at the top of the client window, press 
Connect, and finally enter your slot name when prompted. You should now successfully be connected to the multiworld and
be ready to start playing.