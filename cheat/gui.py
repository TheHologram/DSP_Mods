################################################
#
# Helper functions for Imgui in python
#
#  Contains reusable components mostly related to GUI components
#
################################################
from __future__ import print_function
from UnityEngine import GUI, GUILayout, GUIContent, GUILayoutOption
import System
import types
import unity_util

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
   
def handle_exception(func):
    """ Decorator for wrapping unity calls """
    import functools, System
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            print('Unhandled: ' + str(e))
        except System.Exception, e:
            print('Unhandled: ' + str(e))
        return kwargs.get('default', None)
    return wrapper
   
def clear():
    _console.Clear()

def clear_globals():
    keys = [key for key in globals().keys() if not key.startswith('__')]
    for key in keys:
        del globals()[key]
    
def cleanup():
    import unity_util
    unity_util.clean_behaviors()
    
def getattrdef(obj, key, defaultcls=None):
    val = getattr(obj, key, None)
    if val == None and defaultcls != None:
        val = defaultcls()
        setattr(obj, key, val)
    return val
        
def getprivateattr(obj, name, default = None, cls=None):
    val = getattr(obj, name, default)
    if val != None: return val
    if not cls: cls = obj.GetType().Name
    return getattr(obj, '_' + cls + '__' + name, default)

def setprivateattr(obj, name, value, cls=None):
    try:
        setattr(obj, name, value)
        if val != None: return val
    except:
        pass
    try:
        if not cls: cls = obj.GetType().Name
        return setattr(obj, '_' + cls + '__' + name, value)
    except:
        pass

class Expando(object):
    pass

def createGlobalGUIState():
    state = Expando()
    state.tinyskin = None
    state.smallskin = None
    return state
    
def getGlobalGUIState(reset=False):
    global _globalguistate
    try:
        if reset or _globalguistate == None:
            _globalguistate = createGlobalGUIState()
    except NameError:
        _globalguistate = createGlobalGUIState()
    return _globalguistate
    
    
def getSystemSettings(configname):
    try:
        import ConfigParser, sys, os.path
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        config.read( configname + '.ini' )
        values = {k.lower(): v for k,v in config.items('System')}
    except Exception, e:
        print(str(e))
        values = {}
        
    from UnityEngine import Screen
    width = max(250, Screen.width / 5)
        
    cls = Expando()
    cls.DynamicFont=values.get('dynamicfont', True) in ['true', '1', 'True', 'y', 'yes', 'Yes', 1, True]
    cls.FontBase=float(values.get('fontbase', 0))
    cls.FontBaseDelta=float(values.get('fontbasedelta', +0))
    cls.FontSmall=float(values.get('fontsmall', -2))
    cls.FontSmaller=float(values.get('fontsmaller', -4))
    cls.EnableCheatShortcuts= values.get('enablecheatshortcuts', False) in ['true', '1', 'True', 'y', 'yes', 'Yes', 1, True]
    cls.PanelWidth=int(values.get('panelwidth', width))
    return cls
        
def parseKeyCode(s):
    from System import Enum
    from UnityEngine import KeyCode
    try:
        if s:
            ctrl, alt, shift = False, False, False
            keys = s.lower().split('+')
            shift = 'shift' in keys
            ctrl = 'ctrl' in keys or 'control' in keys
            alt = 'alt' in keys or 'meta' in keys
            code = Enum.Parse(KeyCode, keys[-1:][0], True)
            return (s, code, ctrl, alt, shift)
    except:
        pass
    return (s, KeyCode.None, False, False, False)
 
def getKeyCodes(configname):
    from UnityEngine import KeyCode
    keycodes = {}
    try:
        import ConfigParser, sys, os.path
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        config.read( configname + '.ini' )
        for k,v in config.items('Shortcuts'):
            keycodes[k.lower()] = parseKeyCode(v)
    except Exception, e:
        print(str(e))
    if not keycodes.get('hide', None):
        keycodes['hide'] = ('Ctrl+F8', KeyCode.F8, True, False, False)    
    return keycodes

    
def isNumber(s):
    return True if (s is int) else str(s).replace('.','',1).isdigit()  # not obvious but fastest check
    
