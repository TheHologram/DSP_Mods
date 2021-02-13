################################################
#
# Dyson Sphere Program
#
#  Installation:
#   * Download base Console - https://github.com/TheHologram/unity-console/releases
#   * Unpack zip to game folder
#   * Drag game exe over IPA.exe to instrument plugins. (Modifies game dlls)
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

class GlobalState(object):
    def __init__(self, visible):
        from UnityEngine import Screen, Rect, Vector2
        import collections
        self.gui = getGlobalGUIState(True)
        self.enabled = False
        self.visible = visible
        self.timerRunning = False
        self.width = 500
        self.height = Screen.height
        self.windowRect = Rect(Screen.width - self.width, 100, self.width, self.height)
        self.tooltipRect = Rect(Screen.width - self.width, Screen.height-500, self.width, 400)
        self.drawPanelRect = Rect(0, 0, 150, 50)
        self.minimize = False

        self.timerPass = True
        self.screen_states = collections.defaultdict(Expando) # shared screen type states
        self.window_states = collections.defaultdict(Expando) # window instance states
        self.windows = []
        self.show_windows = False

       
        pass

def getGlobalState(visible=True, reset=False):
    global _cheatglobalstate
    try:
        if reset:
            _cheatglobalstate = GlobalState(visible)
        _cheatglobalstate
        if visible:
            _cheatglobalstate.visible=True
    except NameError:
        _cheatglobalstate = GlobalState(visible)
    return _cheatglobalstate

def get_all_windows():
    import ManualBehaviour
    from UnityEngine import Object
    #return [ x for x in Object.FindObjectsOfType[ManualBehaviour]() if x.active and x.GetType().Name.EndsWith("Window") or x.GetType().Name.EndsWith("Storage")]
    return [ x for x in Object.FindObjectsOfType[ManualBehaviour]() if x.active and x.GetType().Name.EndsWith("Window") or x.GetType().Name.EndsWith("StorageGrid")]

def getRecipeNames():
    import LDB
    return [(x.ID, x.name) for x in LDB.recipes.dataArray]
    
def getItemNames():
    import LDB
    return [(x.ID, x.name) for x in LDB.items.dataArray]
    
def get_player():
    import GameMain
    return GameMain.mainPlayer

def giveItem(item, count=1):
    import GameMain
    import System
    if isinstance(item, str):
        for x,y in getRecipes():
            if String.Compare(y, str(item), True) == 0:
                GameMain.mainPlayer.package.AddItemStacked(x, count)
    elif isinstance(item, int):
        GameMain.mainPlayer.package.AddItemStacked(int(item), count)

