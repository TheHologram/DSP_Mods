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
import GameMain

def InitScreenMap():
    global _screens

    _screens = {
        'Global': GlobalInspect(),
        'UIReplicatorWindow': ReplicatorInspect(),
        'UIBeltWindow': BeltInspect()
    }
    #print("Screens reloaded")

def LoadScreenMap():
    global _screens
    return _screens

class BaseScreenEditor(object):
    def __init__(self, *args, **kwargs):
        pass

    def Show(self, owner, window):
        pass
        
        
def ShowItems(owner, state):
    import LDB
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
        
def closestVein(planet=None, pos=None):
    if pos == None: pos = GameMain.mainPlayer.position
    if planet == None: planet = GameMain.mainPlayer.planetData
    bestdist = 99999.0
    idx = 0
    result = planet.veinGroups[0]
    for i, vg in enumerate(planet.veinGroups):
        dist = abs((pos - vg.pos).magnitude)
        if dist<bestdist:
            idx = i
            result = vg
            bestdist = dist
    return (idx, result)

def recalculateVein(planet=None):
    if planet == None: planet = GameMain.mainPlayer.planetData
    amounts = [0] * planet.veinAmounts.Length
    for vg in planet.veinGroups:
        i = int(vg.type)
        amounts[i] += vg.amount
    for i, v in enumerate(amounts):
        planet.veinAmounts[i] = v

def alterVeinGroup(planet, index, incr, newtype=None):
    import PlanetData, VeinData, Maths, AnimData, UnityEngine, LDB, EObjectType, PlanetModelingManager
    from UnityEngine import Quaternion, Vector3
    vg = planet.veinGroups[index]
    if vg.count == 0: 
        return False
    
    random2 = System.Random() if newtype != None else None
    
    nodeincr = int(float(incr) / float(vg.count))
    extra = (incr - (nodeincr * vg.count)) # extra amount to make number match due to round off
    count = 0
    total = 0
    
    for i, node in enumerate(planet.factory.veinPool):
        if node.groupIndex == index:
            newmodelid = node.modelId
            newcolliderId = node.colliderId
            newmodelIndex = node.modelIndex
            newproductId = node.productId
            if newtype != None:
                veinModelIndexs = PlanetModelingManager.veinModelIndexs
                veinModelCounts = PlanetModelingManager.veinModelCounts
                veinProducts = PlanetModelingManager.veinProducts
                veinProtos = PlanetModelingManager.veinProtos
                
                num18 = int(newtype)
                veinProto = PlanetModelingManager.veinProtos[num18]
                newmodelIndex = random2.Next(veinModelIndexs[num18], veinModelIndexs[num18] + veinModelCounts[num18])
                newproductId = veinProducts[num18]
                #print(node.id, newtype, num18, newmodelIndex, veinModelIndexs[num18], veinModelCounts[num18])
                
                #veinProto = LDB.veins.Select(int(newtype))
                anim = planet.factory.veinAnimPool[index]
                planet.factoryModel.gpuiManager.RemoveModel(node.modelIndex, node.modelId, True)
                newmodelid = planet.factoryModel.gpuiManager.AddModel(newmodelIndex, index, node.pos, Maths.SphericalRotation(node.pos, UnityEngine.Random.value * 360.0), False)

                newanim = AnimData(time = anim.time, prepare_length = anim.prepare_length, 
                    working_length = anim.working_length, state = num18, power = anim.power)
                    
                planet.factory.veinAnimPool[index] = newanim

                # purge collider
                if node.colliderId != 0:
                    if planet.physics != None:
                        planet.physics.RemoveLinkedColliderData(node.colliderId)
                newcolliderId = 0
                #create new from new vein
                for collider in veinProto.prefabDesc.colliders:
                    cd = collider.BindToObject(index, newcolliderId, EObjectType.Vein, node.pos, Quaternion.FromToRotation(Vector3.up, node.pos.normalized))
                    newcolliderId = planet.physics.AddColliderData(cd)

            newdata = VeinData(
                id = node.id,
                type = node.type if newtype == None else newtype,
                modelIndex = newmodelIndex,
                groupIndex = node.groupIndex,
                amount = node.amount + nodeincr + extra,
                productId = newproductId,
                pos = node.pos,
                minerCount = node.minerCount,
                minerId0 = node.minerId0,
                minerId1 = node.minerId1,
                minerId2 = node.minerId2,
                minerId3 = node.minerId3,
                modelId = newmodelid,
                colliderId = newcolliderId,
                minerBaseModelId = node.minerBaseModelId,
                minerCircleModelId0 = node.minerCircleModelId0,
                minerCircleModelId1 = node.minerCircleModelId1,
                minerCircleModelId2 = node.minerCircleModelId2,
                minerCircleModelId3 = node.minerCircleModelId3,
            )
            planet.factory.veinPool[i] = newdata
            extra = 0
            count += 1
            total += newdata.amount
            if newtype != None:
                planet.physics.RefreshColliders()
            planet.factory.RefreshVeinMiningDisplay(index, 0, 0);
            
            
            #print(node.id, node.type, node.groupIndex, node.amount, newdata.amount)
            
    planet.veinGroups[index] = PlanetData.VeinGroup(type=vg.type if newtype == None else newtype, pos=vg.pos, count=count, amount=total)
    recalculateVein(planet)
    return newtype != None
            