def appName():
    global _appname # truly global in the app
    try:
        _appname
    except NameError:
        _appname = ''
        import ctypes
        buffer = ctypes.create_string_buffer(260)
        ctypes.windll.kernel32.GetModuleFileNameA(None, buffer, len(buffer))
        _appname = buffer.value
    return _appname
    
def appFileName():
    from System.IO import Path
    return Path.GetFileNameWithoutExtension(appName())
    
def appDataFolder():
    from System.IO import Path
    name = appName()
    app = Path.GetFileNameWithoutExtension(name)
    path = Path.Combine( Path.GetDirectoryName(name), app + '_Data')
    return Path.GetFullPath(path)
    
def appOverrideFolder():
    from System.IO import Path
    return Path.GetFullPath(Path.Combine( appDataFolder(), 'override' ))
    
class ColorScope():
    def __init__(self, color=None):
        self.color = color
        
    def __enter__(self):
        from UnityEngine import GUI, Color
        self.save = GUI.color
        GUI.color = self.color
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        from UnityEngine import GUI, Color
        GUI.color = self.save

class GUISkinScope():
    def __init__(self, skin=None):
        self.skin = skin
    def __enter__(self):
        from UnityEngine import GUI
        self.save = GUI.skin
        if self.skin: GUI.skin = self.skin
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        from UnityEngine import GUI
        GUI.skin = self.save
        
class HorizontalScope():
    def __init__(self, options=None):
        self.options = options
        
    def __enter__(self):
        from UnityEngine import GUILayout, GUILayoutOption
        import System
        if self.options:
            GUILayout.BeginHorizontal(System.Array[GUILayoutOption](self.options))
        else:
            GUILayout.BeginHorizontal()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        from UnityEngine import GUILayout, GUILayoutOption
        GUILayout.EndHorizontal()
        
class VerticalScope():
    def __init__(self,text=None,style=None,options=None):
        from UnityEngine import GUI
        self.text=text if text else ''
        self.style=style if style else GUI.skin.scrollView
        self.options = System.Array[GUILayoutOption](options) if options else None
    def __enter__(self):
        from UnityEngine import GUILayout, GUILayoutOption
        import System
        if self.options:
            GUILayout.BeginVertical(self.options)
        else:
            GUILayout.BeginVertical(self.text,self.style)
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        from UnityEngine import GUILayout, GUILayoutOption
        GUILayout.EndVertical()
 
class ScrollView:
    def __init__(self, windowtype=None, width=-500, height=-300, items=[]):
        self.pos = None
        self.windowtype = windowtype
        self.width = width
        self.height = height
        self.options = None
        self.items = items
        self.render = None
        self.error = None
    def Update(self, render=None, items=[], tooltip=False):
        from UnityEngine import GUI, GUILayout, GUILayoutOption
        render = render if render else self.render
        if not render: return
        if not self.options:            
            from UnityEngine import Vector2
            import System
            self.pos = Vector2(0,0)
            if not self.windowtype: self.windowtype = GUI.skin.textArea
            self.options = System.Array[GUILayoutOption]([GUILayout.MaxWidth(abs(self.width)), GUILayout.ExpandWidth(self.width<0), GUILayout.MaxHeight(abs(self.height)), GUILayout.ExpandHeight(self.height<0)])
        self.pos = GUILayout.BeginScrollView(self.pos, self.windowtype, self.options)
        if not self.error:
            try:
                if not items and self.items: 
                    items = self.items
                for row in items:
                    result = render(row)
                    if result == True: break
            except Exception, e:
                self.error = "Error: " + str(e)
        GUILayout.EndScrollView()
        if self.error:
            GUILayout.Label(self.error)
            
def CloneSkin(skin):
    from UnityEngine import GUILayoutOption, GUIContent, Font, GUISkin, ScriptableObject
    from System.Reflection import BindingFlags    
    #newskin = GUISkin()
    newskin = ScriptableObject.CreateInstance[GUISkin]()
    props = newskin.GetType().GetProperties(BindingFlags.Public | BindingFlags.Instance| BindingFlags.SetProperty)
    for prop in [x.Name for x in props]:
        try:
            setattr(newskin, prop, getattr(skin, prop))
        except:
            pass
    return newskin

