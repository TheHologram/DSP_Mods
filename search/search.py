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
import System
import sys

import unity_util
import UnityEngine
import os, sys, math
from System.Reflection import BindingFlags
import System
from System import Random, DateTime

import UIGalaxySelect, GalaxyData, StarData, PlanetData, GameMain, StringBuilderUtility
import PlanetRawData, PlanetModelingManager, PlanetAuxData, EPlanetType, LDB, EPlanetSingularity
import UniverseGen, GameDesc
import HighStopwatch

ores = [LDB.items.Select(x.MiningItem) for x in LDB.veins]
crlf = '\r\n'

class Report(object):
    def __init__(self, seed, *args, **kwargs):
        self.seed = seed
        for k,v in kwargs.iteritems():
            setattr(self, k, v)

class GalaxySearch():
    lock = System.Object()
    rand = Random(int( (DateTime.Now.Ticks/ 10000L) & 0x7FFFFFFF))
    
    def __init__(self, *args, **kwargs):
        self.results = kwargs.get('results', None)
        if self.results == None: self.results = []
        
        self.seed = kwargs.get('seed', 0)
        self.gameDesc = GameDesc()
        self.gameDesc.SetForNewGame(UniverseGen.algoVersion, self.seed, 64, 1, 1)
        self.galaxy = None
        if self.seed > 0:
            self.SetStarmapGalaxy()

    def SetStarmapGalaxy(self):
        System.Threading.Monitor.Enter(GalaxySearch.lock)
        try:
            if self.galaxy != None:
                self.galaxy.Free()
            self.galaxy = UniverseGen.CreateGalaxy(self.gameDesc)
        finally:
            System.Threading.Monitor.Exit(GalaxySearch.lock)
        
    def Reseed(self):
        self.gameDesc.galaxySeed = GalaxySearch.rand.Next(100000000)
        self.SetStarmapGalaxy()
        
    def Seed(self, seed):
        self.gameDesc.galaxySeed = int(seed)
        self.SetStarmapGalaxy()
        
    def getSeed(self):
        return self.gameDesc.galaxySeed
        
    def AddResult(self, report):
        System.Threading.Monitor.Enter(self.results)
        try:
            self.results.append(report)
        finally:
            System.Threading.Monitor.Exit(self.results)
        
    def CalculatePlanet(self, planet):
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
    
    def ReportPlanet(self, planet):
        
        result = planet.displayName
        if planet.orbitAroundPlanet != None:
            result += " (Moon of %s)"%(planet.orbitAroundPlanet.displayName)
        result += crlf + 'Type: \t\t' + planet.typeString
        result += crlf + 'Orbit Radius: \t%.2f AU'%planet.orbitRadius
        result += crlf + 'Orbit Period: \t%.2f'%planet.orbitalPeriod
        result += crlf + 'Rotational Period: \t%.2f'%planet.rotationPeriod
        result += crlf + 'Orbit Incline: \t%.2f'%planet.orbitInclination
        if planet.singularity != EPlanetSingularity.None:
            result += crlf + 'Singularity: \t%s'%planet.singularity
                        
        water = LDB.items.Select(planet.waterItemId)
        if water != None: 
            result += crlf + 'Oceans: \t\t' + water.name
        result += crlf + 'Land: \t\t%.1f %%'%(planet.landPercent*100.0)
        result += crlf + 'Wind: \t\t%.0f'%(planet.windStrength*100.0)
        result += crlf + 'Luminosity:\t%.0f'%(planet.luminosity*100.0)
        if planet.gasItems:
            for k, gas in enumerate(planet.gasItems):
                proto = LDB.items.Select(gas)
                result += crlf + '%-10s\t%.2f'%(proto.name+':', planet.gasSpeeds[k])
        return result
                
    def ReportStar(self, star):
        homestar = self.galaxy.stars[0]
        dist = (homestar.position - star.position).magnitude
        
        tooltip = "%s (%s)"%(star.name, str(star.planetCount) )
        tooltip += crlf 
        tooltip += crlf + 'Luminosity:\t%.0f L'%(star.luminosity*100.0)
        tooltip += crlf + 'Mass:\t\t%.3f M'%(star.mass)
        tooltip += crlf + 'Temperature:\t%.0f K'%(star.temperature)
        tooltip += crlf + 'Spectral Class:\t%s'%(star.spectr)
        tooltip += crlf + 'Radius:\t\t%.2f R'%(star.radius)
        tooltip += crlf + 'Distance:\t\t%.2f ly'%(dist)
        
        #values = [WriteKMG(star.GetResourceAmount(i+1)) for i, vein in enumerate(self.ores)]
        return tooltip
        
    def Report(self):
        star = self.galaxy.stars[0]
        print(self.ReportStar( self.galaxy.stars[0] ))
        for planet in star.planets:
            print('')
            print(self.ReportPlanet(planet))
        
    def QueueGalaxy():
        import System
        for planet in planets:
            System.Threading.ThreadPool.QueueUserWorkItem( System.Threading.WaitCallback(UpdatePlanet), planet )
       
    def MultipleMoons(self, star):
        for planet in star.planets:
            if (planet.singularity & EPlanetSingularity.MultipleSatellites) != EPlanetSingularity.None:
                return True
        return False
        
    def CountMoons(self, star):
        # should verify that the moons are on same planet
        n = 0
        for planet in star.planets:
            # orbit is known before calc
            if planet.orbitAroundPlanet != None:
                n += 1
        return n
        
    def CalculateStar(self, star):
        for planet in star.planets:
            self.CalculatePlanet(planet)

    def CountTidalLockPlanet(self, star):
        n = 0
        locked = EPlanetSingularity.TidalLocked | EPlanetSingularity.TidalLocked2 | EPlanetSingularity.TidalLocked4
        for planet in star.planets:
            if (planet.singularity & locked) != EPlanetSingularity.None:
                n += 1
        return n
            
    def CheckHome(self):
        homestar = self.galaxy.stars[0]
        if self.MultipleMoons(homestar) and self.CountTidalLockPlanet(homestar) > 0:
            self.CalculateStar(homestar)
            if homestar.GetResourceAmount(8) > 0:
                return 1
            return 0
        return -1
        
    def Check(self):
        val = self.CheckHome()
        return val