def ShowPlanet(planet, state):
    with VerticalScope(""):
        with HorizontalScope():
            state.show_near_vein = GUILayout.Toggle(getattr(state, 'show_near_vein', False), "Nearest Vein")
            GUILayout.FlexibleSpace()
            if not state.show_near_vein:
                state.veinidx = None
            elif GUILayout.Button(GUIContent('Refresh', 'Searches for nearest vein again')):
                state.veinidx = None
                
        if state.show_near_vein:
            import EVeinType, LDB, UIRoot
            if getattr(state, 'veinplanet', None) != planet:
                state.veinplanet = planet
                state.veinidx = None
                state.veinids = None                
            if getattr(state, 'veinidx', None) == None:
                idx, vein = closestVein(planet)
                state.veinidx = idx
            if getattr(state, 'veinids', None) == None:
                state.veindict = { int(x): x for x in System.Enum.GetValues(EVeinType) }
                state.veinproto = [x for x in LDB.veins if state.veindict[x.ID] != EVeinType.Oil ]
                state.veinids = [x.ID for x in state.veinproto ]
                
            if state.veinidx != None:                                    
                vein = planet.veinGroups[state.veinidx]
                ShowLabel("Index", state.veinidx)
                #

                if vein.type == EVeinType.Oil:
                    ShowLabel("Vein Type", vein.type)
                    GUILayout.Label('Cannot Edit Oil Resources')
                else:
                    index = state.veinids.index(int(vein.type))
                    veintooltip = lambda x: x.description
                    veinlambda = lambda x: x.name

                    with HorizontalScope():
                        with SmallerFont():
                            GUILayout.Label('Vein Type')
                        val = SpinBox(state.veinproto, index, label=veinlambda, tooltip=veintooltip, skip=False)
                        if val != index:
                            oldidx = state.veinids[index]
                            newidx = state.veinids[val]
                            alterVeinGroup(planet, state.veinidx, 0, newtype=state.veindict[newidx])
                            # TODO: hack to unload and reload models correctly
                            GameMain.instance.data.LeavePlanet()
                            GameMain.instance.data.ArrivePlanet(planet)
                            # TODO: Vein labeling bug fix. toggle off and back on
                            if UIRoot.instance.uiGame.dfVeinOn:
                                UIRoot.instance.uiGame.veinDetail.SetInspectPlanet(None)
                                UIRoot.instance.uiGame.veinDetail.SetInspectPlanet(planet)
                    
                    #newtype = EditList('Vein Type', vein, 'type', EVeinType, EVeinType.None)
                    ShowLabel("Position", vein.pos)
                    ShowLabel("Count", vein.count)
                    changed, newamount = ShowEditFloatValue('Amount', vein.amount, format="%.0f", incr=None, maxv=100000000, buttons=True)
                    if changed:
                        alterVeinGroup(planet, state.veinidx, newamount - vein.amount)
        
class GlobalInspect(BaseScreenEditor):
    def __init__(self, *args, **kwargs):
        BaseScreenEditor.__init__(self, *args, **kwargs)


    def Show(self, owner, _):
        guistate = owner.state.gui
        state = owner.state.screen_states["Global"]
        if GameMain.mainPlayer == None:
            return
       
        if getattr(state, "itembox", None) == None:
            state.itembox = ScrollView(height=500)
            state.show_items = False
            state.show_mecha = False
            state.show_history = False
            def getPlayer():
                return GameMain.mainPlayer            
            def getMecha():
                return GameMain.mainPlayer.mecha
            def getHistory():
                return GameMain.mainPlayer.mecha.lab.gameHistory
            #state.core = FloatCtrlWrapper("Energy", GameMain.mainPlayer.mecha, "coreEnergy", maxname="coreEnergyCap", showMax=True)
            state.core = FloatCtrlWrapper("Energy", getMecha, "coreEnergy", maxname="coreEnergyCap", showMax=True)
            state.attrs = [
                state.core,
                FloatCtrlWrapper("Sand", getPlayer, "sandCount", showAdd=True),
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
            
        with VerticalScope("", guistate.tinyskin.window):
            if Toggle(state, 'show_mecha', "Show Mecha"):
                for ctrl in state.attrs:
                    ShowEditFloatCtrl(ctrl.label, ctrl)
            
            if Toggle(state, 'show_history', "Show Globals"):
                for ctrl in state.history:
                    ShowEditFloatCtrl(ctrl.label, ctrl)
                if ShowButtonWithLabel("Add Research:", "+100000"):
                    GameMain.mainPlayer.mecha.lab.gameHistory.AddTechHash(100000)
                    
            if Toggle(state, 'show_galaxy', "Show Galaxy"):
                with HorizontalScope():
                    GUILayout.Label("Galaxy Screen")
                    GUILayout.FlexibleSpace()
                    if GUILayout.Button(GUIContent('Show', 'Show all resources. Can use a lot of memory and CPU when switching.')):
                        import galaxy; galaxy.showWindow()
                    if GUILayout.Button(GUIContent('Reload', 'Reloads Python Files from disk')):
                        import galaxy; galaxy.Reload()

            planet = GameMain.mainPlayer.planetData
            if planet != None:
                if Toggle(state, 'show_veins', "Show Planet"):
                    ShowPlanet(planet, state)
                    
            with VerticalScope(""):
                state.show_items = GUILayout.Toggle(state.show_items, "Items")
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
        
        import LDB, EntityData
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