def showWindow(visible=True, reset=False):
    import unity_util
    import UnityEngine
    import os, sys, math
    from UnityEngine import GUI, GUILayout, GUIStyle, GUIUtility, Screen, Rect, Vector2, Vector3, Input, KeyCode, GUISkin, Font
    from UnityEngine import Event, EventType, WaitForSeconds, GameObject, GUILayoutOption, GUIContent
    from System.Reflection import BindingFlags
    import System
    
    # clean up previous window if still running
    #  TODO: this is a hack to use global variable but doesn't interfere with other mods
    global _cheatObject
    try:
        if _cheatObject != None:
            UnityEngine.Object.DestroyObject(_cheatObject.gameObject)            
    except NameError:
        _cheatObject = None
        
    #print("loading cheat window (%s, %s)"%(visible, reset))
    
    #TODO: dangerous with other mods.  blasts everything to dust
    #unity_util.clean_behaviors()

    class Controller():
        def __init__(self):
            import screens
            self.gameObject = None  # will be assigned if exists as member
            self.component = None  # will be assigned if exists as member
            self.state = getGlobalState(visible=visible, reset=reset)
            self.screens = screens.LoadScreenMap()
            modulename = os.path.splitext(__file__)[0]
            self.keycodes = getKeyCodes(modulename)
            ShortcutManager.reloadKeyCodes(modulename)
            self.hidestring = 'Hide ('+self.keycodes['hide'][0]+')'
            self.lasterror = None
            self.lasttooltip = None
            sysSettings = getSystemSettings(modulename)
            self.sysSettings = sysSettings
            self.RefreshPanel()

            def FuncPanelGUI(windowid):
                state = self.state
                try:
                    self.StartPanelTimer()
                    if not state.visible:
                        return

                    if state.minimize:
                        with GUILayout.HorizontalScope():
                            GUILayout.Label('Cheats')
                            if GUILayout.Button("Restore"):
                                state.minimize = False
                    else:
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
                        
                state.timerPass = False
                GUI.DragWindow(state.drawPanelRect)

            def TooltipGUI(windowid):
                try:
                    state = self.state
                    if self.lasttooltip:
                        ShowTooltipWindow(self.lasttooltip, state.tooltipRect)
                except Exception, e:
                    GUILayout.Label(str(e))
                GUI.DragWindow(state.tooltipRect)

            def InitFuncPanelGUI(windowid):
                """Initialize State: This is called only once"""
                # Actually lets hold off until it is actually completely running
                state = self.state
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
                    guistate = state.gui
                    guistate.tinyskin = CloneSkin(GUI.skin)
                    guistate.tinyskin.font = Font( guistate.tinyskin.font.fontNames, guistate.tinyskin.font.fontSize + sysSettings.FontSmaller )
                    guistate.smallskin = CloneSkin(GUI.skin)
                    guistate.smallskin.font = Font( GUI.skin.font.fontNames, GUI.skin.font.fontSize + sysSettings.FontSmall)
                    self.StartPanelTimer()

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

        def MainPanel(self):
            #print('#', end='')
            state = self.state
            
            #GUILayout.Label(str(state.windowRect))
            #print(state.windowRect)
            with GUILayout.HorizontalScope():
                GUILayout.Label('Cheats')
                if GUILayout.Button(self.hidestring):
                    state.visible = False
                if GUILayout.Button("Min"):
                    state.minimize = True
                    self.StopPanelTimer()
                if GUILayout.Button(GUIContent('Reload', 'Reloads Python Files from disk')):
                    Reload()
                if GUILayout.Button("X"):
                    if self.gameObject:
                        #state.visible = False
                        UnityEngine.Object.DestroyObject(self.gameObject)

            # startup interlock. dont show until game loaded
            if not state.enabled:
                if get_player() == None:
                    return
                state.enabled = True

            with GUILayout.VerticalScope():
                editor = self.screens.get("Global", None)
                if editor != None: editor.Show(self, None)
                
                self.RefreshPanel()

                # enumerate windows looking for interesting stuff
                if False and Toggle(state, "show_windows", "Show Windows", defaultValue=False):
                    if state.show_windows and state.windows:
                        for window in state.windows:
                            windowType = window.GetType().FullName
                            editor = self.screens.get(windowType, None)
                            if editor != None:
                                editor.Show(self, window)
                            else:
                                GUILayout.Label("Panel: " + windowType)
            

        def RefreshPanel(self):
            """
            Fix any window states periodically based on what is open and closed
            """
            state = self.state
            
            # clean up window instance states for closed windows
            if state.show_windows and state.timerPass:
                windows = get_all_windows()
                state.windows = windows
            
                # TODO: figure out which windows are open and update states
                if state.window_states:
                    state.window_states = collections.defaultdict(Expando, {window: state.window_states[window] for x in windows if window in state.window_states})
            pass

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
                state = self.state
                state.windowRect = GUI.Window(0xfade, state.windowRect, self.windowCallback, '', GUI.skin.scrollView)
                state.tooltipRect = GUI.Window(0xfade+1, state.tooltipRect, self.tooltipCallback, '', GUI.skin.scrollView)
                self.PreventMouseInputs(state.windowRect)
                self.PreventMouseInputs(state.tooltipRect)
            except Exception, e:
                self.PrintError(e)

        def Update(self):
            # Update is called less so better place to check keystate
            ShortcutManager.evaluate(self)
            pass

        def StartPanelTimer(self):
            state = self.state
            if not state.timerRunning and self.component:
                self.component.StartCoroutine(self.PanelRefreshTimer())

        def StopPanelTimer(self):
            state = self.state
            state.timerRunning = False

        def PanelRefreshTimer(self):
            state = self.state
            state.timerRunning = True
            try:
                while state.visible and state.timerRunning:
                    state.timerPass = True
                    yield WaitForSeconds(1)
            except Exception, e:
                self.PrintError(e)
            state.timerRunning = False
            yield None

    _cheatObject = unity_util.create_gui_behavior(Controller)
    return _cheatObject

def Reload():
    import shortcuts, gui, screens, cheat, galaxy
    reload(shortcuts); reload(gui); reload(screens); reload(cheat); reload(galaxy)
    cheat.showWindow(reset=False)

@ShortcutManager.register(name='hide', shortcut='Ctrl+F8', cheat=False)
class HideShortcut(ShortcutHandler):
    def __init__(self, *args, **kwargs):
        ShortcutHandler.__init__(self,*args, **kwargs)
    def execute(self, win):
        win.state.visible = not win.state.visible

@ShortcutManager.register(name='min', shortcut='Ctrl+F7', cheat=False)
class MinimizeShortcut(ShortcutHandler):
    def __init__(self, *args, **kwargs):
        ShortcutHandler.__init__(self,*args, **kwargs)
    def execute(self, win):
        win.state.minimize = not win.state.minimize

@ShortcutManager.register(name='refresh', shortcut='Ctrl+F6', cheat=False)
class MinimizeShortcut(ShortcutHandler):
    def __init__(self, *args, **kwargs):
        ShortcutHandler.__init__(self,*args, **kwargs)
    def execute(self, win):
        import screens
        reload(screens)
        win.window = None

        