def ReportSeed(seed):
    scan = GalaxySearch(seed=seed)
    print("Check = %s"%scan.Check())
    scan.Report()
    
class Scanner():
    def __init__(self):
        self.tasks = []
        self.found = []
        self.taskcount = 0
        self.taskdone = 0
        self.foundcount = 0
        self.cancelEvent = System.Threading.ManualResetEvent(False)
        self.stopwatch = HighStopwatch()

    def start(self, count=12):
        self.stopwatch.Begin()
        self.cancelEvent.Reset()
        try:
            def CallSelfRun(task):
                try:

                    task.counter = 0
                    scan = GalaxySearch()
                    while not task.cancelEvent.WaitOne(0, False):
                        task.counter += 1
                        scan.Reseed()
                        check = scan.Check()
                        if check > 0:
                            task.found.append(scan.galaxy.seed)
                            print(scan.galaxy.seed)
                            task.foundcount += 1
                except Exception as ex:
                    print(str(ex))
                task.done = True
                
            self.taskcount = 0
            self.taskdone = 0
            tasks = [ Expando() for x in range(count) ]
            for task in tasks:
                task.seed = GalaxySearch.rand.Next(100000000)
                task.done = False
                task.counter = 0
                task.found = []
                task.foundcount = 0
                task.cancelEvent = self.cancelEvent
                System.Threading.ThreadPool.QueueUserWorkItem( System.Threading.WaitCallback(CallSelfRun), task )
                self.taskcount += 1
            self.tasks = tasks
        except Exception as ex:
            print(str(ex))
        
    def stop(self):
        self.cancelEvent.Set()
        
    def checkDone(self):
        if self.taskcount == 0: return
            
        donetasks = [task for task in self.tasks if task.done] 
        self.taskcount = len(self.tasks)
        self.taskdone = len(donetasks)
        self.foundcount = sum([task.foundcount for task in self.tasks])
        
        if self.taskcount > 0 and self.taskcount == self.taskdone:
            self.taskcount = 0
            self.taskdone = 0
            
            foundcount = sum([task.foundcount for task in self.tasks])
            totalcount = sum([task.counter for task in self.tasks])
            
            print("C:%s F:%s D:%s"%(totalcount, foundcount, str(float(totalcount) / self.stopwatch.duration)))
            for task in self.tasks:
                for result in task.found:
                    print(result)

        
        pass


def background():
    import unity_util
    import UnityEngine
    from UnityEngine import GUI, GUILayout, Screen, Rect, Input, KeyCode
    import System
    
    # clean up previous window if still running
    #  TODO: this is a hack to use global variable but doesn't interfere with other mods
    global _scanModGUIBehavior
    try:
        if _scanModGUIBehavior != None:
            UnityEngine.Object.DestroyObject(_scanModGUIBehavior.gameObject)            
    except NameError:
        _scanModGUIBehavior = None
    
       
    
    class Message():
        def __init__(self):
            self.color = UnityEngine.Color.white
            self.counter = 0
            self.options = System.Array.CreateInstance(UnityEngine.GUILayoutOption, 0)
            self.show_buttons = False
            self.gameObject = None # will be assigned if exists as member
            self.component = None # will be assigned if exists as member
            self.visible = True
            self.scanner = Scanner()
            self.width = 300
            self.height = 200
            self.count = 12
            self.windowRect = Rect((Screen.width-self.width)/4, (Screen.height-self.height)/4, self.width, self.height)
            
            def WindowCallbackGUI(id):
                with VerticalScope("Group", GUI.skin.window):
                    with HorizontalScope():
                        if GUILayout.Button("Start"):
                            self.scanner.start(count=self.count)
                        if GUILayout.Button("Stop"):
                            self.scanner.stop()
                        GUILayout.FlexibleSpace()
                        if GUILayout.Button("Reload"):
                            import search; reload(search); search.background()
                        if GUILayout.Button("X"):
                            self.scanner.stop()
                            if self.gameObject: 
                                UnityEngine.Object.DestroyObject(self.gameObject)
                    ShowEditInteger('Num Threads', self, 'count', minv=1, maxv=64, buttons=True)
                    with HorizontalScope():
                        GUILayout.Label("Running: "+str(self.scanner.taskcount)  )
                        GUILayout.FlexibleSpace()
                        GUILayout.Label("Done: "+str(self.scanner.taskdone)  )
                        GUILayout.FlexibleSpace()
                        GUILayout.Label("Found: "+str(self.scanner.foundcount)  )
                GUI.DragWindow(self.windowRect)
                
            self.windowCallback = GUI.WindowFunction(WindowCallbackGUI)
            
        def Update(self):
            self.scanner.checkDone() # removes any dead threads
            pass
                    
        def OnGUI(self):
            self.windowRect = GUI.Window(0x1ee7, self.windowRect, self.windowCallback, '', GUI.skin.scrollView)
             
        def OnDisable(self):
            self.scanner.stop()
            
        def __del__(self):
            self.scanner.stop()
            
    _scanModGUIBehavior = unity_util.create_gui_behavior(Message)
    