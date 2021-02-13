def unity(func):
    """ Decorator for wrapping unity calls """
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import coroutine
            if args == None: args=()
            return coroutine.start_new_coroutine(func, args, kwargs)
        except Exception:
            pass
    return wrapper   
    

def cleanup():
    import unity_util
    unity_util.clean_behaviors()

def getprivateattr(obj, name, default = None, cls=None):
    val = getattr(obj, name, default)
    if val != None: return val
    if not cls: cls = obj.GetType().Name
    return getattr(obj, '_' + cls + '__' + name, default)
    

"""
Create centered window that has a couple of buttons for testing
"""
def test():
    import unity_util
    import UnityEngine
    from UnityEngine import GUI, GUILayout, Screen, Rect, Input, KeyCode
    import System
    
    print("loading test")
    # delete all of the old stuff
    #TODO: dangerous with other mods.  blasts everything to dust
    #unity_util.clean_behaviors()
    
    # clean up previous window if still running
    #  TODO: this is a hack to use global variable but doesn't interfere with other mods
    global _testModGUIBehavior
    try:
        if _testModGUIBehavior != None:
            UnityEngine.Object.DestroyObject(_testModGUIBehavior.gameObject)            
    except NameError:
        _testModGUIBehavior = None
    
    class DemoMessage():
        def __init__(self):
            self.color = UnityEngine.Color.white
            self.counter = 1
            self.options = System.Array.CreateInstance(UnityEngine.GUILayoutOption, 0)
            self.show_buttons = False
            self.gameObject = None # will be assigned if exists as member
            self.component = None # will be assigned if exists as member
            self.visible = True
            #print "Called when object is created"
            
        def Update(self):
            # Update is called less so better place to check keystate
            if Input.GetKeyDown(KeyCode.F8):
                # unity sucks for checking meta keys
                ctrl, alt, shift = unity_util.metakey_state()
                if ctrl and not alt and not shift:
                    self.visible = not self.visible
                    
        def OnGUI(self):
            if self.visible:
                self.counter = self.counter + 1
                origColor = GUI.color
                try:
                    GUI.BeginGroup(Rect (Screen.width / 2 - 50, Screen.height / 2 - 50, 400, 400))
                    GUI.color = self.color
                    with GUILayout.VerticalScope("Group", GUI.skin.window):
                        GUILayout.Label(str(self.counter))
                        self.show_buttons = GUILayout.Toggle(self.show_buttons, "Buttons")
                        if self.show_buttons:
                            if GUILayout.Button("Click me"):
                                print "clicked"
                            if GUILayout.Button("Close"):
                                if self.gameObject: 
                                    UnityEngine.Object.DestroyObject(self.gameObject)
                except:
                    GUI.color = origColor
                GUI.EndGroup()
            
        def __del__(self):
            #print "Called when object is garbage collected"
            pass
    
    _testModGUIBehavior = unity_util.create_gui_behavior(DemoMessage)
    