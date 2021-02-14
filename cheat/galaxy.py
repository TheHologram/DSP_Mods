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

def WriteKMG(value):
    import StringBuilderUtility
    buffer = System.Text.StringBuilder(8)
    buffer.Append(' ', 7)
    StringBuilderUtility.WriteKMG(buffer, 6, value, True)
    return buffer.ToString()

def showWindow(visible=True, reset=False):
    import unity_util
    import UnityEngine
    import os, sys, math
    from UnityEngine import GUI, GUILayout, GUIStyle, GUIUtility, Screen, Rect, Vector2, Vector3, Input, KeyCode, GUISkin, Font, Color
    from UnityEngine import Event, EventType, WaitForSeconds, GameObject, GUILayoutOption, GUIContent
    from System.Reflection import BindingFlags
    import System
    
    import UIGalaxySelect, GalaxyData, StarData, PlanetData, LDB, GameMain, StringBuilderUtility
    import EPlanetType, PlanetModelingManager
    
    # clean up previous window if still running
    #  TODO: this is a hack to use global variable but doesn't interfere with other mods
    global _galaxyObject
    try:
        if _galaxyObject != None:
            UnityEngine.Object.DestroyObject(_galaxyObject.gameObject)            
    except NameError:
        _galaxyObject = None
        
    crlf = '\r\n'
    #TODO: dangerous with other mods.  blasts everything to dust
    #unity_util.clean_behaviors()

    class Controller():
        def __init__(self):
            import screens
            self.gameObject = None  # will be assigned if exists as member
            self.component = None  # will be assigned if exists as member
            
            self.gui = getGlobalGUIState(True)
            self.width = Screen.width * 4 / 5
            if self.width < (69*16): # 14 icons + text
                self.width = Screen.width
                
            self.height = Screen.height * 4 / 5
            
            self.windowRect = Rect(min(50,(Screen.width-self.width)/2), min(50,(Screen.height-self.height)/2) , self.width, self.height)
            self.tooltipRect = Rect(Screen.width - 400, Screen.height-300, 400, 300)
            self.drawPanelRect = Rect(0, 0, self.width, 50)
            
            self.lasterror = None
            self.lasttooltip = None
            modulename = os.path.join(os.path.dirname(__file__), 'cheat')            
            sysSettings = getSystemSettings(modulename)
            self.sysSettings = sysSettings
            
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
        
            #return str(value)
            
        def MainPanel(self):
            galaxyData = self.GetGalaxy()
            if self.seedcache != galaxyData.seed:
                self.seedcache = galaxyData.seed
                self.selectedstar = -1
                self.ores = [LDB.items.Select(x.MiningItem) for x in LDB.veins]
                self.starcache = [ Expando() for x in range(galaxyData.starCount) ]
                self.itemlist = [None] # placeholder for header
                self.itemlist.extend(self.starcache)
                
                for i, cache in enumerate(self.starcache):
                    star = galaxyData.stars[i]
                    cache.showtoggle = False
                    cache.toggled = False
                    cache.star = star
                    cache.starloaded = -1
                    cache.values = ['']*len(self.ores)
                    cache.tooltip = star.name 
                    cache.name = "%s (%s)"%(star.name, star.planetCount)
                    cache.planets = [ ]
                    cache.color = Color.grey

                # queue work manually.  loading in game can cause errors
                cache.loadedplanets = set()
                planets = []
                for cache in self.starcache:
                    star = cache.star
                    for planet in star.planets:
                        pcache = Expando()
                        pcache.planet = planet
                        pcache.loaded = 0
                        cache.planets.append(pcache)
                        planets.append(pcache)
                ProcessPlanets(planets)
                    
            #PlanetModelingManager.modPlanetReqList.Clear()
            #PlanetModelingManager.fctPlanetReqList.Clear()
                    
            for i, cache in enumerate(self.starcache):
                if cache.starloaded < 0: # check planets
                    loaded = sum( ( planet.loaded for planet in cache.planets ) )
                    if loaded == len(cache.star.planets):
                        cache.starloaded = 0
                    #cache.star.Load()
                if cache.starloaded == 0:
                    cache.values = [WriteKMG(cache.star.GetResourceAmount(i+1)) for i, vein in enumerate(self.ores)]
                    cache.starloaded = 1
                    cache.showtoggle = True
                    cache.color = Color.white
                    tooltip = cache.star.name
                    cache.name = "%s (%s)"%(cache.star.name, str(cache.star.planetCount) )
                    for pcache in cache.planets:
                        planet = pcache.planet
                        if planet.orbitAroundPlanet != None:
                            tooltip += crlf + planet.displayName + ' ' +" (Moon of %s)"%(planet.orbitAroundPlanet.displayName)
                        
                    tooltip += crlf 
                    tooltip += crlf + 'Luminosity:\t%.0f L'%(cache.star.luminosity*100.0)
                    tooltip += crlf + 'Mass:\t\t%.3f M'%(cache.star.mass)
                    tooltip += crlf + 'Temperature:\t%.0f K'%(cache.star.temperature)
                    tooltip += crlf + 'Spectral Class:\t%s'%(cache.star.spectr)
                    tooltip += crlf + 'Radius:\t\t%.2f R'%(cache.star.radius)
                        
                    cache.tooltip = tooltip
                    

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
                    itemwidth = (self.width) / (LDB.veins.Length + 3) # 3 lengths for star nams
                    iconwidth = round(self.ores[0].iconSprite.textureRect.width,0) + 1
                    itemwidth = int( max(iconwidth, itemwidth) )
                    #options = System.Array[GUILayoutOption]([GUILayout.MinWidth(itemwidth), GUILayout.MaxWidth(itemwidth)])
                    options = System.Array[GUILayoutOption]([GUILayout.Width(itemwidth)])
                    
                    if False:  # TODO inline header
                        with HorizontalScope():
                            with VerticalScope():
                                #select = UnityEngine.Object.FindObjectOfType[UIGalaxySelect]()
                                #if select != None:
                                #    tooltip = 'Using Random or Changing Seed while loading will cause an error.'
                                #    tooltip += crlf + 'You will need to restart the game to clear.'
                                #    tooltip += crlf + 'You will need to restart the game to clear.'
                                #    with ColorScope(Color.yellow):
                                #        GUILayout.Box(GUIContent('Changing Seed while loading planets may cause error', tooltip))
                                #        
                                GUILayout.Label(str(itemwidth))
                                #GUILayout.Label(str(self.ores[0].iconSprite.textureRect))
                                
                                GUILayout.FlexibleSpace()
                                GUILayout.Label('Stars')
                            GUILayout.FlexibleSpace()
                            for proto in self.ores: 
                                tooltip = proto.name + "\r\n\r\n" + proto.description
                                GUILayout.Label(GUIContent(proto.iconSprite.texture, tooltip), options)
                                
                            if itemwidth > iconwidth:
                                GUILayout.Space((itemwidth-iconwidth)/3)
                                
                    def render(cache):
                        if cache == None:
                            with HorizontalScope():
                                with VerticalScope():
                                    GUILayout.Label('')
                                    GUILayout.FlexibleSpace()
                                    GUILayout.Label('Stars')
                                GUILayout.FlexibleSpace()
                                for proto in self.ores: 
                                    tooltip = proto.name + "\r\n\r\n" + proto.description
                                    GUILayout.Label(GUIContent(proto.iconSprite.texture, tooltip), options)
                            return
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
                                        itemlist.append(None)
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

        # call to consume mouse events from passing through after windows are processed
        def PreventMouseInputs(self, rect):
            if rect.Contains(Vector2(Input.mousePosition.x, Screen.height - Input.mousePosition.y)):
                if Input.GetMouseButton(0) or Input.GetMouseButtonDown(0) or Input.mouseScrollDelta.y != 0:
                    Input.ResetInputAxes()
        
        def OnGUI(self):
            try:
                self.windowRect = GUI.Window(0xdeaf, self.windowRect, self.windowCallback, '', GUI.skin.scrollView)
                
                self.tooltipRect = GUI.Window(0xdeaf+1, self.tooltipRect, self.tooltipCallback, '', GUI.skin.scrollView)
                self.PreventMouseInputs(self.windowRect)
                #TODO: just disable this there is no value
                #self.PreventMouseInputs(self.tooltipRect)
            except Exception, e:
                self.PrintError(e)
                
                
    _galaxyObject = unity_util.create_gui_behavior(Controller)
    return _galaxyObject

