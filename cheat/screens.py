################################################
#
# Customized screens for Dyson Sphere Program
#
#  Collection Screens together here
#
################################################
from __future__ import print_function
from UnityEngine import GUI, GUILayout, GUILayoutOption
import System
import gui
from gui import *

def InitScreenMap():
    global _screens

    _screens = {
        'Global': GlobalInspect(),
        'UIReplicatorWindow': ReplicatorInspect(),
        'UIBeltWindow': BeltInspect()
    }
    print("Screens reloaded")

def LoadScreenMap():
    global _screens
    return _screens

class BaseScreenEditor(object):
    def __init__(self, *args, **kwargs):
        pass

    def Show(self, owner, window):
        pass
        
        
def ShowItems(owner, state):
    import LDB, GameMain
    guistate = owner.state.gui
    from UnityEngine import GUILayout, GUILayoutOption, GUIContent
    items = LDB.items.dataArray
    with GUISkinScope(guistate.smallskin):
        def render(item):
            tooltip = item.description
            with HorizontalScope():
                GUILayout.Label(GUIContent(item.name, tooltip))
                GUILayout.FlexibleSpace()
                if GUILayout.Button(GUIContent('+1', tooltip)):
                    GameMain.mainPlayer.package.AddItemStacked(item.ID, 1)
                if GUILayout.Button(GUIContent('+10', tooltip)):
                    GameMain.mainPlayer.package.AddItemStacked(item.ID, 10)
                if GUILayout.Button(GUIContent('+100', tooltip)):
                    GameMain.mainPlayer.package.AddItemStacked(item.ID, 100)
        state.itembox.Update(items=LDB.items.dataArray, render=render)
        
class GlobalInspect(BaseScreenEditor):
    def __init__(self, *args, **kwargs):
        BaseScreenEditor.__init__(self, *args, **kwargs)


    def Show(self, owner, _):
        guistate = owner.state.gui
        state = owner.state.screen_states["Global"]
       
        if getattr(state, "itembox", None) == None:
            import GameMain
            state.itembox = ScrollView(height=500)
            state.show_items = False
            state.show_mecha = False
            state.show_history = False
            def getMecha():
                return GameMain.mainPlayer.mecha
            def getHistory():
                return GameMain.mainPlayer.mecha.lab.gameHistory
            #state.core = FloatCtrlWrapper("Energy", GameMain.mainPlayer.mecha, "coreEnergy", maxname="coreEnergyCap", showMax=True)
            state.core = FloatCtrlWrapper("Energy", getMecha, "coreEnergy", maxname="coreEnergyCap", showMax=True)
            state.attrs = [
                state.core,
                FloatCtrlWrapper("Research Power", getMecha, "researchPower", showAdd=True),
                FloatCtrlWrapper("Replicate Speed", getMecha, "replicateSpeed", showAdd=True),
                FloatCtrlWrapper("Replicate Power", getMecha, "replicatePower", showAdd=True),
                FloatCtrlWrapper("Walk Speed", getMecha, "walkSpeed", showAdd=True),
                FloatCtrlWrapper("Walk Power", getMecha, "walkPower", showAdd=True),
                FloatCtrlWrapper("Mining Speed", getMecha, "miningSpeed", showAdd=True),
                FloatCtrlWrapper("Mining Power", getMecha, "miningPower", showAdd=True),
                FloatCtrlWrapper("Jump Speed", getMecha, "jumpSpeed", showAdd=True),
                FloatCtrlWrapper("Jump Power", getMecha, "jumpPower", showAdd=True),
                FloatCtrlWrapper("Max Warp Speed", getMecha, "maxWarpSpeed", showAdd=True),
                FloatCtrlWrapper("Max Sail Speed", getMecha, "maxSailSpeed", showAdd=True),
            ]
            state.history = [
                FloatCtrlWrapper("Solar Sail Life", getHistory, "solarSailLife", showAdd=True),
                FloatCtrlWrapper("Solar Energy Loss Rate", getHistory, "solarEnergyLossRate", showAdd=True),
                FloatCtrlWrapper("Mining Speed Scale", getHistory, "miningSpeedScale", showAdd=True),
                FloatCtrlWrapper("Mining Cost Rate", getHistory, "miningCostRate", showAdd=True),
                FloatCtrlWrapper("Logistic Drone Carries", getHistory, "logisticDroneCarries", showAdd=True),
                FloatCtrlWrapper("Logistic Drone Speed", getHistory, "logisticDroneSpeed", showAdd=True),
                FloatCtrlWrapper("Logistic Drone Speed Scale", getHistory, "logisticDroneSpeedScale", showAdd=True),
                FloatCtrlWrapper("Logistic Ship Carries", getHistory, "logisticShipCarries", showAdd=True),
                FloatCtrlWrapper("Logistic Ship Speed", getHistory, "logisticShipSpeed", showAdd=True),
                FloatCtrlWrapper("Logistic Ship Speed Scale", getHistory, "logisticShipSpeedScale", showAdd=True),
                FloatCtrlWrapper("Logistic Ship Warp Speed", getHistory, "logisticShipWarpSpeed", showAdd=True),
            ]
            
        
        if Toggle(state, 'show_mecha', "Show Mecha"):
            for ctrl in state.attrs:
                ShowEditFloatCtrl(ctrl.label, ctrl)
        if Toggle(state, 'show_history', "Show Globals"):
            for ctrl in state.history:
                ShowEditFloatCtrl(ctrl.label, ctrl)
            if ShowButtonWithLabel("Add Research:", "+100000"):
                import GameMain
                GameMain.mainPlayer.mecha.lab.gameHistory.AddTechHash(100000)
        
        with VerticalScope("", guistate.tinyskin.window):
            with HorizontalScope():
                GUILayout.Label('Items')
                state.show_items = GUILayout.Toggle(state.show_items, "Show")
            if state.show_items:
                ShowItems(owner, state)
            

