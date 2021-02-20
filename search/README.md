#Python Cheat Mod for DSP

Python Cheat Mod is example mod for the Python Console for DSP mod.

WARNING: This probably should go without saying but I strongly advise that you backup games before using any Cheat Mods not just this one and generally be careful with them.  Probably use them first in an experimental capacity first before relying on them heavily and making big changes that you cannot recover from if that is possible.

I use the mod myself and do not have these problems but I probably do not do the same things as other people and therefore cannot anticipate all use cases.

NOTE:  It has been noted that this mod may cause performance issues on lower end hardware. I have not notice this
but its be documented in other games.  


---
1. What it does
---

    Python Cheat Mod is example mod for the Python Console for DSP mod
    
    Currently it lets you any item to your Mecha Inventory, edit basic Mecha stats and view galaxy resources
        
---
2. How it works
---
    The mod is loaded by the Python engine in the Console mod and shows a simple UI.
  
---
3. Directory Structure Overview
---

    \BepInEx\
        The root folder managed by BepInEx.  Shared by BepInEx and plugins.
        
    \BepInEx\Console\Mods\
        This folder is the location for python based mods
        
    \BepInEx\Console\Mods\cheats
      This folder is the location for this mod
                   
---
4. Installation
---

    Prerequisites:
      1. Download BepInEx 5 LTS version
         
         BepInEx_x64_5.4.5.0.zip was tested.
           https://github.com/BepInEx/BepInEx/releases/download/v5.4.5/BepInEx_x64_5.4.5.0.zip
           
         The current versions can be downloaded from here:
          https://github.com/BepInEx/BepInEx/releases
          
         More help on BepInEx
          https://github.com/BepInEx/BepInEx/wiki/Installation 
          
      2. Unpack BepInEx to game folder so winhttp.dll is in same folder as DSPGAME.exe
               
      3. Test game still loads before adding console

      4. Download the current version of Python Console for DSP (Unity-Console)
        
      5. Unpack to game folder.  BepInEx folder is already present so extract
         to same folder as DSPGAME.exe
      
      6. Test game still loads before adding console
      
    Installation:
      1. Unpack to game folder.  BepInEx folder is already present so extract
         to same folder as DSPGAME.exe
             
---
5. Usage
---
    
    The mod will appear in the upper right corner of the screen by default.
    
    1. Load a game.
    
    2. Look for Cheat menu on the right.
    
    3. Click on "Show" to right of Items
    
    4. Click on E to open Mecha inventory.
    
    5. Select +1 next to item in menu and see it appear in Mecha Inventory
    
    6. Click Show Galaxy > View to show all resources in current galaxy or galaxy in new game

    
---
6. TODO
---
   
    I'm sure there can be a lot done to improve some basic scripting libraries.
    
---
7. Contact
---

    The code is offered as-is for demonstration purposes.
  
    The author apologizes for not having time to maintain the code but hopes that it is still useful to other users.

    The official homepage:
      https://github.com/TheHologram/unity-console
      https://github.com/TheHologram/DSP_Mods
      
    You can report bugs or other issues at nexus.
        https://www.nexusmods.com/dysonsphereprogram/mods/11
  
---
8. Change log
---

    Version 1.7.3
        Change the dependency to 1.1.2 of python console corrected for r9modman
    Version 1.7.2
        Change the dependency to 1.1.1 of python console corrected for r9modman
    Version 1.7.1
        Rerelease to thunder mods with correct change log
    Version 1.7
        Remove tooltip as it was main trigger for the random error
    Version 1.6
        More fixes for consuming mouse events behind the window
        Restructure the galaxy window to inline the icons to the list so fewer resolution dependent artifacts
    Version 1.5
        Fix bug with mouse blocking script blocking controls that appear below the main window
    Version 1.4
        Fix click through for mouse actions on dialogs
        Add Galaxy screen showing all resources
    Version 1.2
        Add Show Globals (move research to globals) with most of the items from GameHistory
    Version 1.1
        Bug fix for mecha stats not updating
        add max sail and warp speeds
