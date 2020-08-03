import pymel.core as Pm
import maya.cmds as Mc
import os
import json
import subprocess
import traceback
from maya.api.OpenMaya import MGlobal as Omg
import maya.api.OpenMaya as Om
import sys

class FacsPicker(object):
    def __init__(self, strBasePath):
        self.strBasePathG = strBasePath
        self.lStrFiles = os.listdir(self.strBasePathG)
        #print self.lStrFiles[0]
        self.lStrActors = []
        self.strLocatorGroup = "MeshLocators"
        self.lStrCaps = []
        os.chdir(strBasePath + '\\' + self.lStrFiles[0])
        lStrPlugins = Pm.pluginInfo(q = True, listPlugins = True)
        if 'objExport' not in lStrPlugins:
            Pm.pluginInfo( 'objExport', edit=True)    
            Pm.loadPlugin( 'objExport')     

    def DrawGUI(self):
        if 'FACSgui' in Mc.lsUI(windows=True):
            Mc.deleteUI("FACSgui",window=True)
        self.windowGUI = Pm.window('FACSgui', title="FACS Picker", iconName='Short Name', widthHeight=(300, 55), resizeToFitChildren = True)
        Pm.columnLayout( adjustableColumn=True)
        self.optMenuCurrentActor = Pm.optionMenuGrp ( label=' Actor',w = 300, cc = self.Actorswitch)
        for strActor in self.lStrFiles:
            if '.mayaSwatches' not in strActor and 'Face Regions' not in strActor:
                if os.path.isfile(self.strBasePathG+'/'+strActor) == False:
                    Pm.menuItem(strActor)
                    self.lStrActors.append(strActor)

        self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
        self.txtScrollListScanFiles = Pm.textScrollList() 
        print self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans'
        self.strActorPath = os.listdir(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans')
        self.lStrScansPath = os.listdir(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans')
        self.lStrCaps = []
        for i in self.strActorPath:
            if 'scans' in i or 'Scans' in i:
                self.lStrCaps.append(i)
        self.lStrBaseObj = []
        for strScan in self.strActorPath:
            strScanPref = ''
            if '.obj' in strScan and '_partial' not in strScan and '_clean' not in strScan and '_tracker' not in strScan and '_aligned' not in strScan and '_transform' not in strScan and '_remesh' not in strScan and '_merged' not in strScan and '_wrap' not in strScan and '_solved' not in strScan and '_sculpt' not in strScan:
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_clean.obj') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'C'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_aligned.obj') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'A'
                if not os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_labeled.json') and os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_partial.json') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'P'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_labeled.json') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'L'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'R'
                strScan = strScanPref + '__' + strScan
                self.lStrBaseObj.append(strScan[:-4])
        self.txtScrollListScanFiles = Pm.textScrollList(self.txtScrollListScanFiles, removeAll = True, e = True)            
        self.txtScrollListScanFiles = Pm.textScrollList(self.txtScrollListScanFiles, append = self.lStrBaseObj, e = True, ams = True)
        Pm.separator()
        self.optMenuPresetQ = Pm.optionMenuGrp(label = 'Preset Selection', cc = self.PresetChanger)
        Pm.menuItem('None')
        Pm.menuItem('First Alignment')
        Pm.menuItem('Marker Debug')
        Pm.menuItem('Alignment Adjusts')
        Pm.menuItem('Final Alignment Polish')
        Pm.text('')
        self.checkBoxCheck1 = Pm.checkBoxGrp(numberOfCheckBoxes=2, labelArray2 = ['Clean','Aligned'])
        self.checkBoxCheck2 = Pm.checkBoxGrp(numberOfCheckBoxes=2, labelArray2 = ['Tracker/Partial','Game Mesh'])
        self.checkBoxCheck3 = Pm.checkBoxGrp(numberOfCheckBoxes=2, labelArray2 = ['Markers','Remesh'])
        Pm.text(' ')
        self.buttonLoad = Pm.button(label = 'Load', bgc = [.2,.6,.2], h =50, command = self.LoadIt)
        Pm.text('    ')
        Pm.separator()
        self.checkBoxGRIND = Pm.checkBoxGrp(numberOfCheckBoxes = 1, label = 'ENGAGE GRIND MODE', cc = self.Lockdown)
        self.buttonExport = Pm.button(label = 'Export', bgc = [.0, .4, .4], h = 50, command = self.StepItUp)
        Pm.text('  ')
        Pm.separator()
        self.forceRemesh = Pm.checkBoxGrp(numberOfCheckBoxes=1, label = 'Force Remesh')
        self.buttonEx = Pm.button(label = 'Run Remesher', h = 50, bgc = [.4, .3, .6], command = self.RunSppRemeshJob)
        Pm.setParent( '..' )
        Pm.showWindow( self.windowGUI )

    def Actorswitch(self, *args):
        self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
        self.strActorPath = os.listdir(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans')
        print self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans'
        os.chdir(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1])
        self.lStrBaseObj = []
        for strScan in self.strActorPath:
            strScanPref = ''
            if '.obj' in strScan and '_partial' not in strScan and '_clean' not in strScan and '_tracker' not in strScan and '_aligned' not in strScan and '_transform' not in strScan and '_remesh' not in strScan and '_merged' not in strScan and '_wrap' not in strScan and '_solved' not in strScan and '_sculpt' not in strScan:
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_clean.obj') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'C'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_aligned.obj') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'A'
                if not os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_labeled.json') and os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_partial.json') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'P'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_labeled.json') and not  os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'L'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScan[:-4]+'_remesh.obj'):
                    strScanPref += 'R'

                strScan = strScanPref + '__' + strScan
                self.lStrBaseObj.append(strScan[:-4])
            self.txtScrollListScanFiles = Pm.textScrollList(self.txtScrollListScanFiles, removeAll = True, e = True)            
            self.txtScrollListScanFiles = Pm.textScrollList(self.txtScrollListScanFiles, append = self.lStrBaseObj, e = True, ams = True)

    def PresetChanger(self, *args):
        nPresets = Pm.optionMenuGrp(self.optMenuPresetQ, q = True, sl = True)    

            #sets all checkbox presets

        if nPresets == 1:
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v2 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v2 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v2 = False)    
        if nPresets == 2:                                                                        
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v1 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v2 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v2 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v2 = False)    
        if nPresets == 3:                                                                        
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v1 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v2 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v1 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v2 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v1 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v2 = False)    
        if nPresets == 4:                                                                        
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v2 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v2 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v2 = False)    
        if nPresets == 5:                                                                        
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v2 = True)     
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v2 = True)      
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v1 = False)    
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, v2 = True)     

    def LoadIt(self, *args):
        lStrScrollListQ = Pm.textScrollList(self.txtScrollListScanFiles, q = True, si = True)
        lStrTruncFiles = []
        for strFile in lStrScrollListQ:
            strFile = strFile.split('__',1)[1]
            lStrTruncFiles.append(strFile)

        lStrScrollListQ = lStrTruncFiles
        #queries all checkboxes        

        fValue1 = Pm.checkBoxGrp(self.checkBoxCheck1, v1 = True, q = True)    
        fValue2 = Pm.checkBoxGrp(self.checkBoxCheck1, v2 = True, q = True)    
        fValue3 = Pm.checkBoxGrp(self.checkBoxCheck2, v1 = True, q = True)    
        fValue4 = Pm.checkBoxGrp(self.checkBoxCheck2, v2 = True, q = True)    
        fValue5 = Pm.checkBoxGrp(self.checkBoxCheck3, v1 = True, q = True)    
        fValue6 = Pm.checkBoxGrp(self.checkBoxCheck3, v2 = True, q = True)    

        if fValue1 == True:  

            #imports clean mesh file

            for strScrollListSel in lStrScrollListQ:
                self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
                if not Pm.objExists(strScrollListSel+'_clean_mesh'):
                    try:
                        lStrNewNodes = Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_clean.obj', returnNewNodes = True)
                    except:
                        Pm.warning(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_clean.obj  does not seem to exist!')
                    self.lXformsCleanMesh = Pm.ls(lStrNewNodes, type = Pm.nt.Transform)
                    Pm.rename(self.lXformsCleanMesh, strScrollListSel+'_clean_mesh')
                    if fValue2 == False:
                        Pm.spaceLocator(n = strScrollListSel + '_ws_loc')
                        Pm.parentConstraint(self.lXformsCleanMesh, strScrollListSel+'_ws_loc', mo = True)
                        Pm.select(cl = True)
                else:
                    Pm.warning('Confirm ' + strScrollListSel+'_clean_mesh not already in scene')
                try:
                    xformNloc = Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/temp/noseLoc.ma', returnNewNodes = True)
                    Pm.parent(strScrollListSel+'_clean_mesh', xformNloc)
                except:
                    pass

        if fValue2 == True:  

            #imports aligned mesh file

            for strScrollListSel in lStrScrollListQ:
                if not Pm.objExists(strScrollListSel+'_aligned_mesh'):
                    self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
                    try:
                        lStrAlignedNewNodes = Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_aligned.obj', returnNewNodes = True)
                    except:
                        Pm.warning(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_aligned.obj  does not seem to exist!')
                    try:
                        Pm.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0]+'_transform.ma')
                    except:
                        Pm.warning('No transform file!')
                    try:
                        self.lStrAlignedMesh = Pm.ls(lStrAlignedNewNodes, type = Pm.nt.Transform)
                        self.XformAlignedMesh = Pm.rename(self.lStrAlignedMesh, strScrollListSel+'_aligned_mesh')
                    except:
                        pass
                    if Pm.objExists(strScrollListSel+'_aligned_mesh') and Pm.objExists(strScrollListSel+'_ws_loc'):
                        Pm.parentConstraint(lStrScrollListQ[0]+'_aligned_mesh', strScrollListSel+'_ws_loc', mo = True)
                    else:
                        Pm.warning('Confirm '+strScrollListSel+'_aligned.obj not already in scene')
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/temp/noseLoc.ma'):
                    self.xformNloc = [node for node in Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/temp/noseLoc.ma', returnNewNodes = True) if isinstance(node, Pm.nt.Transform)][0]
                    Pm.parent(strScrollListSel+'_aligned_mesh', self.xformNloc)
                    self.lStrNoseLocatorName = Pm.ls(self.xformNloc, type = Pm.nt.Transform)
                    self.XformNoseLocator = Pm.rename(self.lStrNoseLocatorName, 'NoseLocator')

        if fValue3 == True:  

            #imports tracker/partial mesh or json if they exist

            for strScrollListSel in lStrScrollListQ:
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_partial.json'):
                    self.ImportMarkerSet()
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_tracker.obj'):
                    self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
                    Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_tracker.obj')
                elif os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_partial.obj'):
                    self.strCurrent = Pm.optionMenuGrp(self.optMenuCurrentActor, sl = True, q = True)
                    Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_partial.obj')
                elif not os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_tracker.obj')  and not os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_partial.obj'):
                    Pm.warning('No Tracker/Partial mesh available.')

        if fValue4 == True:  

            #Imports game mesh file

            if Pm.objExists('game_mesh'):
                pass
            else:
                lStrNewNodesGM = Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/gamemesh.obj', returnNewNodes = True)
                lStrGameMesh = Pm.ls(lStrNewNodesGM, type = Pm.nt.Transform)
                try:
                    Pm.rename(lStrGameMesh, 'game_mesh')
                except:
                    Pm.warning('no game mesh available')

        if fValue5 == True:  

            #Loads marker file

            for strScrollListSel in lStrScrollListQ:
                if not Pm.objExists(self.strLocatorGroup):
                    self.ImportMarkerSet()
                else:
                    Pm.warning('Markers already in scene')

        if fValue6 == True: 

            #Imports the remesh file

            for strScrollListSel in lStrScrollListQ:
                if not Pm.objExists(strScrollListSel+'_remesh'):
                    try:
                        lStrRemeshNewNodes = Pm.system.importFile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strScrollListSel+'_remesh.obj', returnNewNodes = True)
                        lStrRemesh = Pm.ls(lStrRemeshNewNodes, type = Pm.nt.Transform)
                        if Pm.objExists(lStrRemesh):
                            Pm.rename(lStrRemesh, strScrollListSel+'_remesh')
                        Mc.SelectAllGeometry()
                        lStrSel = Mc.ls(sl = True)
                        for strSelectionItem in lStrSel:
                            if '_remesh' not in strSelectionItem:
                                lStrSel.remove(strSelectionItem)
                        if fValue4 == True: 

                            #creates a blendshape for all shapes in scene if remesh and game_mesh are checked

                            try:
                                Pm.blendShape('Face_Blends', e = True, t = ('game_mesh', len(lStrSel), strScrollListSel+'_remesh', 1.0))
                                Pm.setAttr(strScrollListSel+'_remesh.visibility', 0)
                            except:
                                Pm.blendShape(strScrollListSel+'_remesh', 'game_mesh', n = 'Face_Blends')
                                Pm.setAttr(strScrollListSel+'_remesh.visibility', 0)
                    except:
                        Pm.warning('Remesh file for'+ strScrollListSel + ' does not exist')
                else:
                    Pm.warning('Confirm ' + strScrollListSel+'_remesh not already in scene') 

    def Walk(self, *args): 

        #steps through gui text scroll list

        try:
            lStrScrollListSelection = Pm.textScrollList(self.txtScrollListScanFiles, q = True, sii = True)
            Pm.textScrollList(self.txtScrollListScanFiles, dii = lStrScrollListSelection[0], e = True)
            Pm.textScrollList(self.txtScrollListScanFiles, e = True, sii = lStrScrollListSelection[0]+1)
        except:
            Pm.warning('No selections')

    def Lockdown(self, *args):
        fLockdownQ =  Pm.checkBoxGrp(self.checkBoxGRIND, v1 = True, q = True)  
        if fLockdownQ == True:

            # Locks everything for grind mode

            Pm.textScrollList(self.txtScrollListScanFiles, e = True, en = False)   
            Pm.button(self.buttonLoad, e = True, en = False)               
            Pm.setParent('..')                                        
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, en = False)         
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, en = False)         
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, en = False)         
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, en = False)         
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, en = False)         
            Pm.optionMenuGrp(self.optMenuCurrentActor, e = True, en = False) 
            Pm.optionMenuGrp(self.optMenuPresetQ, e = True, en = False)      

            try:
                Pm.button(self.buttonExport, e = True, label = 'Load Next',  bgc = [.0, .3, .5])
            except:
                pm.error('Button Change Failed')

        if fLockdownQ == False:

            # Unlocks everything for grind mode

            Pm.textScrollList(self.txtScrollListScanFiles, e = True, en = True)    
            Pm.button(self.buttonLoad, e = True, en = True)                 
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, en = True)         
            Pm.checkBoxGrp(self.checkBoxCheck1, e = True, en = True)          
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, en = True)          
            Pm.checkBoxGrp(self.checkBoxCheck2, e = True, en = True)          
            Pm.checkBoxGrp(self.checkBoxCheck3, e = True, en = True)            
            Pm.optionMenuGrp(self.optMenuCurrentActor, e = True, en = True)  
            Pm.optionMenuGrp(self.optMenuPresetQ, e = True, en = True) 

            try:
                Pm.button(self.buttonExport, e = True, label = 'Export', bgc = [.0, .4, .4])
            except:
                pm.error('Button Change Failed')            

    def StepItUp(self, *args): 
        strButtonName = Pm.button(self.buttonExport, q = True, label = True)
        if strButtonName == 'Export':
            self.FindExport()
        elif  strButtonName == 'Load Next':
            try: 
                self.FindExport(self) 
            except:
                traceback.print_exc()
            Mc.SelectAll()
            Pm.delete()
            self.Walk(self)
            self.LoadIt(self)

    def FindExport(self, *args):
        lStrScrollListQ = Pm.textScrollList(self.txtScrollListScanFiles, q = True, si = True)
        lStrTruncFiles = []
        for strFile in lStrScrollListQ:
            strFile = strFile.split('__',1)[1]
            lStrTruncFiles.append(strFile)

        lStrScrollListQ = lStrTruncFiles
                #if len(lStrScrollListQ) == 0:
                        #Pm.warning('You must select a scan in the list to continue')
                        #return

        #cleans out object sets
        try:
            if Pm.objExists(lStrScrollListQ[0]+'_clean_mesh') and Pm.objectType(lStrScrollListQ[0]+'_clean_mesh', i = 'objectSet'):
                Pm.delete(lStrScrollListQ[0]+'_clean_mesh')
        except:
            traceback.print_exc()

            #Determines whether to export aligned or clean mesh

        listNLocTrans = None
        listNLocRot = None  
        if Pm.objExists(lStrScrollListQ[0]+'_clean_mesh'):
            if not Pm.objectType(lStrScrollListQ[0]+'_clean_mesh', i = 'objectSet'):    
                listNTrans = Pm.getAttr(lStrScrollListQ[0]+'_clean_mesh.translate') 
                listNRot = Pm.getAttr(lStrScrollListQ[0]+'_clean_mesh.rotate')      
        elif Pm.objExists(lStrScrollListQ[0]+'_aligned_mesh'):                                 
            listNTrans = Pm.getAttr(lStrScrollListQ[0]+'_aligned_mesh.translate')    
            try:
                if Pm.objExists(self.XformNoseLocator):
                    listNLocRot = self.XformNoseLocator+'.rotate'
            except:
                Pm.warning('stinky')
            listNRot = Pm.getAttr(lStrScrollListQ[0]+'_aligned_mesh.rotate')    
            try:
                if Pm.objExists(self.XformNoseLocator):
                    listNLocTrans = self.XformNoseLocator+'.translate'            
                else:
                    Pm.warning ('no aligned or clean mesh in scene')
            except:
                Pm.warning('stinko')

            #exports mesh locators if they're in scene

        if Pm.objExists('MeshLocators') and len(Pm.listRelatives('MeshLocators', c = True)) > 0 and not Pm.objExists('partial_json'): 
            self.ExportMarkerSet()
        if Pm.objExists('partial_json'):
            self.ExportMarkerSet()
        elif listNTrans != Pm.dt.Vector([0,0,0]) or listNRot != Pm.dt.Vector([0,0,0]) or listNLocTrans != Pm.dt.Vector([0,0,0]) and listNLocTrans != None or listNLocRot != Pm.dt.Vector([0,0,0]) and listNLocRot != None: 
            if Pm.objExists(lStrScrollListQ[0]+'_clean_mesh'):
                self.cleanMesh = lStrScrollListQ[0]+'_clean_mesh'
                Pm.select(self.cleanMesh)
            if Pm.objExists(lStrScrollListQ[0]+'_aligned_mesh'):
                self.xformAlignedMesh = lStrScrollListQ[0]+'_aligned_mesh'
                Pm.select(self.xformAlignedMesh)

            #export aligned    
            print self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0]+'_aligned.obj'
            Pm.exportSelected(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0]+'_aligned.obj', type = 'OBJexport', options = 'groups=0;ptgroups=0;materials=1;smoothing=0;normals=0')
            Pm.select(cl = True)
            try:
                Pm.delete(lStrScrollListQ[0]+'_ws_loc_parentConstraint1')
            except:
                print 'failed to delete ' + lStrScrollListQ[0]+'_ws_loc_parentConstraint1'
            if Pm.objExists(lStrScrollListQ[0]+'_clean_mesh'):

                #Exports transform nodes 

                try:  
                    Pm.select(cl = True)
                    Pm.select(lStrScrollListQ[0]+'_ws_loc')
                    Pm.exportSelected(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0]+'_transform.ma', type = 'mayaAscii', force = True)
                    Pm.rename(lStrScrollListQ[0]+'_ws_loc', 'xform')
                    Pm.exportSelected(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0], type = 'mayaBinary', force = True)
                    Pm.rename('xform', lStrScrollListQ[0]+'_ws_loc')
                    Pm.parentConstraint(lStrScrollListQ[0]+'_clean_mesh', lStrScrollListQ[0]+'_ws_loc', mo = True)
                except:
                    Pm.warning('Scene has no ws_loc')
                Pm.select(cl = True)
            elif Pm.objExists(lStrScrollListQ[0]+'_aligned_mesh'):
                try:
                    Pm.select(cl = True)
                    Pm.select(lStrScrollListQ[0]+'_ws_loc')
                    Pm.exportSelected(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0]+'_transform.ma', type = 'mayaAscii')
                    Pm.rename(lStrScrollListQ[0]+'_ws_loc', 'xform')
                    Pm.exportSelected(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+lStrScrollListQ[0], type = 'mayaBinary')
                    Pm.rename('xform', lStrScrollListQ[0]+'_ws_loc')
                    Pm.parentConstraint(lStrScrollListQ[0]+'_aligned_mesh', lStrScrollListQ[0]+'_ws_loc',mo = True)
                except:
                    Pm.warning('Scene has no ws_loc')
                Pm.select(cl = True)

    def ImportMarkerSet(self):
        fv3 = Pm.checkBoxGrp(self.checkBoxCheck2, v1 = True, q = True)
        fv5 = Pm.checkBoxGrp(self.checkBoxCheck3, v1 = True, q = True)

        # Confirm the user has 1 selected object

        lStrScrollListQ = Mc.textScrollList(self.txtScrollListScanFiles, q = True, si = True)
        lStrTruncFiles = []
        for strFile in lStrScrollListQ:
            strFile = strFile.split('__',1)[1]
            lStrTruncFiles.append(strFile)        
        # We need strScrollListSel single selected target mesh
        lStrScrollListQ = lStrTruncFiles
        Mc.namespace(set=':')
        if fv5 == True:
            self.strLocatorGroup = 'MeshLocators'
            for strSelectedItem in lStrScrollListQ:
                Mc.select(strSelectedItem+'_clean_mesh')
                print self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strSelectedItem+'_markers.json'
                if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strSelectedItem+'_markers.json'):
                    json_file = open(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strSelectedItem+'_markers.json', 'r')

                else:
                    json_file = open(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strSelectedItem+'_markers.json', 'r')
                listPointList = json.load(json_file)
                json_file.close()
                listNewList = []
                for lStrEntry in listPointList:
                    strNodeName = lStrEntry[0]
                    strName, type = Mc.sphere(name=strNodeName, r=0.1)
                    Mc.setAttr(strName + '.translate', lStrEntry[1],lStrEntry[2],lStrEntry[3])
                    listNewList.append(strName)

                # Parent all created locators to the 'MeshLocators' group

                Mc.createNode('transform', name=self.strLocatorGroup, skipSelect=True, shared=True)
                Mc.select(listNewList)
                Mc.select(self.strLocatorGroup, add=True)
                Mc.parent()

        if fv3 == True:
            self.strLocatorGroup = 'partial_json'
            Mc.createNode('transform', name=self.strLocatorGroup, skipSelect=True, shared=True)
            for strSelectedItem in lStrScrollListQ:
                Mc.select(strSelectedItem+'_clean_mesh')
                json_file = open(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strSelectedItem+'_partial.json', 'r')
                listPointList = json.load(json_file)
                json_file.close()
                listNewList = []
                for xform in listPointList:
                    strNodeName = xform[0]
                    strName, type = Mc.sphere(name=strNodeName, r=0.1)
                    Mc.setAttr(strName + '.translate', xform[1],xform[2],xform[3])
                    listNewList.append(strName)

                # Parent all created locators to the 'MeshLocators' group

                Mc.createNode('transform', name=self.strLocatorGroup, skipSelect=True, shared=True)
                Mc.select(listNewList)
                Mc.select('partial_json', add=True)
                Mc.parent()


    def ExportMarkerSet(self):
        self.strLocatorGroup = "MeshLocators"
        lLControlMarkerList = []
        listFileName = Mc.textScrollList(self.txtScrollListScanFiles, q = True, si = True)
        for strName in listFileName:
            strPchzTarget = strName.split('__',1)[1]
            print strPchzTarget
            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strPchzTarget+'_markers.json'):
                userPrompt = Mc.confirmDialog( title='Export markers', message='Marker file exists. Overwrite?', button=['Yes','No'], defaultButton='No', cancelButton='No', dismissString='No')
                if userPrompt != 'Yes':
                    return
            listWorldKids = Mc.ls('|*')  
            v3 = Pm.checkBoxGrp(self.checkBoxCheck2, v1 = True, q = True)
            if v3 == True:
                self.strLocatorGroup = 'partial_json'
            if not Pm.objExists('MeshLocators'):
                self.strLocatorGroup = 'partial_json'
            for kid in listWorldKids:
                if 'psLocator' in kid:
                    Mc.parent(kid, self.strLocatorGroup)
            self.SaveCurrentSelectionList()
            Mc.select(self.strLocatorGroup + "|*")
            listSelectionList = Omg.getActiveSelectionList()
            self.RestoreSavedSelectionList()
            for index in range(listSelectionList.length()):
                mdpLocator = listSelectionList.getDagPath(index)
                mfntransLocator = Om.MFnTransform(mdpLocator)
                listNMarker_position = mfntransLocator.translation(Om.MSpace.kWorld)
                lLControlMarkerList.append([mdpLocator.partialPathName(),listNMarker_position.x,listNMarker_position.y,listNMarker_position.z])

            if len(strPchzTarget) != 0:
                if self.strLocatorGroup == 'MeshLocators':
                    strFile = self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strPchzTarget+'_markers.json'
                    json_file = open(strFile, 'w')
                    json.dump(lLControlMarkerList, json_file)
                    json_file.close()
                    print strFile
                    Mc.warning(listSelectionList.length().__str__()+ ' markers exported')
                elif self.strLocatorGroup == 'partial_json':
                    strFile = self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/'+strPchzTarget+'_partial.json'
                    json_file = open(strFile, 'w')
                    json.dump(lLControlMarkerList, json_file)
                    json_file.close()
                    print strFile
                    Mc.warning(listSelectionList.length().__str__()+ ' markers exported')

    def SaveCurrentSelectionList(self):
        self.savedSelectionList = Omg.getActiveSelectionList()

    def RestoreSavedSelectionList(self):
        Mc.select(clear=True)
        for iObject in range (0, self.savedSelectionList.length()):
            Mc.select(self.savedSelectionList.getDagPath(iObject), add=True)

    def RunSppRemeshJob(self, *args):
        strListPicker = Mc.textScrollList(self.txtScrollListScanFiles, q = True, si = True)
        lStrTruncFiles = []
        for strFile in strListPicker:
            strFile = strFile.split('__',1)[1]
            lStrTruncFiles.append(strFile)     
        strListPicker = lStrTruncFiles
        import os
        import SppRemesh
        reload(SppRemesh)
        if len(strListPicker)>6:
            nLenPicker = range(len(strListPicker))
            listNSixFaces = [nLenPicker[i:i+6] for i in range(0,len(nLenPicker),6)]
            for nFace in range(0, len(listNSixFaces)):
                listStrFaceName = []
                for strFaceName in listNSixFaces[nFace]:
                    listStrFaceName.append(strListPicker[strFaceName])
                    if Pm.checkBoxGrp(self.forceRemesh, v1 = True, q = True)  == True:
                        for extraFiles in listStrFaceName:
                            print self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_remesh.obj'
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_remesh.obj'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_remesh.obj')
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_wrap_1.obj'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_wrap_1.obj')                
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_wrap_2.obj'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_wrap_2.obj')
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_merged.obj'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_merged.obj')   
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_solved.obj'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_solved.obj')
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_barycentric.json'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_barycentric.json')
                            if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_labeled.json'):
                                os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_labeled.json')  
                                

                

                SppRemesh.RemeshJobMain(listStrFaceName)
        else:
            if Pm.checkBoxGrp(self.forceRemesh, v1 = True, q = True)  == True:
                for extraFiles in strListPicker:
                    if os.path.isfile(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_remesh.obj'):
                        os.remove(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_remesh.obj')
                    if os.path.isfile(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_wrap_1.obj'):
                        print '______________hell yea it is my dude______________'
                        os.remove(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_wrap_1.obj')                
                    if os.path.isfile(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_wrap_2.obj'):
                        os.remove(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_wrap_2.obj')
                    if os.path.isfile(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_merged.obj'):
                        os.remove(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_merged.obj')   
                    if os.path.isfile(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_solved.obj'):
                        os.remove(self.strBasePathG+'\\'+self.lStrActors[self.strCurrent-1]+'\\scans\\' + extraFiles+'_solved.obj')   
                        
                    if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_barycentric.json'):
                        os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_barycentric.json')
                    if os.path.isfile(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_labeled.json'):
                        os.remove(self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1]+'/scans/' + extraFiles+'_labeled.json')    
                           
                strCommandLine = self.strBasePathG+'/'+self.lStrActors[self.strCurrent-1] + ' remesher -All -partial scans\\' + strListPicker[0]
                os.system(strCommandLine)
                #popenMarkers.wait()           
                
            SppRemesh.RemeshJobMain(strListPicker)