def Toggle(state, name, label, defaultValue=False):
    from UnityEngine import GUILayout
    value = getattr(state, name, defaultValue)
    newvalue = GUILayout.Toggle(value, label)
    if newvalue != value:
        setattr(state, name, newvalue)
    return newvalue
    
class AttrCtrl:
    def __init__(self, obj, attr, default=None):
        self.obj = obj
        self.attr = attr
        self.default = default
    def get(self):
        return getprivateattr(self.obj, self.attr, self.default)
    def set(self, value):
        setprivateattr(self.obj, self.attr, value)
        
class ArrayCtrl:
    def __init__(self, arr, idx):
        self.arr = arr
        self.idx = idx
    def get(self):
        return self.arr[self.idx]
    def set(self, value):
        self.arr[self.idx] = value
        

def ShowEditFloatValue(name, value, incr=1.0, minv=0.0, maxv=100.0, format='%.2f', buttons=False):
    with HorizontalScope():
        if name: GUILayout.Label(name)
        GUILayout.FlexibleSpace()
        oidx = format%(value)
        nidx = GUILayout.TextField(oidx)
        changed = oidx != nidx
        val = max(minv, min(maxv, float(nidx)) )
        if buttons:
            ctrl, alt, shift = unity_util.metakey_state()
            if incr == None:
                import math
                power = max(0, int(math.log(value)/math.log(10))-1) if val > 0 else 0
                incr = 10.0 ** power
            if shift: incr *= 10.0
            if ctrl: incr /= 10.0
            if GUILayout.Button(GUIContent('-', 'Reduce by '+str(incr))):
                val = max(minv, min(maxv, val-incr) )
                changed = True
            if GUILayout.Button(GUIContent('+', 'Increase by '+str(incr))):
                val = max(minv, min(maxv, val+incr) )
                changed = True
        if changed:
            val = System.Convert.ChangeType(val, value.GetType())
        return (changed, val)

def ShowEditInteger(name, obj, attr, minv=0, maxv=255, buttons=False):
    changed = False
    with HorizontalScope():
        GUILayout.Label(name)
        GUILayout.FlexibleSpace()
        oidx = str(getprivateattr(obj, attr))
        nidx = GUILayout.TextField(oidx)
        if oidx != nidx:
            value = max(minv, min(maxv, int(nidx)) )
            setprivateattr(obj, attr, value)
            changed = True
        if buttons:
            value = getprivateattr(obj, attr)
            if GUILayout.Button('-'):
                value = max(minv, min(maxv, int(value)-1) )
                setprivateattr(obj, attr, value)
                changed = True
            if GUILayout.Button('+'):
                value = max(minv, min(maxv, int(value)+1) )
                setprivateattr(obj, attr, value)                    
                changed = True
    return changed

class FloatCtrlWrapper:
    def __init__(self, label, owner, name, **kwargs):
        self.owner = owner
        self.label = label
        self.name = name
        self.minv=0.0
        self.maxv=1000000000.0
        self.incr=1.0
        self.format='%.2f'
        self.minname=None
        self.maxname=None
        self.showMin=False
        self.showMax=False
        self.showAdd=False
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
    def get(self):
        owner = self.owner() if isinstance(self.owner, types.FunctionType) else self.owner
        return getattr(owner, self.name, self.minv)
    def set(self, value):
        owner = self.owner() if isinstance(self.owner, types.FunctionType) else self.owner
        setattr(owner, self.name, value)
    def min(self):
        owner = self.owner() if isinstance(self.owner, types.FunctionType) else self.owner
        return getattr(owner, self.minname) if self.minname else self.minv
    def max(self):
        owner = self.owner() if isinstance(self.owner, types.FunctionType) else self.owner
        return getattr(owner, self.maxname) if self.maxname else self.maxv