def ProcessPlanets(planets):
    import PlanetRawData, PlanetModelingManager, PlanetAuxData, EPlanetType, LDB, EPlanetSingularity
    import UnityEngine
    import os, sys, math
    from UnityEngine import GUI, GUILayout, GUIStyle, GUIUtility, Screen, Rect, Vector2, Vector3, Input, KeyCode, GUISkin, Font, Color
    from UnityEngine import Event, EventType, WaitForSeconds, GameObject, GUILayoutOption, GUIContent
    ores = [LDB.items.Select(x.MiningItem) for x in LDB.veins]
    crlf = '\r\n'
    
    def UpdatePlanet(pcache):
        try:
            planet = pcache.planet
            if (planet.data == None):
                # Begin copy algorithm from PlanetComputeThreadMain
                algorithm = PlanetModelingManager.Algorithm(planet)
                planet.data = PlanetRawData(planet.precision)
                planet.modData = planet.data.InitModData(planet.modData)
                planet.data.CalcVerts()
                planet.aux = PlanetAuxData(planet)
                algorithm.GenerateTerrain(planet.mod_x, planet.mod_y)
                algorithm.CalcWaterPercent()        
                if planet.factory == None:
                    if (planet.type != EPlanetType.Gas):
                        algorithm.GenerateVegetables
                    if (planet.type != EPlanetType.Gas):
                        algorithm.GenerateVeins(False)
                # End copy algorithm from PlanetComputeThreadMain

            # Build cache
            pcache.showtoggle = False
            pcache.name = planet.displayName
            pcache.tooltip = planet.displayName
            pcache.color = Color.grey
            if planet.orbitAroundPlanet != None:
                pcache.tooltip += " (Moon of %s)"%(planet.orbitAroundPlanet.displayName)
                pcache.name += ' (Moon)'
            if planet.type != EPlanetType.Gas:
                pcache.values = [ WriteKMG(planet.veinAmounts[i+1]) for i, vein in enumerate(ores) ]
            else:
                pcache.values = ['']*len(ores)
                
            pcache.tooltip += crlf + 'Type: \t\t' + planet.typeString
            pcache.tooltip += crlf + 'Orbit Radius: \t%.2f AU'%planet.orbitRadius
            pcache.tooltip += crlf + 'Orbit Period: \t%.2f'%planet.orbitalPeriod
            pcache.tooltip += crlf + 'Rotational Period: \t%.2f'%planet.rotationPeriod
            pcache.tooltip += crlf + 'Orbit Incline: \t%.2f'%planet.orbitInclination
            if planet.singularity != EPlanetSingularity.None:
                pcache.tooltip += crlf + 'Singularity: \t%s'%planet.singularity
                            
            water = LDB.items.Select(planet.waterItemId)
            if water != None: 
                pcache.tooltip += crlf + 'Oceans: \t\t' + water.name
            pcache.tooltip += crlf + 'Land: \t\t%.1f %%'%(planet.landPercent*100.0)
            pcache.tooltip += crlf + 'Wind: \t\t%.0f'%(planet.windStrength*100.0)
            pcache.tooltip += crlf + 'Luminosity:\t%.0f'%(planet.luminosity*100.0)
            if planet.gasItems:
                for k, gas in enumerate(planet.gasItems):
                    proto = LDB.items.Select(gas)
                    pcache.tooltip += crlf + '%-10s\t%.2f'%(proto.name+':', planet.gasSpeeds[k])
        except Exception as ex:
            print(str(ex))
        
        #print("Loaded '%s'"%planet.name)
        pcache.loaded = 1
    
    import System
    for planet in planets:
        System.Threading.ThreadPool.QueueUserWorkItem( System.Threading.WaitCallback(UpdatePlanet), planet )
            
        #import coroutine
        #coroutine.start_new_coroutine(ProcessPlanetsThread, (planets,), {})
        
        
def Reload():
    import shortcuts, gui, screens, galaxy
    reload(shortcuts); reload(gui); reload(screens); reload(galaxy); 
    global _galaxyObject
    try:
        if _galaxyObject != None:
            galaxy.showWindow(reset=False)
    except:
        pass

