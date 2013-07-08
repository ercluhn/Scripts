#special thanks to Joe Weidenbach and Paul Katsen

'''
Installation:
Copy this file into your maya scripts folder. Source the script. I used this code.

import elPoser2
reload (elPoser2)
run = elPoser2.poser()

Or you can just create a folder and place the .py in it, create another folder inside called "Characters" and run this script.

import sys
path = "C:\\your\file\path"
if not path in sys.path:
    sys.path.append(path)
import elPoser2
reload (elPoser2)
caller = elPoser2.poser()

Create a folder in the scripts directory called "Characters and another one called Images"

That's it, enjoy! :)
'''

import maya.cmds as cmds #imports maya.cmds
import cPickle
import os
import sys
import stat
import shutil #imports those things

class poser():	  
    def __init__ (self):
        # Initialize class Attributes
        self.values = [] #initializes self.values
        self.infoDict = {} #initializes self.infoDict
        self.getKeyableAttr = [] #initializes self.getKeyableAttr
        self.fileName = '' #initializes self.fileName
        self.fileNameQuery = '' #initializes self.fileNameQuery
        self.fileLoc = sys.modules[__name__].__file__.rpartition("\elPoser2.py")[0] #partitions from right
        print 'printing self.fileLoc', self.fileLoc
        listDir = os.listdir(self.fileLoc)#variable listDir
        print 'printing listDir', listDir
        if 'Characters' not in listDir: #Creates the folder "Characters" if not present
            os.makedirs(self.fileLoc +'/Characters')
        if 'Images' not in listDir:#Creates the folder "Images" if not present
            os.makedirs(self.fileLoc + '/Images')
        self.listDir = os.listdir(self.fileLoc + '/Characters') #initializes self.listDir
        self.poseToLoad = '' #initializes self.poseToLoad
        self.listToAdd = [] #initializes self.listToAdd
        self.folderName = '' #initializes self.folerName
        self.folders = os.listdir(self.fileLoc + '/Characters') #initializes self.folders

        # delete any UI if already open
        if cmds.window("ELP",exists=True):
            cmds.deleteUI("ELP",window=True)
        if cmds.window('welp', exists = True):
            cmds.deleteUI ('welp', window = True)
        if cmds.window('CharDelete', exists = True):
            cmds.deleteUI('CharDelete', window = True)
        # Define UI
        self.win = cmds.window("ELP",title = "Eric Luhn's Poser", widthHeight = (225,200),resizeToFitChildren=True) ## Notice the "ELP argument. It tags the UI with a string"		 
        self.layout = cmds.columnLayout(rowSpacing=5) ## rowSpacing argument replaces all of your calls to <cmds.text()>
        self.newCharName = cmds.textFieldGrp(label = 'New Char:',w = 255, columnAlign = (1,'left'), columnWidth = (1,50),
                                                text = 'Enter new character name')
        cmds.button(label = 'Create New Character',w = 255, command = self.newChar)
        cmds.text('         ')
        cmds.text('Characters---------------------------------------------------')
        cmds.setParent('..') #sets parent
        self.layoutB = cmds.columnLayout(rowSpacing = 5)
        self.folderName = cmds.textScrollList(numberOfRows=8, allowMultiSelection= False,h = 80, append = self.listDir, sc = self.refreshList)
        cmds.setParent('..') #sets parent
        cmds.columnLayout (rowSpacing = 5)
        cmds.button(label = 'Delete Character', width = 255, bgc = (.7,.2,.2), command = self.warningWindowB)
        cmds.text('    ')
        cmds.text('Poses---------------------------------------------------------')
        self.fileName = cmds.textFieldGrp(label="Pose Name:",w = 255,columnAlign=(1,"left"),columnWidth=(1,50),
                                               text = "Please enter desired file name") ## textField Grp comes with a label option
        cmds.text('   ')
        cmds.button(label='Save Pose',width=255, command = self.writeFile )
        cmds.text('             ')
        self.folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)
        self.listQuery = self.folderQuery
        self.listFiles = os.listdir(self.fileLoc + "/Characters/")
        if len(self.listFiles) > 0:
            self.picker = self.folderQuery
            self.listSubFiles = os.listdir(self.fileLoc + '/Characters/')
        else:
            self.picker = ''
            self.listSubFiles = os.listdir(self.fileLoc + '/Characters/')
        if not self.folderQuery:
            self.initialFiles = 'No character selected'
        else:	
            self.initialFiles = os.listdir(self.fileLoc + '/Characters/' + self.folderQuery)
        cmds.setParent('..')#sets parent
        self.refreshLayout = cmds.columnLayout (rowSpacing = 5, height = 200)
        self.poseToLoad = cmds.textScrollList(numberOfRows=8, allowMultiSelection= False, append = self.initialFiles, sc = self.refreshPic, en = False, height = 200)
        cmds.setParent('..')#sets parent
        self.imgParent = cmds.frameLayout(label = 'Preview', height = 165)
        self.posePic = cmds.iconTextButton(style = 'iconOnly', image1 = 'sphere.png', label = 'Pose Name', width = 255, height = 200)
        cmds.setParent('..')#sets parent
        cmds.button(label='Load Pose',width=255, command = self.readFile )
        cmds.text('   ')
        cmds.button(label = 'Delete Pose', width = 255, bgc = (.7,.2,.2), command = self.warningWindow)
        cmds.setParent('..')#sets parent
        # Draw UI
        cmds.showWindow(self.win)


    def writeFile(self,*args):
        self.infoDict = {} #redefines self.infoDict
        self.selection = cmds.ls(sl = True) #gets names of selected objects
        poseQuery = cmds.textFieldGrp(self.fileName, q = True, text = True) #queries the pose name text field
        charQuery = cmds. textScrollList(self.folderName, q = True, selectItem = True) #queries the folder name text scroll list

        if self.selection == []: #if selection is empty, raises a warning
            cmds.warning('Please make a selection!!')
        elif not poseQuery: #if pose is not named, raises a warning
            cmds.warning('Please name the pose!!')
        
        if not charQuery: #if a character is not selected, raises a warning
            cmds.warning('Please select a character!!')
    
        poses = os.listdir(self.fileLoc + '/Characters/'+ charQuery[0]) #gets files in directory
        poseFile =('POSE_' + poseQuery + '.txt') #gets pose name
        if poseFile in poses: # if a file with the same name already exists, raises a warning.
            cmds.warning('There is already a pose with that name!!')
            return False
        else: #else: runs writeFile
            cmds.select(cl=True)	#clears selection
            self.outputDict()
            # Get file name from user and write to file
            self.fileNameQuery = cmds.textFieldGrp(self.fileName,query=True,text=True) #queries the file name
            if (self.fileNameQuery =='') or (self.fileNameQuery == 'Please enter desired file name'):
                cmds.warning('Please name the file!') #if the text box is empy, requests input.
            else:
                self.folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)  #Queries the text scroll list for character name
                self.listFiles = os.listdir(self.fileLoc + "/Characters") #lists files in the characters directory
                if not self.folderQuery: #if there's nothing selected, raises a warning
                    cmds.warning('Select a character!!')
                else:
                    self.listSubFiles = os.listdir(self.fileLoc + '/Characters/' + self.folderQuery[0]) #lists the files in the character folder
                    self.listToAdd = [] #defines listToAdd
                    cmds.textScrollList(self.poseToLoad, e= True, removeAll = True)  #empties the textScrollList
                    with open(self.fileLoc + '/Characters/' +self.folderQuery[0] + '/POSE_' + self.fileNameQuery + '.txt', "w+") as fileOpen: #opens the file
                        fileOpen.write(cPickle.dumps (self.infoDict)) #dumps cpickle into file
                        fileOpen.close() #closes file
                        charQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True) #Queries the character name
                        poseQuery = cmds.textFieldGrp(self.fileName, q = True, text = True) #queries the pose name
                        picName = (self.fileLoc + '/Images/'+ charQuery[0] + '/POSE_' + poseQuery) # defines pic name
                        picNameB = (picName) #is useless
                        cmds.playblast(format  = 'image', frame = 1, f = picNameB) #creates image for preview
                        self.listDir = os.listdir(self.fileLoc + "/Characters/" + self.folderQuery[0]) # lists the directory
                # Update option Menu
                #if item is not in the list, adds it to directory
            if not self.folderQuery: 
                cmds.warning('Please select a character!!')
            else:    
                for items in os.listdir(self.fileLoc  + "/Characters/"+ self.folderQuery[0]):# for every item in the pose directory
                    if items not in self.listToAdd:#if the item is not in the list to add
                        self.listToAdd.append(items) #adds it to the list
                        cmds.deleteUI(self.poseToLoad) # delete the UI element
                        self.poseToLoad = cmds.textScrollList(parent = self.refreshLayout, numberOfRows=8, allowMultiSelection= False, append = self.listToAdd, sc = self.refreshPic, en = True) #recreates the UI element
                    else:
                        cmds.warning('There is already a pose with that name!') #raises a warning
            if not self.folderQuery: 
                cmds.warning('Please Select a character') #raises a warning

    def outputDict (self, *args):	    
        for item in self.selection:  
            self.getKeyableAttr = cmds.listAttr(item,k = True) #defines list of keyable attributes
            self.lockedAttr = cmds.listAttr(item, l = True) #gets locked attributes
            for key in self.getKeyableAttr:
                rar = cmds.connectionInfo((item +'.' +key), isDestination = True) #grabs attributes with incoming connections
                if rar == False: #if attribute doesn't have an incoming connection, continues
                    if not self.lockedAttr: #if there are no locked attributes, defines as empty
                        self.lockedAttr = ['empty']
                    elif key not in self.lockedAttr: #if it's not in locked attributes, 
                        self.infoDict[item+"."+key] = cmds.getAttr(item+"."+key) #adds attributes to dictionary with their values		


    def readFile(self,*args): #read file
        self.infoDict = {}
        self.folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)
        if not self.folderQuery :
            cmds.warning('Please select a character!!')
        elif self.folderQuery:
            self.listFiles = os.listdir(self.fileLoc + "/Characters")
            self.poseName = cmds.textScrollList(self.poseToLoad, q= True, selectItem=True)
            self.listSubFiles = os.listdir(self.fileLoc + '/Characters/' + self.folderQuery[0])
            if self.poseName:
                with open(self.fileLoc + '/Characters/' + self.folderQuery[0] + '/' + self.poseName[0], 'r') as fileOpen:
                    sData = fileOpen.read()
                    self.infoDict = cPickle.loads(sData)
                    for key in self.infoDict.keys():
                        cmds.setAttr(key,self.infoDict[key]) 
            else: 
                cmds.warning ('Please select a pose to load!!')


    def refreshList (self, *args):
        cmds.deleteUI(self.poseToLoad)
        self.folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True, en = True)
        self.listFiles = os.listdir(self.fileLoc + "/Characters")
        self.listSubFiles = os.listdir(self.fileLoc + '/Characters/' + self.folderQuery[0])
        self.listToAdd = []
        self.noPoses = 'No saved poses'
        if not os.listdir(self.fileLoc + '/Characters/' + self.folderQuery[0]):
            self.poseToLoad = cmds.textScrollList(parent = self.refreshLayout, numberOfRows=8, allowMultiSelection= False, append = self.noPoses, sc = self.refreshPic, en = False, h = 200)
        else:	
            self.poseToLoad = cmds.textScrollList(parent = self.refreshLayout, numberOfRows=8, allowMultiSelection= False, append = self.initialFiles, sc = self.refreshPic, en = True, h = 200)
        #if item is not in the list, adds it to directory
        for items in self.listSubFiles:
            if items not in self.listToAdd:
                self.listToAdd.append(items)
                cmds.textScrollList(self.poseToLoad, e= True, removeAll = True)
                cmds.textScrollList(self.poseToLoad, e= True, append = self.listToAdd) #if item is not in the list, adds it to directory
            else:
                cmds.warning('There is already a pose with that name!')


    def newChar (self, *args):
        charName = cmds.textFieldGrp(self.newCharName, q = True, text = True)
        if (charName == '') or (charName == 'Enter new character name'):
            cmds.warning ('Please name the character!')
        else:
            directory = (self.fileLoc + '/Characters/' + charName)
            directoryB = (self.fileLoc + '/Images/' + charName)
            if not os.path.exists(directory):
                os.makedirs(directory)
                os.makedirs(directoryB)
            self.folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)
            self.listSubFiles = os.listdir(self.fileLoc + "/Characters")
            self.listToAdd = []
            cmds.textScrollList(self.folderName, e= True, removeAll = True)
             #if item is not in the list, adds it to directory
            for items in self.listSubFiles:
                if items not in self.listToAdd:
                    self.listToAdd.append(items)
                    cmds.textScrollList(self.folderName, e= True, removeAll = True, en = True)
                    cmds.textScrollList(self.folderName, e= True, append = self.listToAdd, en = True) #if item is not in the list, adds it to directory
                else:
                    cmds.warning('There is already a character with that name!')


    def deletePose (self,*args):
        self.listToAdd = []
        charQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)
        poseQuery = cmds.textScrollList(self.poseToLoad, q = True, selectItem = True)
        if not charQuery:
            cmds.warning('Please select a character!!')
        elif not poseQuery:
            cmds.warning('Please select a pose to delete!!')
        else:
            os.remove(self.fileLoc + '/Characters/' + charQuery[0] + '/' + poseQuery[0] )
            poseName =(self.fileLoc + '/Images/' + charQuery[0] + '/' + poseQuery[0] )
            imageName =(poseName.rpartition ('txt'))
            os.remove(imageName[0] + '0000.iff')
            self.refreshList()
        cmds.deleteUI('welp', window = True)	

    def deleteChar (self,*args):
        self.charQuery = cmds.textScrollList(self.folderName,q = True, selectItem = True)
        self.strChar = str(self.charQuery[0])
        print 'printing strChar', self.strChar
        if not self.charQuery:
            cmds.warning('Please select a character to delete!')
        else:
            shutil.rmtree(self.fileLoc + '/Characters/' + self.strChar)
            shutil.rmtree(self.fileLoc + '/Images/' + self.strChar)
        cmds.deleteUI(self.folderName)
        self.listDir = os.listdir(self.fileLoc + '/Characters') #initializes self.listDir
        if not self.listDir:
            self.folderName = cmds.textScrollList(parent = self.layoutB, numberOfRows=8, allowMultiSelection= False,h = 80, append = 'No Characters', sc = self.refreshList, en = False)
        else:
            self.folderName = cmds.textScrollList(parent = self.layoutB, numberOfRows=8, allowMultiSelection= False,h = 80, append = self.listDir, sc = self.refreshList)
        if cmds.window('CharDelete', exists = True):
            cmds.deleteUI('CharDelete', window = True)	


    def refreshPic (self, *args):
        cmds.deleteUI(self.posePic)
        poseQuery = cmds.textScrollList(self.poseToLoad, q = True, selectItem = True)
        picName = (self.fileLoc + '/Images/'+ self.folderQuery[0] + '/' + poseQuery[0])
        len (picName)
        picNameB = (picName.rpartition('.txt')[0] + '.0000.iff')
        self.posePic = cmds.iconTextButton(parent = self.imgParent ,style = 'iconOnly', image1 = picNameB, label = 'Pose Name', width = 255, height = 100)

    def deleteUI(self, *args):
        self.deleteIT = cmds.deleteUI('welp', window = True)


    def warningWindow (self, *args):
        if cmds.window("welp",exists=True):
            cmds.deleteUI("welp",window=True)
        poseQuery = cmds.textScrollList(self.poseToLoad, q = True, selectItem = True)
        if not poseQuery:
            cmds.warning ('Please select a character to delete!!')
        else:
            self.deleteWarning = cmds.window ('welp', title = 'WARNING!!')
            deleteLayout = cmds.columnLayout (rowSpacing = 5)
            cmds.iconTextButton (style = 'iconOnly', image1 = 'pointConstraint.svg', height = 200, width = 200, command = self.deletePose)
            cmds.button(label = 'Close', command = self.deleteUI)
            cmds.showWindow(self.deleteWarning)

    def warningWindowB (self, *args):
        if cmds.window("CharDelete",exists=True):
            cmds.deleteUI("CharDelete",window=True)
        folderQuery = cmds.textScrollList(self.folderName, q = True, selectItem = True)
        if not folderQuery:
            cmds.warning('Please select a character to delete!!')
        else:
            self.deleteWarningB = cmds.window('CharDelete', title = 'WARNING!!')
            deleteLayout = cmds.columnLayout (rowSpacing = 5)
            cmds.iconTextButton(style = 'iconOnly', image1 = 'pointConstraint.svg', height = 200, width = 200, command = self.deleteChar)
            cmds.button(label = 'Close', command = self.deleteUI)
            cmds.showWindow(self.deleteWarningB)		
