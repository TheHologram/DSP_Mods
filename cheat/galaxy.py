################################################
#
# Galaxy Screen
#
#  Installation:
#   * Copy this file to <game>\Plugins\Console\Lib\
#   * Start Game
#   * Use Ctrl+` (Ctrl+BackTick) to open console
#   * Type: 
#     >>> import cheat
#     >>> cheat.showWindow()
#   
#     >>> import shortcuts, gui, screens, dsp
#     >>> reload(shortcuts); reload(gui); reload(screens); reload(dsp); dsp.showWindow(reset=True); _console.Clear()
################################################
from __future__ import print_function
from gui import *
from shortcuts import ShortcutManager, ShortcutHandler

def showWindow(visible=True, reset=False):
    import unity_util
    import UnityEngine
    import os, sys, math
    from UnityEngine import GUI, GUILayout, GUIStyle, GUIUtility, Screen, Rect, Vector2, Vector3, Input, KeyCode, GUISkin, Font, Color
    from UnityEngine import Event, EventType, WaitForSeconds, GameObject, GUILayoutOption, GUIContent
    from System.Reflection import BindingFlags
    import System
    
    import UIGalaxySelect, GalaxyData, StarData, PlanetData, LDB, GameMain, StringBuilderUtility
    import EPlanetType
    
    # clean up previous window if still running
    #  TODO: this is a hack to use global variable but doesn't interfere with other mods
    global _galaxyObject
    try:
        if _galaxyObject != None:
            UnityEngine.Object.DestroyObject(_galaxyObject.gameObject)            
    except NameError:
        _galaxyObject = None
        
        
    #TODO: dangerous with other mods.  blasts everything to dust
    #unity_util.clean_behaviors()

    class Controller():
        def __init__(self):
            import screens
            self.gameObject = None  # will be assigned if exists as member
            self.component = None  # will be assigned if exists as member
            
            self.gui = getGlobalGUIState(True)
            self.width = Screen.width - 450
            self.height = Screen.height - 400 - 200
            
            self.windowRect = Rect(50, 400, self.width, self.height)
            self.tooltipRect = Rect(Screen.width - 400, Screen.height-500, 400, 400)
            self.drawPanelRect = Rect(0, 0, self.width, 50)
            
            self.lasterror = None
            self.lasttooltip = None
            modulename = os.path.join(os.path.dirname(__file__), 'cheat')            
            sysSettings = getSystemSettings(modulename)
            self.sysSettings = sysSettings
            
            self.buffer = System.Text.StringBuilder(4096)
            self.starcache = []
            self.valuecache = []
            self.ores = []
            self.seedcache = None
            
            self.itembox = ScrollView(height=self.height - 50, width=self.width)

            def FuncPanelGUI(windowid):
                try:
                    self.MainPanel()
                    if Event.current.type == EventType.Repaint:
                        self.lasttooltip = str(GUI.tooltip) if GUI.tooltip else None
                    self.lasterror = None
                except Exception, e:
                    error = "Error: " + str(e)
                    if error != self.lasterror:
                        self.lasterror = error
                        print(error)
                    GUILayout.Label(error)
                        
                self.timerPass = False
                GUI.DragWindow(self.drawPanelRect)

            def TooltipGUI(windowid):
                try:
                    if self.lasttooltip:
                        ShowTooltipWindow(self.lasttooltip, self.tooltipRect)
                except Exception, e:
                    GUILayout.Label(str(e))
                GUI.DragWindow(self.tooltipRect)

            def InitFuncPanelGUI(windowid):
                """Initialize State: This is called only once"""
                # Actually lets hold off until it is actually completely running
                try:
                    if self.gameObject:
                        UnityEngine.Object.DontDestroyOnLoad(self.gameObject)

                    overrideFont = sysSettings.FontBase or sysSettings.FontBaseDelta or sysSettings.DynamicFont
                    fontsize = sysSettings.FontBase if sysSettings.FontBase else GUI.skin.font.fontSize
                    if sysSettings.DynamicFont:
                        fontsize = max(12, Screen.height / 100 * 4 / 3)
                        sysSettings.FontBase = fontsize
                        overrideFont = True
                    if sysSettings.FontBaseDelta:
                        fontsize += sysSettings.FontBaseDelta
                        sysSettings.FontBase = fontsize
                        sysSettings.FontBaseDelta = 0

                    if overrideFont:
                        GUI.skin.font = Font( GUI.skin.font.fontNames, fontsize)
                    guistate = self.gui
                    guistate.tinyskin = CloneSkin(GUI.skin)
                    guistate.tinyskin.font = Font( guistate.tinyskin.font.fontNames, guistate.tinyskin.font.fontSize + sysSettings.FontSmaller )
                    guistate.smallskin = CloneSkin(GUI.skin)
                    guistate.smallskin.font = Font( GUI.skin.font.fontNames, GUI.skin.font.fontSize + sysSettings.FontSmall)
                                        
                    # have to have at least one control
                    #GUILayout.Label('')
                except Exception, e:
                    self.PrintError(e)

                # switch gui call to main function
                self.windowCallback = GUI.WindowFunction(FuncPanelGUI)
                FuncPanelGUI(windowid)

            self.windowCallback = GUI.WindowFunction(InitFuncPanelGUI)
            self.tooltipCallback = GUI.WindowFunction(TooltipGUI)

        def PrintError(self, e):
            error = "Error: " + str(e)
            if error != self.lasterror:
                self.lasterror = error
                print(error)
            GUILayout.Label(error)

        def GetGalaxy(self):
            select = UnityEngine.Object.FindObjectOfType[UIGalaxySelect]()
            return GameMain.galaxy if select == None else select.starmap.galaxyData
        
        def WriteKMG(self, value):
            self.buffer.Append(' ', 7)
            StringBuilderUtility.WriteKMG(self.buffer, 6, value, True)
            return self.buffer.ToString()
            #return str(value)
            
        def MainPanel(self):
            galaxyData = self.GetGalaxy()
            if self.seedcache != galaxyData.seed:
                self.seedcache = galaxyData.seed
                self.selectedstar = -1
                self.ores = [LDB.items.Select(x.MiningItem) for x in LDB.veins]
                self.starcache = [ Expando() for x in range(galaxyData.starCount) ]
                self.itemlist = self.starcache
                for i, cache in enumerate(self.starcache):
                    star = galaxyData.stars[i]
                    cache.showtoggle = False
                    cache.toggled = False
                    cache.star = star
                    cache.starloaded = -1
                    cache.values = ['']*len(self.ores)
                    cache.tooltip = star.name 
                    cache.name = "%s (?)"%star.name
                    cache.planets = [ ]
                    cache.color = Color.grey
            for i, cache in enumerate(self.starcache):
                starloaded = cache.star.loaded
                if starloaded and cache.starloaded <= 0:
                    cache.values = [self.WriteKMG(cache.star.GetResourceAmount(i+1)) for i, vein in enumerate(self.ores)]
                    cache.starloaded = 1
                    cache.showtoggle = True
                    cache.color = Color.white
                    tooltip = cache.star.name
                    cache.name = "%s (%s)"%(cache.star.name, str(cache.star.planetCount) )
                    cache.planets = [ Expando() for x in range(cache.star.planetCount) ]
                    for j, pcache in enumerate(cache.planets):
                        planet = cache.star.planets[j]
                        pcache.showtoggle = False
                        pcache.name = planet.displayName
                        pcache.tooltip = planet.displayName
                        pcache.color = Color.grey
                        if planet.orbitAroundPlanet != None:
                            pcache.tooltip += " (Moon of %s)"%(planet.orbitAroundPlanet.displayName)
                            pcache.name += ' (Moon)'
                            
                        tooltip += '\r\n ' + pcache.tooltip
                        if planet.type != EPlanetType.Gas:
                            pcache.values = [ self.WriteKMG(planet.veinAmounts[i+1]) for i, vein in enumerate(self.ores) ]
                        else:
                            pcache.values = ['']*len(self.ores)
                            
                        pcache.tooltip += '\r\nType: \t\t' + planet.typeString
                        pcache.tooltip += '\r\nOrbit Radius: \t%.2f AU'%planet.orbitRadius
                        pcache.tooltip += '\r\nOrbit Period: \t%.2f'%planet.orbitalPeriod
                        pcache.tooltip += '\r\nOrbit Rotate: \t%.2f'%planet.rotationPeriod
                        pcache.tooltip += '\r\nOrbit Incline: \t%.2f'%planet.orbitInclination                        
                        
                        water = LDB.items.Select(planet.waterItemId)
                        if water != None: 
                            pcache.tooltip += '\r\nOceans: \t\t' + water.name
                        pcache.tooltip += '\r\nLand: \t\t%.1f %%'%(planet.landPercent*100.0)
                        pcache.tooltip += '\r\nWind: \t\t%.0f'%(planet.windStrength*100.0)
                        pcache.tooltip += '\r\nLuminosity:\t%.0f'%(planet.luminosity*100.0)
                        if planet.gasItems:
                            for k, gas in enumerate(planet.gasItems):
                                proto = LDB.items.Select(gas)
                                pcache.tooltip += '\r\n%-10s\t%.2f'%(proto.name+':', planet.gasSpeeds[k])
                        
                    tooltip += '\r\n'
                    tooltip += '\r\nLuminosity:\t%.0f L'%(cache.star.luminosity*100.0)
                    tooltip += '\r\nMass:\t\t%.3f M'%(cache.star.mass)
                    tooltip += '\r\nTemperature:\t%.0f K'%(cache.star.temperature)
                    tooltip += '\r\nSpectral Class:\t%s'%(cache.star.spectr)
                    tooltip += '\r\nRadius:\t\t%.2f R'%(cache.star.radius)
                        
                    cache.tooltip = tooltip
                    
                if not starloaded and cache.starloaded < 0:
                    cache.starloaded = 0
                    cache.star.Load()
                    break

            with VerticalScope("Galaxy Seed: %d"%(galaxyData.seed), self.gui.tinyskin.window):
                with GUILayout.HorizontalScope():
                    GUILayout.Label('')                    
                    options = System.Array[GUILayoutOption]([GUILayout.ExpandWidth(True), GUILayout.MaxWidth(30)])
                    if GUILayout.Button("X", options):
                        if self.gameObject:
                            UnityEngine.Object.DestroyObject(self.gameObject)
                            _galaxyObject = None
                
                with GUISkinScope(self.gui.smallskin):
                    labeloptions = System.Array[GUILayoutOption]([GUILayout.MaxWidth(300)])
                    itemwidth = (self.width - 400 - 50) / LDB.veins.Length
                    options = System.Array[GUILayoutOption]([GUILayout.MaxWidth(itemwidth)])
                    
                    with HorizontalScope():
                        GUILayout.Label('Stars')
                        GUILayout.FlexibleSpace()
                        for proto in self.ores: 
                            tooltip = proto.name + "\r\n\r\n" + proto.description
                            GUILayout.Label(GUIContent(proto.iconSprite.texture, tooltip), options)
                                
                    def render(cache):
                        name = cache.name
                        tooltip = cache.tooltip
                        color = cache.color
                        with ColorScope(color):
                            with HorizontalScope():
                                if cache.showtoggle:
                                    prev = cache.toggled
                                    Toggle(cache,'toggled', GUIContent(name, tooltip))
                                    if prev != cache.toggled:
                                        itemlist = []
                                        for x in self.starcache:
                                            itemlist.append(x)
                                            if x.toggled: itemlist.extend(x.planets)
                                        self.itemlist = itemlist
                                else:
                                    GUILayout.Label('   ')
                                    GUILayout.Label(GUIContent(name, tooltip))
                                GUILayout.FlexibleSpace()
                                for i, vein in enumerate(self.ores):
                                    GUILayout.Label(cache.values[i], options)
                                
                    self.itembox.Update(items=self.itemlist, render=render)

        # make the game object permanent and not unload when scene changes
        def getGameObject(self):
            return self._gameObject

        def setGameObject(self, value):
            print('GameObject', value)
            if self._gameObject == value:
                return
            from UnityEngine import Object
            if self._gameObject:
                Object.DestroyObject(self._gameObject)
            self._gameObject = value
            if value:
                Object.DontDestroyOnLoad(value)

        def Start(self):
            # self.useGUILayout = True
            pass

        def OnGUI(self):
            try:
                self.windowRect = GUI.Window(0xdeaf, self.windowRect, self.windowCallback, '', GUI.skin.scrollView)
                self.tooltipRect = GUI.Window(0xdeaf+1, self.tooltipRect, self.tooltipCallback, '', GUI.skin.scrollView)
            except Exception, e:
                self.PrintError(e)

    _galaxyObject = unity_util.create_gui_behavior(Controller)
    return _galaxyObject

def onSceneChange():
    import shortcuts, gui, screens, galaxy
    reload(shortcuts); reload(gui); reload(screens); reload(galaxy); 
    galaxy.showWindow(reset=False)

