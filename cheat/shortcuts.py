################################################
#
# Contains keyboard shortcut handlers
#
#  Contains reusable components mostly related to GUI components that
#
################################################
from __future__ import print_function

from UnityEngine import KeyCode, Input
import unity_util


class ShortcutManager(object):
    # global _keycodes
    _keycodes = {}

    def __init__(self):
        pass

    @staticmethod
    def register(*args, **kwargs):
        def wrapper(cls):
            result = cls(*args, **kwargs)
            name = kwargs.get('name', None)
            if name: ShortcutManager._keycodes[name] = result
            return result
        return wrapper


    #@classmethod
    #def register(cls, name='', shortcut='', cheat=False):
    #    #name = kwargs.get('name', None)
    #    if name: cls._keycodes[name] = cls(name=name, shortcut=shortcut, cheat=cheat)
    #    return cls


    @classmethod
    def parseKeyCode(cls, s):
        from System import Enum

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

    @classmethod
    def reloadKeyCodes(cls, configname):
        if cls._keycodes:
            from UnityEngine import KeyCode, Input
            try:
                import ConfigParser, sys, os.path
                config = ConfigParser.SafeConfigParser(allow_no_value=True)
                config.read(configname + '.ini')
                for k, shortcut in config.items('Shortcuts'):
                    handler = cls._keycodes.get(k.lower(), None)
                    if handler:
                        handler.shortcut = cls.parseKeyCode(shortcut) if shortcut else ShortcutHandler._defaultcode
            except Exception, e:
                print(str(e))
        

    @classmethod
    def evaluate(cls, context):
        try:
            # quick bypass
            if not Input.anyKeyDown:
                return False

            ctrl, alt, shift = unity_util.metakey_state()
            for k,v in ShortcutManager._keycodes.iteritems():
                if v.enabled:
                    (_, icode, ictrl, ialt, ishift) = v.shortcut
                    if Input.GetKeyDown(icode) and ctrl == ictrl and alt == ialt and shift == ishift:
                        v.execute(context)
                        return True
        except Exception, ex:
            print('Error: ' + str(ex))
        return False


class ShortcutHandler(object):
    from UnityEngine import KeyCode, Input
    _defaultcode = ('', KeyCode.None, False, False, False)

    # def __init__(self, name=None, shortcut=None, cheat=False):
    #     self.name = name
    #     self.shortcut = ShortcutManager.parseKeyCode(shortcut) if shortcut else ShortcutHandler._defaultcode
    #     self.cheat = cheat

    def __init__(self, *args, **kwargs):
        #super(ShortcutHandler, self).__init__()
        self._name = kwargs.get('name', None)
        shortcut = kwargs.get('shortcut', None)
        self._shortcut = ShortcutManager.parseKeyCode(shortcut) if shortcut else ShortcutHandler._defaultcode
        self._cheat = kwargs.get('cheat', False)

    def get_name(self):
        return self._name

    name = property(fget=get_name, doc="Shortcut Name")

    def get_enabled(self):
        return self._shortcut and int(self._shortcut[1]) != 0
    enabled = property(fget=get_enabled, doc="Shortcut Enabled")

    def get_shortcut(self):
        return self._shortcut

    def set_shortcut(self, code):
        self._shortcut = code if code else ShortcutHandler._defaultcode

    shortcut = property(fget=get_shortcut, fset=set_shortcut, doc="Shortcut Tuple")

    def get_keydesc(self):
        return self._shortcut[0] if self._shortcut else ''

    keydesc = property(fget=get_keydesc, doc="Shortcut Key Description")

    def can_execute(self, context):
        """
        Can Execute this shortcut

        :param context:
        :return: Boolean indicating if shortcut can be executed
        """
        return True

    def execute(self, context):
        pass


# @ShortcutManager.register(name='hide', shortcut='Ctrl+F8', cheat=False)
# class HideShortcut(ShortcutHandler):
#     def __init__(self, *args, **kwargs):
#         super(ShortcutHandler, self).__init__(*args, **kwargs)
#
#     def execute(self, context):
#         pass