def ShowEditFloatCtrl(name, ctrl, refresh=None):
    with HorizontalScope():
        minv=getattr(ctrl,'minv', 0.0)
        maxv=ctrl.max()
        format=getattr(ctrl,'format','%.2f')
        showMin=getattr(ctrl,'showMin',False)
        showMax=getattr(ctrl,'showMax',False)
        showAdd=getattr(ctrl,'showAdd',False)
    
        GUILayout.Label(name)
        GUILayout.FlexibleSpace()
        oidx = format%(ctrl.get())
        nidx = GUILayout.TextField(oidx)
        changed = False
        if oidx != nidx:
            value = max(minv, min(maxv, float(nidx)) )
            ctrl.set(value)
            changed=True
        if showMin and GUILayout.Button('Min'):
            ctrl.set(float(minv))
        if showAdd:
            import math
            value = ctrl.get()
            
            power = max(0, int(math.log(value)/math.log(10))-1) if value > 0 else 0
            incr = 10.0 ** power
            if GUILayout.Button('-'):
                value = max(minv, min(maxv, float(value)-incr) )
                ctrl.set(value)
                changed=True
            if GUILayout.Button('+'):
                value = max(minv, min(maxv, float(value)+incr) )
                ctrl.set(value)                    
                changed=True
            incr = 10.0 ** (power+1)
            if GUILayout.Button('++'):
                value = max(minv, min(maxv, float(value)+incr) )
                ctrl.set(value)                    
                changed=True
            
        if showMax and GUILayout.Button('Max'):
            ctrl.set(float(maxv))
            changed=True
        
        if changed and refresh: refresh()
        return changed
        
def ShowFloatSliderCtrl(name, ctrl, minv=0.0, maxv=100.0, format='%.2f', pct=0.4, refresh=None):
    with HorizontalScope():
        GUILayout.Label(name)
        GUILayout.FlexibleSpace()
        oval = ctrl.get()
        oidx = format%(oval)
        nidx = GUILayout.TextField(oidx)
        changed = False
        if oidx != nidx:
            value = max(minv, min(maxv, float(nidx)) )
            ctrl.set(value)
            changed=True
        options = System.Array[GUILayoutOption]([GUILayout.ExpandWidth(True), GUILayout.MaxWidth(windowWidth*pct)])
        nval = GUILayout.HorizontalSlider(oval, minv, maxv, options)
        if oval != nval:
            ctrl.set( max(minv, min(maxv, float(nval)) ) )
            changed=True
        if changed and refresh: refresh()
        return changed
        
def ShowFloatSlider(val, name='', minv=0.0, maxv=100.0, format='%.2f', pct=0.4, width=500):
    import System
    with HorizontalScope():
        if name: GUILayout.Label(name)
        oval = val
        oidx = format%(oval)
        nidx = GUILayout.TextField(oidx)
        if oidx != nidx:
            val = max(minv, min(maxv, float(nidx)) )
        options = System.Array[GUILayoutOption]([GUILayout.ExpandWidth(True), GUILayout.MaxWidth(500)])
        nval = GUILayout.HorizontalSlider(oval, minv, maxv, options)
        if oval != nval:
            val = max(minv, min(maxv, float(nval)) )
        return val
        
            
def ShowEditValue(label, obj, attr, tooltip=None):
    oval = str(getprivateattr(obj, attr))
    GUILayout.Label(label)
    value = getprivateattr(obj, attr)
    nval = GUILayout.TextField(oval)
    if oval != nval:
        setprivateattr(obj, attr, nval)
        return True
    return False
        
def ShowEditArrayValue(label, arr, idx, tooltip=None):
    GUILayout.Label(label)
    oval = str(arr[idx])
    nval = GUILayout.TextField(oval)
    if oval != nval:
        arr[idx] = int(nval)
        return True
    return False
            
def ShowEditText(label, obj, attr, tooltip=None):
    with HorizontalScope():
        oval = str(getprivateattr(obj, attr))
        GUILayout.Label(GUIContent(label, oval))
        GUILayout.FlexibleSpace()
        value = getprivateattr(obj, attr)
        nval = GUILayout.TextField(oval)
        if oval != nval:
            setprivateattr(obj, attr, nval)


def ShowLabel(label, value):
    with HorizontalScope():
        GUILayout.Label(GUIContent(str(label), ''))
        GUILayout.FlexibleSpace()
        GUILayout.Label(GUIContent(str(value), ''))
        
        