# Add optional things to Replicator (autocomplete?)
class ReplicatorInspect(BaseScreenEditor):
    def __init__(self, *args, **kwargs):
        BaseScreenEditor.__init__(self, *args, **kwargs)

    def Show(self, owner, _):
        guistate = owner.state.gui
        #state = owner.state.screen_states["Replicator"]
        if ShowButtonWithLabel("Build All", "Go"):
            pass

class BeltInspect(BaseScreenEditor):
    def __init__(self, *args, **kwargs):
        BaseScreenEditor.__init__(self, *args, **kwargs)

    def Show(self, owner, this):
        guistate = owner.state.gui
        
        import GameMain, LDB, EntityData
        id = GameMain.mainPlayer.controller.actionInspect.inspectId
        beltid = this.beltId
        
        if id > 0:
            with SmallerFont():
                with HorizontalScope():
                    GUILayout.Label("Inspect Id")
                    GUILayout.FlexibleSpace()
                    GUILayout.Label(str(id))
                with HorizontalScope():
                    GUILayout.Label("Belt Id")
                    GUILayout.FlexibleSpace()
                    GUILayout.Label(str(beltid))
                   
                component = this.traffic.beltPool[beltid]
                if component.id == beltid:
                    with HorizontalScope():
                        GUILayout.Label("Seg Index")
                        GUILayout.FlexibleSpace()
                        GUILayout.Label(str(component.segIndex))
                    entity = this.factory.entityPool[component.entityId]
                    with HorizontalScope():
                        GUILayout.Label("Proto ID")
                        GUILayout.FlexibleSpace()
                        GUILayout.Label(str(entity.protoId))
                    
                    proto = LDB.items.Select(entity.protoId)
                    with HorizontalScope():
                        GUILayout.Label("Proto ID")
                        GUILayout.FlexibleSpace()
                        GUILayout.Label(str(proto.name))
                    
                    if entity.protoId == 2001 or entity.protoId == 2002: # Conveyor belt MK.I
                        if ShowButtonWithLabel("Upgrade", "Go"):
                            e = entity
                            e = EntityData(
                                id = e.id, 
                                protoId = e.protoId + 1,
                                modelIndex = e.modelIndex,
                                pos = e.pos,
                                rot = e.rot,
                                beltId = e.beltId,
                                splitterId = e.splitterId,
                                storageId = e.storageId,
                                tankId = e.tankId,
                                minerId = e.minerId,
                                inserterId = e.inserterId,
                                assemblerId = e.assemblerId,
                                fractionateId = e.fractionateId,
                                ejectorId = e.ejectorId,
                                siloId = e.siloId,
                                labId = e.labId,
                                stationId = e.stationId,
                                powerNodeId = e.powerNodeId,
                                powerGenId = e.powerGenId,
                                powerConId = e.powerConId,
                                powerAccId = e.powerAccId,
                                powerExcId = e.powerExcId,
                                monsterId = e.monsterId,
                                modelId = e.modelId,
                                mmblockId = e.mmblockId,
                                colliderId = e.colliderId,
                                audioId = e.audioId
                            )
                            this.factory.entityPool[component.entityId] = e
                            pass

                    
            
                    #state = owner.state.screen_states["Replicator"]
                    if ShowButtonWithLabel("Build All", "Go"):
                        pass
        

InitScreenMap()