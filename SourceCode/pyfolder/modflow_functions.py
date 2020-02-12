import os
import os.path
from PyQt4.QtCore import *
from PyQt4.QtGui import * # @UnusedWildImport
import processing
from qgis.core import (QgsVectorLayer, QgsField,
                       QgsMapLayerRegistry, QgsFeatureIterator, QgsVectorFileWriter,
                       QgsProject, QgsLayerTreeLayer)
import glob
import posixpath
import ntpath
import shutil
from datetime import datetime
from PyQt4.QtCore import QVariant


def MF_grid(self):  # Create fishnet based on MODFLOW dis file
    QSWATMOD_path_dict = self.dirs_and_paths()

    # User inputs for coordinate origins at North-West
    x_origin = self.dlg.lineEdit_x_coordinate.text()
    y_origin = self.dlg.lineEdit_y_coordinate.text()

    # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nrow = int(data[0][1])
        ncol = int(data[0][2])
        delr = float(data[2][1])  # cell width along rows (y spacing)
        delc = float(data[3][1])  # cell width along columns (x spacing)

        # Calculate MODFLOW extent
        x_right = (float(x_origin) + (ncol * delc) - delc)
        y_lower = (float(y_origin) - (nrow * delr) + delr)
        MF_extent = "{a},{b},{c},{d}".format(a=x_origin, b=x_right, c=y_lower, d=y_origin)

    #
    name = "mf_grid"
    name_ext = "mf_grid.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file = os.path.normpath(output_dir + "/" + name)

    # running the acutal routine:
    processing.runalg("qgis:vectorgrid", MF_extent, delr, delc, 0, output_file)

    # Define the outputfile to be loaded into the canvas
    mf_grid_shapefile = os.path.join(output_dir, name_ext)

    layer = QgsVectorLayer(mf_grid_shapefile, '{0} ({1})'.format("mf_grid", "MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    mf_group = root.findGroup("MODFLOW")
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))

### I don't know how to retrieve values. 'NoneType' object is not iterable
# def read_dis_MF(self):
#   org_shps, SMshps, SMfolder, Table, SM_exes = self.dirs_and_paths()

#   # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
#   for filename in glob.glob(str(SMfolder)+"/*.dis"):
#       with open(filename, "r") as f:
#           data = []
#           for line in f.readlines():
#               if not line.startswith("#"):
#                   data.append(line.replace('\n', '').split())
#       nrow = int(data[0][1])
#       ncol = int(data[0][2])
#       delr = float(data[2][1]) # is the cell width along rows (y spacing)
#       delc = float(data[3][1]) # is the cell width along columns (x spacing).
#       return nrow, ncol, delr, delc