def ShowBool(label, obj, attr, tooltip='', options=None):
    oval = getprivateattr(obj, attr)
    content  = GUIContent(label, tooltip)
    if options:
        nval = GUILayout.Toggle(bool(oval), content, GUI.skin.toggle, options)
    else:
        nval = GUILayout.Toggle(bool(oval), content)
    if oval != nval:
        setprivateattr(obj, attr, nval)


def ShowButtonWithLabel(label, value, tooltip='', options=None):
    with HorizontalScope():
        nval = False
        GUILayout.Label(GUIContent(label, tooltip))
        if options:
            nval = GUILayout.Button(value, GUI.skin.button, options)                        
        else:
            nval = GUILayout.Button(value)
        return nval

def ShowTooltipWindow(tooltip, tooltipRect):
    from System import Array
    from UnityEngine import GUI, GUILayout, GUILayoutOption, GUIContent, Font, GUISkin, GUIStyle, TextClipping, TextAnchor
    
    tooltip = tooltip if tooltip else ''
    state = getGlobalGUIState()
    skinbox = getattr(state, 'skinbox', None)
    if skinbox == None:
        skinbox = CloneSkin(GUI.skin)
        setattr(state, 'skinbox', skinbox)
        skinbox.font = Font( GUI.skin.font.fontNames, GUI.skin.font.fontSize-4)
        skinbox.box = GUIStyle(skinbox.box)
        skinbox.box.wordWrap = True
        skinbox.box.clipping = TextClipping.Clip
        skinbox.box.alignment = TextAnchor.UpperLeft        
        skinbox.label = GUIStyle(skinbox.label)
        skinbox.label.wordWrap = True
        skinbox.label.clipping = TextClipping.Clip
        skinbox.label.alignment = TextAnchor.UpperLeft    
    with GUISkinScope(skinbox):
        options = Array[GUILayoutOption]([GUILayout.Width(tooltipRect.width), GUILayout.ExpandHeight(False), GUILayout.MaxHeight(tooltipRect.height)])
        GUILayout.Box(tooltip, options)

        
def SpinBox(items, index, skip=False, label=None, tooltip=None, extra=None):
    state = getGlobalGUIState()
    nitems = len(items)
    if nitems == 0: return
    tt = tooltip(items[index]) if tooltip else ''
    with GUISkinScope(state.smallskin):
        with GUILayout.HorizontalScope():
            with GUISkinScope(state.tinyskin):
                idx = index+1
                newidx = int(GUILayout.TextArea(str(idx)))
                if newidx != idx:
                    index = max(0, min(nitems-1, newidx))                
            if not skip and nitems > 10 and GUILayout.Button(GUIContent('<<', tt)):
                index = max(0, index - 10)
            if GUILayout.Button(GUIContent('<', tt)):
                index = max(0, index - 1)
            GUILayout.FlexibleSpace()
            with GUISkinScope(state.tinyskin):
                item = items[index]
                GUILayout.Label( GUIContent(label(item) if label else str(item), tooltip(item) if tooltip else '') )
            GUILayout.FlexibleSpace()
            if GUILayout.Button(GUIContent('>', tt)):
                index = min(nitems-1, index + 1)
            if not skip and nitems > 10 and GUILayout.Button(GUIContent('>>', tt)):
                index = min(nitems-1, index + 10)
            with GUISkinScope(state.tinyskin):
                GUILayout.Label(str(nitems))
            if extra:
                extra(item)
    return index

def EditEnum(label, obj, attr, enum, default=None):
    change = False
    with HorizontalScope():
        with SmallerFont():
            GUILayout.Label(label)
        items = list(System.Enum.GetNames(enum))
        val = getattr(obj, attr, None)
        if val == None: 
            val = System.Enum.Parse(enum, items[0]) if default == None else default
            setattr(obj, attr, val)
        idx = items.index(str(val))
        val = SpinBox(items, idx)
        if val != idx:
            setattr(obj, attr, System.Enum.Parse(enum, items[val]))
            change = True
    return change
        
def SmallerFont():
    state = getGlobalGUIState()
    return GUISkinScope(state.tinyskin)

def SmallFont():
    state = getGlobalGUIState()
    return GUISkinScope(state.smallskin)
