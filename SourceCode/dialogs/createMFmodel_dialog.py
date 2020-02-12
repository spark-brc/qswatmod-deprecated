# -*- coding: utf-8 -*-

#******************************************************************************
#
# Freewat
# ---------------------------------------------------------
# Copyright (C) 2014 - 2015 Iacopo Borsi (iacopo.borsi@tea-group.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************
import os
import os.path
import posixpath
import ntpath
import shutil
import glob
import processing
from PyQt4.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt4.QtCore import *
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic

import numpy as np
# import pandas as pd
from qgis.core import QgsProject
import distutils.dir_util
from datetime import datetime


# import modules related flopy
import flopy
import flopy.utils.binaryfile as bf
from osgeo import gdal

from QSWATMOD.QSWATMOD import *
from QSWATMOD.QSWATMOD_dialog import QSWATMODDialog
from QSWATMOD.pyfolder import modflow_functions
from QSWATMOD.pyfolder import writeMF
from QSWATMOD.pyfolder import db_functions
from QSWATMOD.pyfolder import linking_process

#
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/createMFmodel.ui'))

class createMFmodelDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
    # def __init__(self, parent = None):
    #   super(createMFmodelDialog, self).__init__(parent)
    #   self.setupUi(self)


    #   self.pushButton_TxtInOut.clicked.connect(self.test)

    # def test(self):
    #   options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
    #   directory = QtGui.QFileDialog.getExistingDirectory(None,
    #       "QFileDialog.getExistingDirectory()",
    #       "self.dlg.Lakemodel_directory.text()", options)
    #   if directory:
    #       proj = QgsProject.instance()
    #       Project_Name = QFileInfo(proj.fileName()).baseName()
            
    #       Out_folder_temp = QgsProject.instance().readPath("./")
    #       Out_folder = os.path.normpath(Out_folder_temp + "/" + Project_Name + "/" + "existingModel" + "/" + "SWAT-MODFLOW")
    #       #distutils.dir_util.remove_tree(Out_folder)
    #       distutils.dir_util.copy_tree(directory, Out_folder)
    #       #self.dlg.Lakemodel_directory.setText(Out_folder)
    #       #self.DB_Update_Lakemodel_Directory()
    #       #time.sleep(1)
            
    #       # Check file extension
    #       file_check = os.path.abspath(os.path.join(Out_folder, "tr_041316.nam"))
        
    #       if os.path.isfile(file_check) is True: 
       
    #           msgBox = QMessageBox()
    #           msgBox.setText("The MODLFOW folder was succesfully copied")
    #           msgBox.exec_()
    #           self.lineEdit_TxtInOut.setText(Out_folder)
    #       else:
    #           msgBox = QMessageBox()
    #           msgBox.setText("There was a problem copying the folder")
    #           msgBox.exec_()


        #------------------------------------------------------------------------------------------------
        self.checkBox_ratio.setCheckState(Qt.Checked)
        self.pushButton_createMFfolder.clicked.connect(self.createMFfolder)
        self.pushButton_loadDEM.clicked.connect(self.loadDEM)
        self.checkBox_use_sub.toggled.connect(self.use_sub_shapefile)
        self.pushButton_create_MF_shps.clicked.connect(self.create_MF_shps)
        
        # -----------------------------------------------------------------------------------------------
        self.radioButton_aq_thic_single.toggled.connect(self.aqufierThickness_option)
        self.radioButton_aq_thic_uniform.toggled.connect(self.aqufierThickness_option)  
        self.radioButton_aq_thic_raster.toggled.connect(self.aqufierThickness_option)
        self.pushButton_aq_thic_raster.clicked.connect(self.loadBotElev)

        self.radioButton_hk_single.toggled.connect(self.hk_option)
        self.radioButton_hk_raster.toggled.connect(self.hk_option)      
        self.pushButton_hk_raster.clicked.connect(self.loadHK)

        self.comboBox_layerType.clear()
        self.comboBox_layerType.addItems([' - Convertible - ', ' - Confined - '])

        self.radioButton_ss_single.toggled.connect(self.ss_option)
        self.radioButton_ss_raster.toggled.connect(self.ss_option)
        self.pushButton_ss_raster.clicked.connect(self.loadSS)

        self.radioButton_sy_single.toggled.connect(self.sy_option)
        self.radioButton_sy_raster.toggled.connect(self.sy_option)
        self.pushButton_sy_raster.clicked.connect(self.loadSY)

        self.radioButton_initialH_single.toggled.connect(self.initialH_option)
        self.radioButton_initialH_uniform.toggled.connect(self.initialH_option)
        self.radioButton_initialH_raster.toggled.connect(self.initialH_option)
        self.pushButton_initialH_raster.clicked.connect(self.loadInitialH)

        self.pushButton_evt_raster.clicked.connect(self.loadEVT)
        
        self.pushButton_writeMF.clicked.connect(self.writeMF)
        self.DB_Pull_mf_inputs()  # instant call
        self.pushButton_reset.clicked.connect(self.DB_resetTodefaultVal)
        self.pushButton_create_mf_riv_shapefile.clicked.connect(self.create_mf_riv)

        # Retrieve info
        self.retrieve_ProjHistory_mf()

        # ----------------------------------------------------------------------
        QObject.connect(self.doubleSpinBox_delc, SIGNAL("valueChanged(double)"), self.esti_ngrids)
        QObject.connect(self.doubleSpinBox_delr, SIGNAL("valueChanged(double)"), self.esti_ngrids)
        QObject.connect(self.doubleSpinBox_delc, SIGNAL("valueChanged(double)"), self.set_delr)
        # ----------------------------------------------------------------------

    ##### QUESTIONS!! Is this function should be here too? ######
    def dirs_and_paths(self):
        global QSWATMOD_path_dict
        # project places
        Projectfolder = QgsProject.instance().readPath("./") 
        proj = QgsProject.instance() 
        Project_Name = QFileInfo(proj.fileName()).baseName()
        # definition of folders
        org_shps = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/org_shps")
        SMshps = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/SMshps")
        SMfolder = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "SWAT-MODFLOW")
        Table = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/Table")
        SM_exes = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "SM_exes")
        exported_files = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "exported_files")
        
        QSWATMOD_path_dict = {
                            'org_shps': org_shps,
                            'SMshps': SMshps,
                            'SMfolder': SMfolder,
                            'Table': Table,
                            'SM_exes': SM_exes,
                            'exported_files': exported_files}

        return QSWATMOD_path_dict

    # def dirs_and_paths(self):
    #   # project places
    #   Projectfolder = QgsProject.instance().readPath("./") 
    #   proj = QgsProject.instance() 
    #   Project_Name = QFileInfo(proj.fileName()).baseName()
                        
    #   # definition of folders
    #   org_shps = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/org_shps")
    #   SMshps = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/SMshps")
    #   SMfolder = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "SWAT-MODFLOW")
    #   Table = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "GIS/Table")
    #   SM_exes = os.path.normpath(Projectfolder + "/" + Project_Name + "/" + "SM_exes")
    #   return org_shps, SMshps, SMfolder, Table, SM_exes

    def DB_Pull_mf_inputs(self):
        db = db_functions.db_variable(self)      
        query = QtSql.QSqlQuery(db)
        query.exec_("SELECT user_val FROM mf_inputs WHERE parNames = 'ss' ")
        LK = str(query.first()) # What does LK do?
        self.lineEdit_ss_single.setText(str(query.value(0)))

    # ...
    def DB_push_mf_userVal(self):
        db = db_functions.db_variable(self)
        query = QtSql.QSqlQuery(db)
        query.prepare("UPDATE mf_inputs SET user_val = :UP1 WHERE parNames = 'ss'")
        query.bindValue (":UP1", self.lineEdit_ss_single.text())
        query.exec_() 

    def DB_resetTodefaultVal(self):
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        response = msgBox.question(
            self, 'Set to default?',
            "Are you sure you want to reset the current aquifer property settings to the default values?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if response == QMessageBox.Yes:
            db = db_functions.db_variable(self)      
            query = QtSql.QSqlQuery(db)
            query.exec_("SELECT default_val FROM mf_inputs WHERE parNames = 'ss' ")
            LK = str(query.first())
            self.lineEdit_ss_single.setText(str(query.value(0)))
            self.DB_push_mf_userVal()

    def retrieve_ProjHistory_mf(self):
        QSWATMOD_path_dict = self.dirs_and_paths()

        # Define folders and files
        SMfolder = QSWATMOD_path_dict['SMfolder']
        org_shps = QSWATMOD_path_dict['org_shps']
        SMshps = QSWATMOD_path_dict['SMshps']

        # retrieve DEM
        if os.path.isfile(os.path.join(org_shps, 'DEM.tif')):
            self.lineEdit_loadDEM.setText(os.path.join(org_shps, 'DEM.tif'))
        else:
            self.textEdit_mf_log.append("* Provide DEM raster file.")


    def createMFfolder(self):
        settings = QSettings()
        if settings.contains('/QSWATMOD/LastInputPath'):
            path = unicode(settings.value('/QSWATMOD/LastInputPath'))
        else:
            path = ''
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        title = "create MODFLOW folder"
        mffolder = QFileDialog.getExistingDirectory(None, title, path, options)
        mffolder_path = self.lineEdit_createMFfolder.setText(mffolder)
        return mffolder_path


    # navigate to the DEM raster from SWAT
    def loadDEM(self):
        QSWATMOD_path_dict = self.dirs_and_paths()
        settings = QSettings()
        if settings.contains('/QSWATMOD/LastInputPath'):
            path = unicode(settings.value('/QSWATMOD/LastInputPath'))
        else:
            path = ''
        title = "Choose DEM rasterfile"
        inFileName = QFileDialog.getOpenFileName(None, title, path, "Rasterfiles (*.tif);; All files (*.*)")

        if inFileName:
            settings.setValue('/QSWATMOD/LastInputPath', os.path.dirname(unicode(inFileName)))
            Out_folder = QSWATMOD_path_dict['org_shps']
            inInfo = QFileInfo(inFileName)
            inFile = inInfo.fileName()
            pattern = os.path.splitext(inFileName)[0] + '.*'
            baseName = inInfo.baseName()
    
            # inName = os.path.splitext(inFile)[0]
            inName = 'DEM'
            for f in glob.iglob(pattern):
                suffix = os.path.splitext(f)[1]
                if os.name == 'nt':
                    outfile = ntpath.join(Out_folder, inName + suffix)
                else:
                    outfile = posixpath.join(Out_folder, inName + suffix)                    
                shutil.copy(f, outfile)
        
            if os.name == 'nt':
                DEM = ntpath.join(Out_folder, inName + ".tif")
            else:
                DEM = posixpath.join(Out_folder, inName + ".tif")
            layer = QgsRasterLayer(DEM, '{0} ({1})'.format("DEM","SWAT"))
            # Put in the group
            root = QgsProject.instance().layerTreeRoot()
            swat_group = root.findGroup("SWAT") 
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            swat_group.insertChildNode(0, QgsLayerTreeLayer(layer))
            self.lineEdit_loadDEM.setText(DEM)
            return DEM


    def loadHK(self):
        writeMF.loadHK(self)
        writeMF.getHKfromR(self)

    def loadBotElev(self):
        writeMF.loadBotElev(self)
        writeMF.getBotfromR(self)

    def loadSS(self):
        writeMF.loadSS(self)
        writeMF.getSSfromR(self)

    def loadSY(self):
        writeMF.loadSY(self)
        writeMF.getSYfromR(self)

    def loadInitialH(self):
        writeMF.loadInitialH(self)
        writeMF.getIHfromR(self)

    def loadEVT(self):
        writeMF.loadEVT(self)
        writeMF.getEVTfromR(self)

    def use_sub_shapefile(self):
        from PyQt4 import QtCore, QtGui, QtSql
        QSWATMOD_path_dict = self.dirs_and_paths()

        try:
            input1 = QgsMapLayerRegistry.instance().mapLayersByName("sub (SWAT)")[0]
            #provider = layer.dataProvider()
            if self.checkBox_use_sub.isChecked():
                name = "mf_boundary"
                name_ext = "mf_boundary.shp"
                output_dir = QSWATMOD_path_dict['org_shps']
                # output_file = os.path.normpath(output_dir + "/" + name)

                mf_boundary = os.path.join(output_dir, name_ext)
                processing.runalg("qgis:dissolve", input1, True, None, mf_boundary)

                # defining the outputfile to be loaded into the canvas
                layer = QgsVectorLayer(mf_boundary, '{0} ({1})'.format("mf_boundary","MODFLOW"), 'ogr')

                # Put in the group
                root = QgsProject.instance().layerTreeRoot()
                mf_group = root.findGroup("MODFLOW")    
                QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))
                #subpath = layer.source()
                self.lineEdit_boundary.setText(mf_boundary)

        except:
            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
            msgBox.setWindowTitle("Error!")
            msgBox.setText("There is no 'sub' shapefile!")
            msgBox.exec_()
            # self.dlg.checkBox_default_extent.setChecked(0)
        # return layer

    def create_MF_grid(self): # Create fishnet based on user inputs
        QSWATMOD_path_dict = self.dirs_and_paths()
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_boundary (MODFLOW)")[0]

        ext = input1.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()

        delc = float(self.doubleSpinBox_delc.value())
        delr = float(self.doubleSpinBox_delr.value())

        nx = round((xmax - xmin) / delc)
        ny = round((ymax - ymin) / delr)
        ngrid = abs(int(nx*ny))

        MF_extent = "{a},{b},{c},{d}".format(a = xmin, b = xmax, c = ymin, d = ymax)

        #
        name = "mf_grid"
        name_ext = "mf_grid.shp"
        output_dir = QSWATMOD_path_dict['org_shps']
        output_file = os.path.normpath(output_dir + "/" + name)

        # running the acutal routine:
        processing.runalg("qgis:vectorgrid", MF_extent, delc,delr,0, output_file)

        # Define the outputfile to be loaded into the canvas
        mf_grid_shapefile =  os.path.join(output_dir, name_ext)
        layer = QgsVectorLayer(mf_grid_shapefile, '{0} ({1})'.format("mf_grid","MODFLOW"), 'ogr')
        
        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        mf_group = root.findGroup("MODFLOW")    
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))

    def create_grid_id_ii(self):
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
        provider = self.layer.dataProvider()

        if self.layer.dataProvider().fields().indexFromName("grid_id") == -1:
            field = QgsField("grid_id", QVariant.Int)
            provider.addAttributes([field])
            self.layer.updateFields()

            # I don't know
            grid_id = self.layer.dataProvider().fields().indexFromName("grid_id")
            feats = self.layer.getFeatures()
            self.layer.startEditing()
            for i, f in enumerate(feats):
                self.layer.changeAttributeValue(f.id(), grid_id, i+1)
            self.layer.commitChanges()
            time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
            self.textEdit_mf_log.append(time+' -> ' + "'grid_id' has been created ...")
        else:
            time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
            self.textEdit_mf_log.append(time+' -> ' + "'grid_id' already exists ...")
   
    # for elev, not using *.dis file. instead using DEM
    def create_row_col_elev_mf_ii (self):
        import math
        QSWATMOD_path_dict = self.dirs_and_paths()
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
        provider = self.layer.dataProvider()

        # from qgis.core import QgsField, QgsExpression, QgsFeature
        if self.layer.dataProvider().fields().indexFromName( "row" ) == -1:
            field = QgsField("row", QVariant.Int)
            provider.addAttributes([field])
            self.layer.updateFields()
        
        # Create Column field
        if self.layer.dataProvider().fields().indexFromName( "col" ) == -1:
            field = QgsField("col", QVariant.Int)
            provider.addAttributes([field])
            self.layer.updateFields()

        # Get the index numbers of the fields
        # elev_mean = self.layer.dataProvider().fields().indexFromName( "elev_mean" )
        row = provider.fields().fieldNameIndex("row")
        col = provider.fields().fieldNameIndex("col")

        # Change name
        for field in self.layer.pendingFields():
            if field.name() == 'elev_mean':
                self.layer.startEditing()
                idx = self.layer.fieldNameIndex(field.name())
                self.layer.renameAttribute(idx, "elev_mf")
                self.layer.commitChanges()

        # Get number of rows and of columns
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_boundary (MODFLOW)")[0]

        ext = input1.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()

        delc = float(self.doubleSpinBox_delc.value())
        delr = float(self.doubleSpinBox_delr.value())

        nx = math.ceil(abs(abs(xmax) - abs(xmin)) / delc)
        ny = math.ceil(abs(abs(ymax) - abs(ymin)) / delr) 
    
        # Get row and column lists
        iy = [] # row
        ix = [] # col
        for i in range(1, ny + 1):
            for j in range(1, nx + 1):
                ix.append(j)
                iy.append(i)

        # Get features (Find out a way to change attribute values using another field)
        feats = self.layer.getFeatures()
        self.layer.startEditing()

        # add row number
        for f, r, c in zip(feats, iy, ix):
            self.layer.changeAttributeValue(f.id(), row, r)
            self.layer.changeAttributeValue(f.id(), col, c)
            # self.layer.changeAttributeValue(f.id(), elev_mf, elev)                
            # self.layer.changeAttributeValue(f[grid_id] - 1, row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, col, c)
        self.layer.commitChanges()


    #  ======= Update automatically when 1:1 ratio is checked
    def set_delr(self, value):
        if self.checkBox_ratio.isChecked():
            self.doubleSpinBox_delr.setValue(value)

    # ======= Estimate number of grid cells
    def esti_ngrids(self):
        import math
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_boundary (MODFLOW)")[0]

        try:
            ext = input1.extent()
            xmin = ext.xMinimum()
            xmax = ext.xMaximum()
            ymin = ext.yMinimum()
            ymax = ext.yMaximum()

            delc = float(self.doubleSpinBox_delc.value())
            delr = float(self.doubleSpinBox_delr.value())
            if delc !=0 and delr !=0:
                nx = math.ceil(abs(abs(xmax) - abs(xmin)) / delc)
                ny = math.ceil(abs(abs(ymax) - abs(ymin)) / delr) 
                ngrid = abs(int(nx*ny))
            else:
                ngrid = ' '
        except:
            ngrid = ' '
        self.lcdNumber_numberOfgrids.display(unicode(ngrid))

    # ========== createMF_active
    def create_mf_act_grid(self):
        from PyQt4 import QtCore, QtGui, QtSql
        QSWATMOD_path_dict = self.dirs_and_paths()
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
        input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_boundary (MODFLOW)")[0]

        name = "mf_grid_active"
        name_ext = "mf_grid_active.shp"
        output_dir = QSWATMOD_path_dict['org_shps']

        # output_file = os.path.normpath(os.path.join(output_dir, name))
        # Select features by location
        processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 0)

        # Save just the selected features of the target layer
        mf_grid_act_shp = os.path.join(output_dir, name_ext)
        QgsVectorFileWriter.writeAsVectorFormat(input1, mf_grid_act_shp,
            "utf-8", input1.crs(), "ESRI Shapefile", 1)

        # Deselect the features
        processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 2)

        layer = QgsVectorLayer(mf_grid_act_shp, '{0} ({1})'.format("mf_act_grid","MODFLOW"), 'ogr')

        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        mf_group = root.findGroup("MODFLOW")    
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))


    def create_MF_shps(self):
        self.progressBar_mf.setValue(0)
        self.create_MF_grid()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'MODFLOW grid is created ...')
        self.progressBar_mf.setValue(30)
        QCoreApplication.processEvents() # it works as F5 !! Be careful to use this for long geoprocessing
        
        # Create grid_id
        self.create_grid_id_ii()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'MODFLOW grid id is added ...')
        self.progressBar_mf.setValue(40)
        QCoreApplication.processEvents()

        # Extract elevation
        self.getElevfromDem()
        self.progressBar_mf.setValue(50)
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'Extrating elevation info from DEM is done ... ...')
        QCoreApplication.processEvents()

        # Extract elevation
        self.create_row_col_elev_mf_ii()
        self.progressBar_mf.setValue(60)
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'Writing row and col ... ...')
        QCoreApplication.processEvents()

        # Get active cells
        self.create_mf_act_grid()
        self.progressBar_mf.setValue(70)
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'MODLFOW active grid is created ...')
        QCoreApplication.processEvents()

        self.mf_act_grid_delete_NULL()
        QCoreApplication.processEvents()

        self.cvtElevToR()
        QCoreApplication.processEvents()

        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.textEdit_mf_log.append(time+' -> ' + 'Done!')
        self.progressBar_mf.setValue(100)
        QCoreApplication.processEvents()

        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        msgBox.setWindowTitle("Created!")
        msgBox.setText("MODFLOW shapefiles were created!")
        msgBox.exec_()

    # sp 03-20-18 : Change input1 mf_act_grid to mf_grid  
    def getElevfromDem(self):
        from qgis.analysis import QgsZonalStatistics
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
        input2 = QgsMapLayerRegistry.instance().mapLayersByName("DEM (SWAT)")[0]
        provider = input2.dataProvider()
        rpath = provider.dataSourceUri()
        zoneStat = QgsZonalStatistics (input1, rpath, 'elev_', 1, QgsZonalStatistics.Mean)
        zoneStat.calculateStatistics(None)

    def cvtElevToR(self):
        QSWATMOD_path_dict = self.dirs_and_paths()

        delc = float(self.doubleSpinBox_delc.value())
        delr = float(self.doubleSpinBox_delr.value())

        extlayer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_act_grid (MODFLOW)")[0]

        # get extent
        ext = extlayer.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()
        extent = "{a},{b},{c},{d}".format(a=xmin, b=xmax, c=ymin, d=ymax)

        name = 'top_elev'
        name_ext = "top_elev.tif"
        output_dir = QSWATMOD_path_dict['org_shps']

        output_raster = os.path.join(output_dir, name_ext)
        processing.runalg(
            "gdalogr:rasterize",
            input1,
            "elev_mf",1,delc,delr,
            extent,
            False,5,"-9999",0,75,6,1,False,0,"",
            output_raster)

        # fileInfo = QFileInfo(output_raster)
        # path = fileInfo.filePath()
        # baseName = fileInfo.baseName()

        # for raster no 'ogr'
        layer = QgsRasterLayer(output_raster, '{0} ({1})'.format("top_elev","MODFLOW"))
        
        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        mf_group = root.findGroup("MODFLOW")    
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))


    def mf_act_grid_delete_NULL(self):
        layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_act_grid (MODFLOW)")[0]
        provider = layer.dataProvider()
        request =  QgsFeatureRequest().setFilterExpression('"elev_mf" IS NULL' )
        request.setSubsetOfAttributes([])
        request.setFlags(QgsFeatureRequest.NoGeometry)

        layer.startEditing()
        for f in layer.getFeatures(request):
            layer.deleteFeature(f.id())
        layer.commitChanges()

    def create_mf_riv(self):
        ### ============================================ why!!!!!!!!!!!!!!!!!!!!!!!!
        self.dlg = QSWATMODDialog()
        self.dlg.groupBox_river_cells.setEnabled(True) # not working
        self.dlg.radioButton_mf_riv2.setChecked(1) # not working
        ### ============================================        
        modflow_functions.mf_riv2(self)
        linking_process.river_grid(self)
        linking_process.river_grid_delete_NULL(self)
        linking_process.rgrid_len(self)
        linking_process.delete_river_grid_with_threshold(self)
        modflow_functions.rivInfoTo_mf_riv2_ii(self)
        modflow_functions.riv_cond_delete_NULL(self)
        writeMF.create_layer_inRiv(self)
        QCoreApplication.processEvents()

    #-------------------------------------------------------------------------------
    def aqufierThickness_option(self):
        # Single
        if self.radioButton_aq_thic_single.isChecked():
            self.lineEdit_aq_thic_single.setEnabled(True)
            self.lineEdit_aq_thic_uniform.setEnabled(False)
            self.lineEdit_aq_thic_raster.setEnabled(False)
            self.pushButton_aq_thic_raster.setEnabled(False)

        # Uniform
        elif self.radioButton_aq_thic_uniform.isChecked():
            self.lineEdit_aq_thic_uniform.setEnabled(True)
            self.lineEdit_aq_thic_single.setEnabled(False)
            self.lineEdit_aq_thic_raster.setEnabled(False)
            self.pushButton_aq_thic_raster.setEnabled(False)

        # Raster
        elif self.radioButton_aq_thic_raster.isChecked():
            self.lineEdit_aq_thic_raster.setEnabled(True)
            self.pushButton_aq_thic_raster.setEnabled(True) 
            self.lineEdit_aq_thic_single.setEnabled(False)
            self.lineEdit_aq_thic_uniform.setEnabled(False)

        # else:
        #   self.lineEdit_aq_thic_single.setEnabled(False)
        #   self.lineEdit_aq_thic_uniform.setEnabled(False)
        #   self.lineEdit_aq_thic_raster.setEnabled(False)
        #   self.pushButton_aq_thic_raster.setEnabled(False)    

    def hk_option(self):
        if self.radioButton_hk_single.isChecked():
            self.lineEdit_hk_single.setEnabled(True)
            self.lineEdit_vka.setEnabled(True)
            self.comboBox_layerType.setEnabled(True)
            self.lineEdit_hk_raster.setEnabled(False)
            self.pushButton_hk_raster.setEnabled(False)

        elif self.radioButton_hk_raster.isChecked():
            self.lineEdit_hk_raster.setEnabled(True)
            self.pushButton_hk_raster.setEnabled(True)
            self.lineEdit_vka.setEnabled(True)
            self.comboBox_layerType.setEnabled(True)
            self.lineEdit_hk_single.setEnabled(False)
        # else:
        #   self.lineEdit_hk_single.setEnabled(False)

    def ss_option(self):
        if self.radioButton_ss_single.isChecked():
            self.lineEdit_ss_single.setEnabled(True)
            self.lineEdit_ss_raster.setEnabled(False)
            self.pushButton_ss_raster.setEnabled(False)
        elif self.radioButton_ss_raster.isChecked():
            self.lineEdit_ss_raster.setEnabled(True)
            self.pushButton_ss_raster.setEnabled(True)
            self.lineEdit_ss_single.setEnabled(False)           

    def sy_option(self):
        if self.radioButton_sy_single.isChecked():
            self.lineEdit_sy_single.setEnabled(True)
            self.lineEdit_sy_raster.setEnabled(False)
            self.pushButton_sy_raster.setEnabled(False)
        else:
            self.lineEdit_sy_raster.setEnabled(True)
            self.pushButton_sy_raster.setEnabled(True)
            self.lineEdit_sy_single.setEnabled(False)           

    def initialH_option(self):
        if self.radioButton_initialH_single.isChecked():
            self.lineEdit_initialH_single.setEnabled(True)
            self.lineEdit_initialH_uniform.setEnabled(False)
            self.lineEdit_initialH_raster.setEnabled(False)
            self.pushButton_initialH_raster.setEnabled(False)

        elif self.radioButton_initialH_uniform.isChecked():
            self.lineEdit_initialH_single.setEnabled(False)
            self.lineEdit_initialH_uniform.setEnabled(True)
            self.lineEdit_initialH_raster.setEnabled(False)
            self.pushButton_initialH_raster.setEnabled(False)           

        else:
            self.lineEdit_initialH_single.setEnabled(False)
            self.lineEdit_initialH_uniform.setEnabled(False)
            self.lineEdit_initialH_raster.setEnabled(True)
            self.pushButton_initialH_raster.setEnabled(True)


    def writeMF(self):
        self.DB_push_mf_userVal()

        from QSWATMOD.pyfolder.writeMF import extentlayer
        self.textEdit_mf_log.append(" ")
        self.textEdit_mf_log.append("- Exporting MODFLOW input files...")
        
        # '''
        self.checkBox_mfPrepared.setChecked(0)
        self.progressBar_mf.setValue(0)

        # Bottom
        if (self.radioButton_aq_thic_single.isChecked() or self.radioButton_aq_thic_uniform.isChecked()):
            writeMF.createBotElev(self)
            self.progressBar_mf.setValue(10)
            QCoreApplication.processEvents()
        writeMF.cvtBotElevToR(self)
        self.progressBar_mf.setValue(20)
        QCoreApplication.processEvents()

        # HK
        if (self.radioButton_hk_raster.isChecked() and self.lineEdit_hk_raster.text()):
            writeMF.cvtHKtoR(self)
            self.progressBar_mf.setValue(30)
            QCoreApplication.processEvents()
        else:
            self.progressBar_mf.setValue(40)
            QCoreApplication.processEvents()

        # writeMF.cvtHKtoR(self)
        # self.progressBar_mf.setValue(40)
        # QCoreApplication.processEvents()
        
        # SS
        if (self.radioButton_ss_raster.isChecked() and self.lineEdit_ss_raster.text()):
            writeMF.cvtSStoR(self)
            self.progressBar_mf.setValue(60)
            QCoreApplication.processEvents()
        else:
            # writeMF.createSY(self)
            self.progressBar_mf.setValue(70)
            QCoreApplication.processEvents()        

        # SY
        if (self.radioButton_sy_raster.isChecked() and self.lineEdit_sy_raster.text()):
            writeMF.cvtSYtoR(self)
            self.progressBar_mf.setValue(80)
            QCoreApplication.processEvents()
        else:
            self.progressBar_mf.setValue(85)
            QCoreApplication.processEvents()
        # IH
        if (self.radioButton_initialH_single.isChecked() or self.radioButton_initialH_uniform.isChecked()):
            writeMF.createInitialH(self)
            self.progressBar_mf.setValue(90)
            QCoreApplication.processEvents()
        writeMF.cvtInitialHtoR(self)
        self.progressBar_mf.setValue(95)
        QCoreApplication.processEvents()

        # EVT
        if self.groupBox_evt.isChecked():
            if (self.radioButton_evt_raster.isChecked() and self.lineEdit_evt_raster.text()):
                writeMF.cvtEVTtoR(self)
                self.progressBar_mf.setValue(80)
                QCoreApplication.processEvents()
            else:
                self.progressBar_mf.setValue(85)
                QCoreApplication.processEvents()

        # '''
        writeMF.writeMFmodel(self)
        self.progressBar_mf.setValue(100)
        self.checkBox_mfPrepared.setChecked(1)