def create_grid_id(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    if self.layer.dataProvider().fields().indexFromName("grid_id") == -1:
        field = QgsField("grid_id", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()

        # I don't know
        # grid_id = self.layer.dataProvider().fields().indexFromName("grid_id")
        grid_id = provider.fields().indexFromName("grid_id")
        feats = self.layer.getFeatures()
        self.layer.startEditing()
        for i, f in enumerate(feats):
            self.layer.changeAttributeValue(f.id(), grid_id, i+1)
        self.layer.commitChanges()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'grid_id' has been created ...")
    else:
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'grid_id' already exists ...")


def create_row(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
    # self.dlg.textEdit_sm_link_log.append(time+' -> ' + 'Creating rows and columns is done ...')

    # from qgis.core import QgsField, QgsExpression, QgsFeature
    if self.layer.dataProvider().fields().indexFromName("row") == -1:
        field = QgsField("row", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()

        # Get the index numbers of the fields
        grid_id = self.layer.dataProvider().fields().indexFromName("grid_id")
        row = provider.fields().fieldNameIndex("row")

        # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
        for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
            with open(filename, "r") as f:
                data = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        data.append(line.replace('\n', '').split())
            nrows = int(data[0][1])
            ncols = int(data[0][2])

        # Get row and column lists
        iy = []  # row
        # ix = [] # col
        for i in range(1, nrows + 1):
            for j in range(1, ncols + 1):
                # ix.append(j)
                iy.append(i)

        # Get features (Find out a way to change attribute values using another field)
        feats = self.layer.getFeatures()
        self.layer.startEditing()

        # add row number
        for f, r in zip(feats, iy):
            self.layer.changeAttributeValue(f.id(), row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, col, c)
        self.layer.commitChanges()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'row number' has been created ...")
    else:
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'row number' already exists ...")


def create_col(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # Create Column field
    if self.layer.dataProvider().fields().indexFromName("col") == -1:
        field = QgsField("col", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()

        # Get the index numbers of the fields
        grid_id = self.layer.dataProvider().fields().indexFromName("grid_id")
        col = provider.fields().fieldNameIndex("col")

        # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
        for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
            with open(filename, "r") as f:
                data = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        data.append(line.replace('\n', '').split())
            nrows = int(data[0][1])
            ncols = int(data[0][2])

        # Get row and column lists
        ix = []  # col
        for i in range(1, nrows + 1):
            for j in range(1, ncols + 1):
                ix.append(j)

        # Get features (Find out a way to change attribute values using another field)
        feats = self.layer.getFeatures()
        self.layer.startEditing()

        # add row number
        for f, c in zip(feats, ix):
            self.layer.changeAttributeValue(f.id(), col, c)
            # self.layer.changeAttributeValue(f[grid_id] - 1, row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, col, c)
        self.layer.commitChanges()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'column number' has been created ...")
    else:
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'column number' already exists ...")


def create_elev_mf(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # Create Elevation field
    if self.layer.dataProvider().fields().indexFromName("elev_mf") == -1:
        field = QgsField("elev_mf", QVariant.Double, 'double', 20, 5)
        provider.addAttributes([field])
        self.layer.updateFields()

        # Get the index numbers of the fields
        grid_id = self.layer.dataProvider().fields().indexFromName("grid_id")
        elev_mf = provider.fields().fieldNameIndex("elev_mf")

        # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
        for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
            with open(filename, "r") as f:
                data = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        data.append(line.replace('\n', '').split())

        # Get an elevation list from discretiztion file
        ii = 5  # Starting line
        elev_mfs = []
        while data[ii][0] != "INTERNAL":
            for jj in range(len(data[ii])):
                elev_mfs.append(float(data[ii][jj]))
            ii += 1

        # Get features (Find out a way to change attribute values using another field)
        feats = self.layer.getFeatures()
        self.layer.startEditing()

        # add row number
        for f, elev in zip(feats, elev_mfs):
            self.layer.changeAttributeValue(f.id(), elev_mf, elev)
            # self.layer.changeAttributeValue(f[grid_id] - 1, row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, col, c)
        self.layer.commitChanges()
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + 'Elevation info from *.dis file was extracted ...')
    else:
        time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        self.dlg.textEdit_sm_link_log.append(time+' -> ' + "'elev_mf' already exists ...")

# Option 1
# Select river cells based on MODFLOW river package info
def mf_riv1(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # Find .dis file and read number of river cells
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.riv"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nRiv = int(data[0][0])

    riv_pac_row = []
    riv_pac_col = []

    # Skip two lines in Riv package and get row and col
    for i in range(2, nRiv+2):
        riv_pac_row.append(int(data[i][1]))
        riv_pac_col.append(int(data[i][2]))

    #
    feats = self.layer.getFeatures()
    riv_matched = []

    for f in feats:
        rowNo = f.attribute("row")
        colNo = f.attribute("col")
        # rowNo = f.attribute["row"]
        # colNo = f.attribute["col"]
        for i in range(len(riv_pac_row)):
            if ((rowNo == riv_pac_row[i]) and (colNo == riv_pac_col[i])):
                riv_matched.append(f.id())
    self.layer.setSelectedFeatures(riv_matched)

    name = "mf_riv1"
    name_ext = "mf_riv1.shp"
    output_dir = QSWATMOD_path_dict['org_shps']

    # Save just the selected features of the target layer
    mf_riv_shapefile = os.path.join(output_dir, name_ext)
    QgsVectorFileWriter.writeAsVectorFormat(
        input1, mf_riv_shapefile,
        "utf-8", input1.crs(), "ESRI Shapefile", 1)

    # Deselect the features
    self.layer.removeSelection()

    layer = QgsVectorLayer(mf_riv_shapefile, '{0} ({1})'.format("mf_riv1","MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    swat_group = root.findGroup("MODFLOW")  
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    swat_group.insertChildNode(0, QgsLayerTreeLayer(layer))
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)


def create_riv_info(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv1 (MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # from qgis.core import QgsField, QgsExpression, QgsFeature
    if self.layer.dataProvider().fields().indexFromName("riv_stage") == -1:
        field = QgsField("riv_stage", QVariant.Double, 'double', 20, 5)
        provider.addAttributes([field])
        self.layer.updateFields()
    
    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName("riv_cond") == -1:
        field = QgsField("riv_cond", QVariant.Double, 'double', 20, 5)
        provider.addAttributes([field])
        self.layer.updateFields()

    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName( "riv_bot" ) == -1:
        field = QgsField("riv_bot", QVariant.Double, 'double', 20, 5)
        provider.addAttributes([field])
        self.layer.updateFields()

    # Get the index numbers of the fields
    riv_stage = provider.fields().fieldNameIndex("riv_stage")
    riv_cond = provider.fields().fieldNameIndex("riv_cond")
    riv_bot = provider.fields().fieldNameIndex("riv_bot")

    # Find .riv file and read number of river cells
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.riv"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nRiv = int(data[0][0])

    riv_pac_row = []
    riv_pac_col = []
    riv_pac_stage = []
    riv_pac_cond = []
    riv_pac_bot = []

    # Skip two lines in Riv package and get row and col
    for i in range(2, nRiv+2):
        riv_pac_row.append(int(data[i][1]))
        riv_pac_col.append(int(data[i][2]))
        riv_pac_stage.append(float(data[i][3]))
        riv_pac_cond.append(float(data[i][4]))
        riv_pac_bot.append(float(data[i][5]))
    #
    feats = self.layer.getFeatures()
    self.layer.startEditing()

    # add riv_info based on row and column numbers
    for f in feats:
        rowNo = f.attribute("row")
        colNo = f.attribute("col")
        for i in range(len(riv_pac_row)):
            if ((rowNo == riv_pac_row[i]) and (colNo == riv_pac_col[i])):
                self.layer.changeAttributeValue(f.id(), riv_stage, riv_pac_stage[i])
                self.layer.changeAttributeValue(f.id(), riv_cond, riv_pac_cond[i])              
                self.layer.changeAttributeValue(f.id(), riv_bot, riv_pac_bot[i])
    self.layer.commitChanges()

# Option 2
def mf_riv2(self):
    from PyQt4 import QtCore, QtGui, QtSql
    QSWATMOD_path_dict = self.dirs_and_paths()
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    input2 = QgsMapLayerRegistry.instance().mapLayersByName("riv (SWAT)")[0]

    name = "mf_riv2"
    name_ext = "mf_riv2.shp"
    output_dir = QSWATMOD_path_dict['org_shps']

    # output_file = os.path.normpath(os.path.join(output_dir, name))
    # Select features by location
    processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 0)

    # Save just the selected features of the target layer
    riv_swat_shp = os.path.join(output_dir, name_ext)
    QgsVectorFileWriter.writeAsVectorFormat(input1, riv_swat_shp,
        "utf-8", input1.crs(), "ESRI Shapefile", 1)

    # Deselect the features
    processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 2)

    layer = QgsVectorLayer(riv_swat_shp, '{0} ({1})'.format("mf_riv2", "MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    swat_group = root.findGroup("MODFLOW")  
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    swat_group.insertChildNode(0, QgsLayerTreeLayer(layer))
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)

    # ing: Tried to put it in "createMFmodel_dialog" but not working
    self.dlg.radioButton_mf_riv2.setChecked(1)

# def getElevfromDem_riv2(self):
#   from qgis.analysis import QgsZonalStatistics
#   input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]
#   input2 = QgsMapLayerRegistry.instance().mapLayersByName("DEM (SWAT)")[0]
#   provider = input2.dataProvider()
#   rpath = provider.dataSourceUri()
#   zoneStat = QgsZonalStatistics (input1, rpath, 'elev_', 1, QgsZonalStatistics.Mean)
#   zoneStat.calculateStatistics(None)

# Option 3
def mf_riv3(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    layer2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]
    layer1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv1 (MODFLOW)")[0]

    name1 = "mf_riv3_differ"
    name_ext1 = "mf_riv3_differ.shp"
    output_dir1 = QSWATMOD_path_dict['org_shps']

    # output_file = os.path.normpath(os.path.join(output_dir, name))
    # Select features by location
    processing.runalg('qgis:selectbylocation', layer2, layer1, ['equals'], 0, 0)

    layer2.invertSelection()

    # Save just the selected features of the target layer
    mf_riv3_differ = os.path.join(output_dir1, name_ext1)
    QgsVectorFileWriter.writeAsVectorFormat(layer2, mf_riv3_differ,
        "utf-8", layer2.crs(), "ESRI Shapefile", 1)

    layer2.removeSelection()

    name2 = "mf_riv3"
    name_ext2 = "mf_riv3.shp"
    output_dir2 = QSWATMOD_path_dict['org_shps']
    output_file2 = os.path.normpath(output_dir2 + "/" + name2)

    # Input layers for merge need to be in list
    processing.runalg("qgis:mergevectorlayers", [mf_riv3_differ, layer1.source()], output_file2)

    mf_riv3_shapefile = os.path.join(output_dir2, name_ext2)
    layer3 = QgsVectorLayer(mf_riv3_shapefile, '{0} ({1})'.format("mf_riv3","MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    swat_group = root.findGroup("MODFLOW")  
    QgsMapLayerRegistry.instance().addMapLayer(layer3, False)
    swat_group.insertChildNode(0, QgsLayerTreeLayer(layer3))
    layer3 = QgsMapLayerRegistry.instance().addMapLayer(layer3)


def overwriteRivPac(self):
    from PyQt4 import QtCore, QtGui, QtSql
    import csv
    import numpy as np

    QSWATMOD_path_dict = self.dirs_and_paths()
    # try:
    if self.dlg.radioButton_mf_riv2.isChecked():
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]

    elif self.dlg.radioButton_mf_riv3.isChecked():
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv3 (MODFLOW)")[0]

    provider = self.layer.dataProvider()
    
    # Get the index numbers of the fields
    grid_id_idx = provider.fields().fieldNameIndex("grid_id")
    row_idx = provider.fields().fieldNameIndex("row")
    col_idx = provider.fields().fieldNameIndex("col")
    riv_stage_idx = provider.fields().fieldNameIndex("riv_stage")
    riv_cond_idx = provider.fields().fieldNameIndex("riv_cond")
    riv_bot_idx = provider.fields().fieldNameIndex("riv_bot")       

    # transfer the shapefile layer to a python list 
    l = []
    for i in self.layer.getFeatures():
        l.append(i.attributes())

    # then sort by grid_id
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(grid_id_idx))

    # Extract grid_ids and layers as lists
    grid_ids = [g[grid_id_idx] for g in l_sorted]
    rows = [r[row_idx] for r in l_sorted]
    cols = [c[col_idx] for c in l_sorted]
    riv_stages = [rs[riv_stage_idx] for rs in l_sorted]
    riv_conds = [rc[riv_cond_idx] for rc in l_sorted]
    riv_bots = [rb[riv_bot_idx] for rb in l_sorted]

    info_number = len(grid_ids)

    # Combine lists into array
    riv_f = np.c_[rows, cols, riv_stages, riv_conds, riv_bots]

    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
    # Find the name of the previous MODFLOW river package -------------- #
    riv_files = [f for f in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.riv")]
    if len(riv_files) == 1:
        # ------------ Export Data to file -------------- #
        from datetime import datetime
        version = "version 1.3."
        time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')
        with open(riv_files[0], "wb") as f:
            writer = csv.writer(f, delimiter='\t')
            first_row = ["# "+ os.path.basename(riv_files[0]) +" file is overwritten by QSWATMOD plugin " + version + time]
            second_row = [str(info_number), "0                # Number of river cells"]
            writer.writerow(first_row)
            writer.writerow(second_row)
            writer.writerow(second_row)
            for item in riv_f:
                writer.writerow(["1",
                    int(item[0]),
                    int(item[1]),
                    '{:f}'.format(item[2]),
                    '{:f}'.format(item[3]),
                    '{:f}'.format(item[4]),
                    "# Layer, Row, Col, Stage, Cond, Rbot"])

        msgBox.setWindowTitle("Great!")
        msgBox.setText(os.path.basename(riv_files[0]) +" file is overwritten successfully!")
        msgBox.exec_()
    elif len(riv_files) > 1:
        msgBox.setWindowTitle("Oops!")
        msgBox.setText(
                        "You have more than one River Package files!("+str(len(riv_files))+")"+"\n"
                        + str(riv_files)+"\n"
                        + "Solution: Keep only one file!")
        msgBox.exec_()
    else:
        msgBox.setWindowTitle("File Not Found!")
        msgBox.setText("We couldn't find your *.riv file.")
        msgBox.exec_()


# Used in Main ui
def rivInfoTo_mf_riv2(self): 
    from PyQt4 import QtCore, QtGui, QtSql
    import csv
    import pandas as pd
    import numpy as np

    QSWATMOD_path_dict = self.dirs_and_paths()
    # try:
    river_grid = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider1 = river_grid.dataProvider()

    # Get the index numbers of the fields
    grid_id_idx = provider1.fields().fieldNameIndex("grid_id")
    width_idx = provider1.fields().fieldNameIndex("Wid2")
    depth_idx = provider1.fields().fieldNameIndex("Dep2")
    row_idx = provider1.fields().fieldNameIndex("row")
    col_idx = provider1.fields().fieldNameIndex("col")
    elev_idx = provider1.fields().fieldNameIndex("elev_mf")
    length_idx = provider1.fields().fieldNameIndex("rgrid_len")         

    # transfer the shapefile layer to a python list 
    l = []
    for i in river_grid.getFeatures():
        l.append(i.attributes())

    # then sort by grid_id
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(grid_id_idx))

    # Extract grid_ids and layers as lists
    grid_ids = [g[grid_id_idx] for g in l_sorted]
    widths = [w[width_idx] for w in l_sorted]
    depths = [d[depth_idx] for d in l_sorted]
    rows = [r[row_idx] for r in l_sorted]
    cols = [c[col_idx] for c in l_sorted]
    elevs = [e[elev_idx] for e in l_sorted]
    lengths = [leng[length_idx] for leng in l_sorted]

    data = pd.DataFrame(
        {"grid_id": grid_ids,
         "Wid2": widths,
         "Dep2": depths,
         "row": rows,
         "col": cols,
         "elev_mf": elevs,
         "rgrid_len": lengths
         })

    hk = self.dlg.lineEdit_riverbedK.text()
    rivBedthick = self.dlg.lineEdit_riverbedThick.text()


    width_sum = data.groupby(["grid_id"])["Wid2"].sum()
    depth_avg = data.groupby(["grid_id"])["Dep2"].mean()
    row_avg = data.groupby(["grid_id"])["row"].mean().astype(int)
    col_avg = data.groupby(["grid_id"])["col"].mean().astype(int)
    elev_avg = data.groupby(["grid_id"])["elev_mf"].mean()
    length_sum = data.groupby(["grid_id"])["rgrid_len"].sum()

    riv2_cond = float(hk)*length_sum*width_sum / float(rivBedthick)
    riv2_stage = elev_avg + depth_avg + float(rivBedthick)
    riv2_bot = elev_avg + float(rivBedthick)

    # Convert dataframe to lists
    row_avg_lst = row_avg.values.tolist()
    col_avg_lst = col_avg.tolist()
    riv2_cond_lst = riv2_cond.tolist()
    riv2_stage_lst = riv2_stage.tolist()
    riv2_bot_lst = riv2_bot.tolist()

    # Part II ---------------------------------------------------------------
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]
    provider2 = self.layer.dataProvider()

    # from qgis.core import QgsField, QgsExpression, QgsFeature
    if self.layer.dataProvider().fields().indexFromName("riv_stage") == -1:
        field = QgsField("riv_stage", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName("riv_cond" ) == -1:
        field = QgsField("riv_cond", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName("riv_bot" ) == -1:
        field = QgsField("riv_bot", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Get the index numbers of the fields
    riv_stage = provider2.fields().fieldNameIndex("riv_stage")
    riv_cond = provider2.fields().fieldNameIndex("riv_cond")
    riv_bot = provider2.fields().fieldNameIndex("riv_bot")  

    #
    feats = self.layer.getFeatures()
    self.layer.startEditing()

    # add riv_info based on row and column numbers
    for f in feats:
        rowNo = f.attribute("row")
        colNo = f.attribute("col")
        for ii in range(len(riv2_cond_lst)):
            if ((rowNo == (row_avg_lst[ii])) and (colNo == (col_avg_lst[ii]))):
                self.layer.changeAttributeValue(f.id(), riv_stage, float(riv2_stage_lst[ii])) # why without float is not working?
                self.layer.changeAttributeValue(f.id(), riv_cond, float(riv2_cond_lst[ii]))             
                self.layer.changeAttributeValue(f.id(), riv_bot, float(riv2_bot_lst[ii]))
    self.layer.commitChanges()


def rivInfoTo_mf_riv2_ii(self):
    from PyQt4 import QtCore, QtGui, QtSql
    import csv
    import pandas as pd
    import numpy as np

    QSWATMOD_path_dict = self.dirs_and_paths()
    # try:
    river_grid = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider1 = river_grid.dataProvider()

    # Get the index numbers of the fields
    grid_id_idx = provider1.fields().fieldNameIndex("grid_id")
    width_idx = provider1.fields().fieldNameIndex("Wid2")
    depth_idx = provider1.fields().fieldNameIndex("Dep2")
    row_idx = provider1.fields().fieldNameIndex("row")
    col_idx = provider1.fields().fieldNameIndex("col")
    elev_idx = provider1.fields().fieldNameIndex("elev_mf")
    length_idx = provider1.fields().fieldNameIndex("rgrid_len")         

    # transfer the shapefile layer to a python list 
    l = []
    for i in river_grid.getFeatures():
        l.append(i.attributes())

    # then sort by grid_id
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(grid_id_idx))

    # Extract grid_ids and layers as lists
    grid_ids = [g[grid_id_idx] for g in l_sorted]
    widths = [w[width_idx] for w in l_sorted]
    depths = [d[depth_idx] for d in l_sorted]
    rows = [r[row_idx] for r in l_sorted]
    cols = [c[col_idx] for c in l_sorted]
    elevs = [e[elev_idx] for e in l_sorted]
    lengths = [leng[length_idx] for leng in l_sorted]

    data = pd.DataFrame({
        "grid_id" : grid_ids,
        "Wid2" : widths,
        "Dep2" : depths,
        "row" : rows,
        "col" : cols,
        "elev_mf" : elevs,
        "rgrid_len" : lengths
        })
    hk = self.lineEdit_riverbedK2.text()
    rivBedthick = self.lineEdit_riverbedThick2.text()
    width_sum = data.groupby(["grid_id"])["Wid2"].sum()
    depth_avg = data.groupby(["grid_id"])["Dep2"].mean()
    row_avg = data.groupby(["grid_id"])["row"].mean().astype(int)   
    col_avg = data.groupby(["grid_id"])["col"].mean().astype(int)   
    elev_avg = data.groupby(["grid_id"])["elev_mf"].mean()
    length_sum = data.groupby(["grid_id"])["rgrid_len"].sum()

    riv2_cond = float(hk)*length_sum*width_sum / float(rivBedthick)
    riv2_stage = elev_avg + depth_avg + float(rivBedthick)
    riv2_bot = elev_avg + float(rivBedthick)

    # Convert dataframe to lists
    row_avg_lst = row_avg.values.tolist()
    col_avg_lst = col_avg.tolist()
    riv2_cond_lst = riv2_cond.tolist()
    riv2_stage_lst = riv2_stage.tolist()
    riv2_bot_lst = riv2_bot.tolist()

    # Part II ---------------------------------------------------------------
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]
    provider2 = self.layer.dataProvider()

    # from qgis.core import QgsField, QgsExpression, QgsFeature
    if self.layer.dataProvider().fields().indexFromName("riv_stage") == -1:
        field = QgsField("riv_stage", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName( "riv_cond" ) == -1:
        field = QgsField("riv_cond", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Obtain col number
    if self.layer.dataProvider().fields().indexFromName( "riv_bot" ) == -1:
        field = QgsField("riv_bot", QVariant.Double, 'double', 20, 5)
        provider2.addAttributes([field])
        self.layer.updateFields()

    # Get the index numbers of the fields
    riv_stage = provider2.fields().fieldNameIndex("riv_stage")
    riv_cond = provider2.fields().fieldNameIndex("riv_cond")
    riv_bot = provider2.fields().fieldNameIndex("riv_bot")  

    #
    feats = self.layer.getFeatures()
    self.layer.startEditing()

    # add riv_info based on row and column numbers
    for f in feats:
        rowNo = f.attribute("row")
        colNo = f.attribute("col")
        for ii in range(len(riv2_cond_lst)):
            if ((rowNo == (row_avg_lst[ii])) and (colNo == (col_avg_lst[ii]))):
                self.layer.changeAttributeValue(f.id(), riv_stage, float(riv2_stage_lst[ii])) # why without float is not working?
                self.layer.changeAttributeValue(f.id(), riv_cond, float(riv2_cond_lst[ii]))             
                self.layer.changeAttributeValue(f.id(), riv_bot, float(riv2_bot_lst[ii]))
    self.layer.commitChanges()

def riv_cond_delete_NULL(self):
    from qgis.core import QgsFeatureRequest
    if self.dlg.radioButton_mf_riv2.isChecked():
        layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]

    provider = layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression("riv_cond IS NULL" )
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)

    layer.startEditing()
    for f in layer.getFeatures(request):
        layer.deleteFeature(f.id())
    layer.commitChanges()


def defaultExtent(self):
    from PyQt4 import QtCore, QtGui, QtSql
    try:
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("sub (SWAT)")[0]
        provider = self.layer.dataProvider()
        if self.dlg.checkBox_default_extent.isChecked():
            extent = self.layer.extent()
            x_origin = extent.xMinimum()
            y_origin = extent.yMaximum()
            self.dlg.lineEdit_x_coordinate.setText(str(x_origin))
            self.dlg.lineEdit_y_coordinate.setText(str(y_origin))

    except:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        msgBox.setWindowTitle("?")
        msgBox.setText("There is no 'sub' shapefile!")
        msgBox.exec_()
        self.dlg.checkBox_default_extent.setChecked(0)


# Use observed well point shapefile
def use_obs_points(self):
    QSWATMOD_path_dict = self.dirs_and_paths()

    settings = QSettings()
    if settings.contains('/QSWATMOD/LastInputPath'):
        path = unicode(settings.value('/QSWATMOD/LastInputPath'))
    else:
        path = ''
    title = "Choose MODFLOW observation point shapefile"
    inFileName = QFileDialog.getOpenFileName(None, title, path, "Shapefiles (*.shp);; All files (*.*)")

    if inFileName:
        settings.setValue('/QSWATMOD/LastInputPath', os.path.dirname(unicode(inFileName)))
        Out_folder = QSWATMOD_path_dict['org_shps']
        inInfo = QFileInfo(inFileName)
        inFile = inInfo.fileName()
        pattern = os.path.splitext(inFileName)[0] + '.*'
        
        # inName = os.path.splitext(inFile)[0]
        inName = 'mf_obs_points'
        for f in glob.iglob(pattern):
            suffix = os.path.splitext(f)[1]
            if os.name == 'nt':
                outfile = ntpath.join(Out_folder, inName + suffix)
            else:
                outfile = posixpath.join(Out_folder, inName + suffix)
            shutil.copy(f, outfile) 
        if os.name == 'nt':
            mf_obs_points = ntpath.join(Out_folder, inName + ".shp")
        else:
            mf_obs_points = posixpath.join(Out_folder, inName + ".shp")
        
        layer = QgsVectorLayer(mf_obs_points, '{0} ({1})'.format("mf_obs_points","MODFLOW"), 'ogr')

        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        mf_group = root.findGroup("MODFLOW")    
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        mf_group.insertChildNode(0, QgsLayerTreeLayer(layer))
        self.dlg.lineEdit_mf_obs_points.setText(mf_obs_points)  


# select
def select_obs_grids(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    from PyQt4 import QtCore, QtGui, QtSql

    input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_obs_points (MODFLOW)")[0]

    name = "mf_obs_grid"
    name_ext = "mf_obs_grid.shp"
    output_dir = QSWATMOD_path_dict['SMshps']

    # output_file = os.path.normpath(os.path.join(output_dir, name))
    # Select features by location
    processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 0)

    # Save just the selected features of the target layer
    mf_obs_shapefile = os.path.join(output_dir, name_ext)
    QgsVectorFileWriter.writeAsVectorFormat(input1, mf_obs_shapefile,
        "utf-8", input1.crs(), "ESRI Shapefile", 1)

    # Deselect the features
    processing.runalg('qgis:selectbylocation', input1, input2, ['intersects'], 0, 2)

    layer = QgsVectorLayer(mf_obs_shapefile, '{0} ({1})'.format("mf_obs","SWAT-MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    swat_group = root.findGroup("SWAT-MODFLOW") 
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    swat_group.insertChildNode(0, QgsLayerTreeLayer(layer))
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)
    self.dlg.lineEdit_mf_obs_shapefile.setText(mf_obs_shapefile)  


# navigate to the shapefile of the point observation shapefile
def mf_obs_shapefile(self):
    QSWATMOD_path_dict = self.dirs_and_paths()        
    settings = QSettings()
    if settings.contains('/QSWATMOD/LastInputPath'):
        path = unicode(settings.value('/QSWATMOD/LastInputPath'))
    else:
        path = ''
    title = "choose MODFLOW observation shapefile"
    inFileName = QFileDialog.getOpenFileName(None, title, path, "Shapefiles (*.shp);; All files (*.*)")

    if inFileName:
        settings.setValue('/QSWATMOD/LastInputPath', os.path.dirname(unicode(inFileName)))
        Out_folder = QSWATMOD_path_dict['SMshps']
        inInfo = QFileInfo(inFileName)
        inFile = inInfo.fileName()
        pattern = os.path.splitext(inFileName)[0] + '.*'
        
        # inName = os.path.splitext(inFile)[0]
        inName = 'mf_obs_SM'
        for f in glob.iglob(pattern):
            suffix = os.path.splitext(f)[1]
            if os.name == 'nt':
                outfile = ntpath.join(Out_folder, inName + suffix)
            else:
                outfile = posixpath.join(Out_folder, inName + suffix)                    
            shutil.copy(f, outfile) 
        if os.name == 'nt':
            mf_obs_shp = ntpath.join(Out_folder, inName + ".shp")
        else:
            mf_obs_shp = posixpath.join(Out_folder, inName + ".shp")
        
        layer = QgsVectorLayer(mf_obs_shp, '{0} ({1})'.format("mf_obs","SWAT-MODFLOW"), 'ogr')

        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        sm_group = root.findGroup("SWAT-MODFLOW")   
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        sm_group.insertChildNode(0, QgsLayerTreeLayer(layer))
        self.dlg.lineEdit_mf_obs_shapefile.setText(mf_obs_shp)     


def create_modflow_obs(self):
    from PyQt4 import QtCore, QtGui, QtSql
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_obs (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()

    if self.layer.dataProvider().fields().indexFromName("layer") == -1:
        field = QgsField("layer", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()
    feats = self.layer.getFeatures()
    self.layer.startEditing()
    for feat in feats:
        layer = 1
        feat['layer'] = layer
        self.layer.updateFeature(feat)
    self.layer.commitChanges()


def export_modflow_obs(self):
    from PyQt4 import QtCore, QtGui, QtSql
    import csv
    QSWATMOD_path_dict = self.dirs_and_paths()
    try:
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_obs (SWAT-MODFLOW)")[0]
        provider = self.layer.dataProvider()

        # Get the index numbers of the fields
        grid_id_index = provider.fields().fieldNameIndex("grid_id")
        layer_index = provider.fields().fieldNameIndex("layer")
        elev_mf_idx = provider.fields().fieldNameIndex("elev_mf")

        # transfer the shapefile layer to a python list 
        l = []
        for i in self.layer.getFeatures():
            l.append(i.attributes())

        # then sort by grid_id
        import operator
        l_sorted = sorted(l, key=operator.itemgetter(grid_id_index))

        # Extract grid_ids and layers as lists
        grid_ids = [g[grid_id_index] for g in l_sorted]
        layers = [l[layer_index] for l in l_sorted]
        elevs_mf = ['{:.2f}'.format(l[elev_mf_idx]) for l in l_sorted]

        info_number = len(grid_ids)
        # Find .dis file and read number of rows, cols, x spacing, and y spacing (not allowed to change)
        for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
            with open(filename, "r") as f:
                data = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        data.append(line.replace('\n', '').split())
            nrows = int(data[0][1])
            ncols = int(data[0][2])

        # Generate row and col number for whole modflow grid
        iy = []
        ix = []
        for i in range(1, nrows + 1):
            for j in range(1, ncols + 1):
                ix.append(j)
                iy.append(i)

        # Select row and columns only chosen using grid_id
        nrow = []
        ncol = []
        for grid_id in grid_ids:
            nrow.append(iy[grid_id-1])
            ncol.append(ix[grid_id-1])
        data = zip(nrow, ncol, layers, grid_ids, elevs_mf)

        # ------------ Export Data to file -------------- #
        from datetime import datetime
        version = "version 1.3."
        time = datetime.now().strftime('- %m/%d/%y %H:%M:%S -')

        name = "modflow.obs"
        output_dir = QSWATMOD_path_dict['SMfolder']
        output_file = os.path.normpath(output_dir + "/" + name)
        with open(output_file, "wb") as f:
            writer = csv.writer(f, delimiter = '\t')
            first_row = ["# modflow.obs file is created by QSWATMOD plugin " + version + time]
            second_row = [str(info_number), "                # Number of observation cells"]
            writer.writerow(first_row)
            writer.writerow(second_row)
            for item in data:
                writer.writerow([item[0], item[1], item[2], item[3], item[4],
                                "# Row, Col, Layer, grid_id, elevation "])

    except:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        msgBox.setIconPixmap(QtGui.QPixmap(':/newPrefix/pics/modflow_obs.png'))
        msgBox.setWindowTitle("Oops!")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.exec_()


def import_mf_grid(self):
    # Initiate function
    QSWATMOD_path_dict = self.dirs_and_paths()
    settings = QSettings()
    if settings.contains('/QSWATMOD/LastInputPath'):
        path = unicode(settings.value('/QSWATMOD/LastInputPath'))
    else:
        path = ''
    title = "choose mf grid shapfile"
    inFileName = QFileDialog.getOpenFileName(None, title, path, "Shapefiles (*.shp);; All files (*.*)")

    if inFileName:
        settings.setValue('/QSWATMOD/LastInputPath', os.path.dirname(unicode(inFileName)))
        Out_folder = QSWATMOD_path_dict['org_shps']
        inInfo = QFileInfo(inFileName)
        inFile = inInfo.fileName()
        pattern = os.path.splitext(inFileName)[0] + '.*'
        
        # inName = os.path.splitext(inFile)[0]
        inName = 'mf_grid'
        for f in glob.iglob(pattern):
            suffix = os.path.splitext(f)[1]
            if os.name == 'nt':
                outfile = ntpath.join(Out_folder, inName + suffix)
            else:
                outfile = posixpath.join(Out_folder, inName + suffix)
            shutil.copy(f, outfile)
        if os.name == 'nt':
            mf_grid_shp = ntpath.join(Out_folder, inName + ".shp")
        else:
            mf_grid_shp = posixpath.join(Out_folder, inName + ".shp")
        
        layer = QgsVectorLayer(mf_grid_shp, '{0} ({1})'.format("mf_grid","MODFLOW"), 'ogr')

        # if there is an existing mf_grid shapefile, it will be removed
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == ("mf_grid (MODFLOW)"):
                QgsMapLayerRegistry.instance().removeMapLayers([lyr.id()])

        # Put in the group
        root = QgsProject.instance().layerTreeRoot()
        swat_group = root.findGroup("MODFLOW")  
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        swat_group.insertChildNode(0, QgsLayerTreeLayer(layer))

        self.dlg.lineEdit_MODFLOW_grid_shapefile.setText(mf_grid_shp)     


# Create "modflow.mfn" file
def create_modflow_mfn(self):
    import datetime
    QSWATMOD_path_dict = self.dirs_and_paths()
    wd = QSWATMOD_path_dict['SMfolder']
    for filename in glob.glob(wd + "/*.nam"):
        version = "version 1.3."
        time = datetime.datetime.now().strftime(' - %m/%d/%y %H:%M:%S -')
        info = "# modflow.mfn file, generated by QSWATMOD plugin "+version+ time +'\n'
        lines = []
        lines.append(info)

        with open(filename) as infile:
            data = [x.strip() for x in infile if x.strip()]
        for line in data:
            if line.startswith("#"):
                lines.append(line + '\n')
            elif len(line.split()[1]) < 4:
                a = line.split()[1]
                b = int(line.split()[1]) + 5000
                line = line.split()[0] + "\t" + str(b) + "\t" + line.split()[2]
                lines.append(line + '\n')
                file = "modflow_EditLog.txt"
                time = datetime.datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
                with open(os.path.join(wd, file), 'a') as outfile:
                    outfile.write(str(time +' -> modflow.mfn: Unit number '+a+' -> '+str(b)+'\n'))
            else:
                lines.append(line + '\n')

        ''' It causes error with blank lines and ignore comment lines.
        # with open(filename) as infile:
        #     for line in infile:
        #         data = line.strip().split()
        #         if not line.startswith("#") and len(data[1]) != 4:  # filter unnecessary lines
        #             a = data[1] # read previous unit numbers
        #             b = int(data[1])+5000 # add 5000 to previous number
        #             data[1] = str(b)  # modify unit number
        #             data1 = "\t".join(data) + "\n" # change list to line
        #             lines.append(data1)
        #             file = "modflow_EditLog.txt"
        #             time = datetime.datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
        #             with open(os.path.join(wd, file), 'a') as outfile:
        #                 outfile.write(str(time +' -> modflow.mfn: Unit number '+a+' -> '+str(b)+'\n')) 
        #         else:
        #             lines.append(line)
        '''

        with open(os.path.join(wd, 'modflow.mfn'), 'w') as outfile:
            for line in lines:
                outfile.write(line)


# Modify *.oc file
def modify_modflow_oc(self):
    import datetime
    QSWATMOD_path_dict = self.dirs_and_paths()
    wd = QSWATMOD_path_dict['SMfolder']
    for filename in glob.glob(wd + "/*.oc"):
        version = "version 1.3."
        time = datetime.datetime.now().strftime(' - %m/%d/%y %H:%M:%S -')
        info = "# Output Control file, modified by QSWATMOD plugin "+version+ time +'\n'

        lines = []
        lines.append(info)
        with open(filename) as infile:
            for line in infile:
                data = line.strip().split()
                if line.startswith("HEAD SAVE UNIT") and len(data[3]) != 4: # filter unnecessary lines
                    a = data[3]  # read previous unit numbers
                    b = int(data[3])+5000  # add 5000 to previous number
                    data[3] = str(b)  # modify unit number
                    data1 = "\t".join(data) + "\n" # change list to line
                    lines.append(data1)
                    file = "modflow_EditLog.txt"
                    time = datetime.datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
                    with open(os.path.join(wd, file), 'a') as outfile:
                        outfile.write(str(time+' -> '+os.path.basename(filename)+': Unit number '+a+' -> '+str(b)+'\n')) 
                else:
                    lines.append(line)
        with open(os.path.join(wd, os.path.basename(filename)), 'w') as outfile:
            for line in lines:
                outfile.write(line)


def modflow_ss_to_tr(self):
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        # check whether it works
        # os.startfile(filename)
        lines = []
        with open(filename) as infile:
            for line in infile:
                data = line.strip().split()
                try:
                    a = data[3]
                    if a == 'ss' or a == 'SS':
                        line = line.replace(a, 'TR')
                        msgBox = QMessageBox()
                        msgBox.setText("Oops!!!" + str(a))
                        msgBox.exec_()
                        file = "editLog.txt"
                        with open(os.path.join(QSWATMOD_path_dict['SMfolder'], file), 'a') as outfile:
                            outfile.write(str("the .dis file was changed from "+ a+" to TR")) 
                    elif a == 'TR':
                        msgBox = QMessageBox()
                        msgBox.setText("Good job!")
                        msgBox.exec_()

                except IndexError:
                    a = 'null'
                lines.append(line)

        with open(filename, 'w') as outfile:
            for line in lines:
                outfile.write(line)

    self.dlg.pushButton_execute_linking.setEnabled(True)

###### this might be an option for MODFLOW-USG, but for now not used for efficiency
# def calculate_grid_area(self):
#   #layer = qgis.utils.iiface.activeLayer()
#   self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
#   provider = self.layer.dataProvider()
#   from PyQt4.QtCore import QVariant
#   from qgis.core import QgsField, QgsExpression, QgsFeature

#   if self.layer.dataProvider().fields().indexFromName( "grid_area" ) == -1:
            
#       # field = QgsField("grid_area", QVariant.Double,'double', 20, 5)
#       field = QgsField("grid_area", QVariant.Int)        
#       provider.addAttributes([field])
#       self.layer.updateFields()
    
#   feats = self.layer.getFeatures()
#   self.layer.startEditing()

#   for feat in feats:
#      area = feat.geometry().area()
#      #score = scores[i]
#      feat['grid_area'] = area
#      self.layer.updateFeature(feat)
#   self.layer.commitChanges()
######


