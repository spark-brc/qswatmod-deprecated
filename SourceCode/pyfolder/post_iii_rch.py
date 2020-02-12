# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import * # @UnusedWildImport

from qgis.core import (
                        QgsMapLayerRegistry, QgsProject, QgsLayerTreeLayer, QgsVectorFileWriter, QgsVectorLayer,
                        QgsField)
from PyQt4 import QtCore, QtGui, QtSql
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
# import numpy as np
import pandas as pd
import os

# try:
#     import deps.pandas as pd
# except AttributeError:
#     msgBox = QMessageBox()
#     msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
#     msgBox.setWindowTitle("QSWATMOD")
#     msgBox.setText("Please, restart QGIS to initialize QSWATMOD properly.")
#     msgBox.exec_()


def read_mf_recharge_dates(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period()
    wd = QSWATMOD_path_dict['SMfolder']
    startDate = stdate.strftime("%m-%d-%Y")
    
    # Create swatmf_results tree inside 
    root = QgsProject.instance().layerTreeRoot()
    if root.findGroup("swatmf_results"):
        swatmf_results = root.findGroup("swatmf_results")
    else:
        swatmf_results = root.insertGroup(0, "swatmf_results")

    input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]
    provider = input1.dataProvider()

    if self.dlg.checkBox_recharge.isChecked() and self.dlg.radioButton_mf_results_d.isChecked():
        filename = "swatmf_out_MF_recharge"

        # Open "swatmf_out_MF_recharge" file
        y = ("MODFLOW", "--Calculated", "daily") # Remove unnecssary lines
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)]  # Remove blank lines
        date = [x.strip().split() for x in data if x.strip().startswith("Day:")] # Collect only lines with dates
        onlyDate = [x[1] for x in date] # Only date
        # data1 = [x.split() for x in data] # make each line a list
        sdate = datetime.datetime.strptime(startDate, "%m-%d-%Y")  # Change startDate format
        dateList = [(sdate + datetime.timedelta(days = int(i)-1)).strftime("%m-%d-%Y") for i in onlyDate]
        self.dlg.comboBox_mf_results_sdate.clear()
        self.dlg.comboBox_mf_results_sdate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.clear()
        self.dlg.comboBox_mf_results_edate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.setCurrentIndex(len(dateList)-1)

        # Copy mf_grid shapefile to swatmf_results tree
        name = "mf_rch_daily"
        name_ext = "mf_rch_daily.shp"
        output_dir = QSWATMOD_path_dict['SMshps']

        # Check if there is an exsting mf_recharge shapefile
        if not any(lyr.name() == ("mf_rch_daily") for lyr in QgsMapLayerRegistry.instance().mapLayers().values()):
            mf_rch_shapfile = os.path.join(output_dir, name_ext)
            QgsVectorFileWriter.writeAsVectorFormat(input1, mf_rch_shapfile,
                "utf-8", input1.crs(), "ESRI Shapefile")
            layer = QgsVectorLayer(mf_rch_shapfile, '{0}'.format("mf_rch_daily"), 'ogr')

            # Put in the group
            root = QgsProject.instance().layerTreeRoot()
            swatmf_results = root.findGroup("swatmf_results")   
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            swatmf_results.insertChildNode(0, QgsLayerTreeLayer(layer))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
            msgBox.setWindowTitle("Created!")
            msgBox.setText("'mf_rch_daily.shp' file is created in 'swatmf_results' group!")
            msgBox.exec_()

    elif self.dlg.checkBox_recharge.isChecked() and self.dlg.radioButton_mf_results_m.isChecked():
        filename = "swatmf_out_MF_recharge_monthly"

        # Open "swatmf_out_MF_recharge" file
        y = ("Monthly") # Remove unnecssary lines
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines
        date = [x.strip().split() for x in data if x.strip().startswith("month:")] # Collect only lines with dates
        onlyDate = [x[1] for x in date] # Only date
        # data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(startDate, periods=len(onlyDate), freq='M').strftime("%b-%Y").tolist()
        self.dlg.comboBox_mf_results_sdate.clear()
        self.dlg.comboBox_mf_results_sdate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.clear()
        self.dlg.comboBox_mf_results_edate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.setCurrentIndex(len(dateList)-1)

        # Copy mf_grid shapefile to swatmf_results tree
        name = "mf_rch_monthly"
        name_ext = "mf_rch_monthly.shp"
        output_dir = QSWATMOD_path_dict['SMshps']

        # Check if there is an exsting mf_recharge shapefile
        if not any(lyr.name() == ("mf_rch_monthly") for lyr in QgsMapLayerRegistry.instance().mapLayers().values()):
            mf_rch_shapfile = os.path.join(output_dir, name_ext)
            QgsVectorFileWriter.writeAsVectorFormat(input1, mf_rch_shapfile,
                "utf-8", input1.crs(), "ESRI Shapefile")
            layer = QgsVectorLayer(mf_rch_shapfile, '{0}'.format("mf_rch_monthly"), 'ogr')

            # Put in the group
            root = QgsProject.instance().layerTreeRoot()
            swatmf_results = root.findGroup("swatmf_results")   
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            swatmf_results.insertChildNode(0, QgsLayerTreeLayer(layer))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
            msgBox.setWindowTitle("Created!")
            msgBox.setText("'mf_rch_monthly.shp' file is created in 'swatmf_results' group!")
            msgBox.exec_()      

    elif self.dlg.checkBox_recharge.isChecked() and self.dlg.radioButton_mf_results_y.isChecked():
        filename = "swatmf_out_MF_recharge_yearly"

        # Open "swatmf_out_MF_recharge" file
        y = ("Yearly") # Remove unnecssary lines
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines
        date = [x.strip().split() for x in data if x.strip().startswith("year:")] # Collect only lines with dates
        onlyDate = [x[1] for x in date] # Only date
        # data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(startDate, periods = len(onlyDate), freq = 'A').strftime("%Y").tolist()
        self.dlg.comboBox_mf_results_sdate.clear()
        self.dlg.comboBox_mf_results_sdate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.clear()
        self.dlg.comboBox_mf_results_edate.addItems(dateList)
        self.dlg.comboBox_mf_results_edate.setCurrentIndex(len(dateList)-1)

        # Copy mf_grid shapefile to swatmf_results tree
        name = "mf_rch_yearly"
        name_ext = "mf_rch_yearly.shp"
        output_dir = QSWATMOD_path_dict['SMshps']

        # Check if there is an exsting mf_recharge shapefile
        if not any(lyr.name() == ("mf_rch_yearly") for lyr in QgsMapLayerRegistry.instance().mapLayers().values()):
            mf_rch_shapfile = os.path.join(output_dir, name_ext)
            QgsVectorFileWriter.writeAsVectorFormat(input1, mf_rch_shapfile,
                "utf-8", input1.crs(), "ESRI Shapefile")
            layer = QgsVectorLayer(mf_rch_shapfile, '{0}'.format("mf_rch_yearly"), 'ogr')

            # Put in the group
            root = QgsProject.instance().layerTreeRoot()
            swatmf_results = root.findGroup("swatmf_results")   
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            swatmf_results.insertChildNode(0, QgsLayerTreeLayer(layer))

            msgBox = QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
            msgBox.setWindowTitle("Created!")
            msgBox.setText("'mf_rch_yearly.shp' file is created in 'swatmf_results' group!")
            msgBox.exec_()      

    else:
        self.dlg.comboBox_mf_results_sdate.clear()


def export_mf_recharge (self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    stdate, eddate, stdate_warmup, eddate_warmup = self.define_sim_period()
    wd = QSWATMOD_path_dict['SMfolder']
    startDate = stdate.strftime("%m-%d-%Y")

    # Open "swatmf_out_MF_recharge" file
    y = ("MODFLOW", "--Calculated", "daily", "Monthly", "Yearly") # Remove unnecssary lines

    if self.dlg.radioButton_mf_results_d.isChecked():
        filename = "swatmf_out_MF_recharge"
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_rch_daily")[0]
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines
        date = [x.strip().split() for x in data if x.strip().startswith("Day:")] # Collect only lines with dates
        onlyDate = [x[1] for x in date] # Only date
        data1 = [x.split() for x in data] # make each line a list
        sdate = datetime.datetime.strptime(startDate, "%m-%d-%Y") # Change startDate format
        dateList = [(sdate + datetime.timedelta(days = int(i)-1)).strftime("%m-%d-%Y") for i in onlyDate]
    elif self.dlg.radioButton_mf_results_m.isChecked():
        filename = "swatmf_out_MF_recharge_monthly"
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_rch_monthly")[0]
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines     
        date = [x.strip().split() for x in data if x.strip().startswith("month:")] # Collect only lines with dates  
        onlyDate = [x[1] for x in date] # Only date
        data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(startDate, periods = len(onlyDate), freq = 'M').strftime("%b-%Y").tolist()
    elif self.dlg.radioButton_mf_results_y.isChecked():
        filename = "swatmf_out_MF_recharge_yearly"
        self.layer = QgsMapLayerRegistry.instance().mapLayersByName("mf_rch_yearly")[0]
        with open(os.path.join(wd, filename), "r") as f:
            data = [x.strip() for x in f if x.strip() and not x.strip().startswith(y)] # Remove blank lines
        date = [x.strip().split() for x in data if x.strip().startswith("year:")] # Collect only lines with dates
        onlyDate = [x[1] for x in date] # Only date
        data1 = [x.split() for x in data] # make each line a list
        dateList = pd.date_range(startDate, periods = len(onlyDate), freq = 'A').strftime("%Y").tolist()
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        msgBox.setWindowTitle("Oops!")
        msgBox.setText("Please, select one of the time options!")
        msgBox.exec_()  

    selectedSdate = self.dlg.comboBox_mf_results_sdate.currentText()
    selectedEdate = self.dlg.comboBox_mf_results_edate.currentText()

    # Reverse step
    dateSidx = dateList.index(selectedSdate)
    dateEidx = dateList.index(selectedEdate)
    dateList_f = dateList[dateSidx:dateEidx+1]

    input1 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0] # Put this here to know number of features

    per = 0
    self.dlg.progressBar_mf_results.setValue(0)    
    for selectedDate in dateList_f:

        # Reverse step
        dateIdx = dateList.index(selectedDate)

        #only
        onlyDate_lookup = onlyDate[dateIdx]
        if self.dlg.radioButton_mf_results_d.isChecked():       
            for num, line in enumerate(data1, 1):
                if line[0] == "Day:" in line and line[1] == onlyDate_lookup in line:
                    ii = num # Starting line
        elif self.dlg.radioButton_mf_results_m.isChecked():
            # Find year 
            dt = datetime.datetime.strptime(selectedDate, "%b-%Y")
            year = dt.year
            for num, line in enumerate(data1, 1):
                if ((line[0] == "month:" in line) and (line[1] == onlyDate_lookup in line) and (line[3] == str(year) in line)):
                    ii = num # Starting line
        elif self.dlg.radioButton_mf_results_y.isChecked():     
            for num, line in enumerate(data1, 1):
                if line[0] == "year:" in line and line[1] == onlyDate_lookup in line:
                    ii = num # Starting line

        mf_rchs = []
        count = 0
        while count < input1.featureCount():
            for jj in range(len(data1[ii])):
                mf_rchs.append(float(data1[ii][jj]))
                count += 1
            ii += 1

        provider = self.layer.dataProvider()
        if self.layer.dataProvider().fields().indexFromName(selectedDate) == -1:
            field = QgsField(selectedDate, QVariant.Double, 'double', 20, 5)
            provider.addAttributes([field])
            self.layer.updateFields()

        mf_rchs_idx = provider.fields().fieldNameIndex(selectedDate)

        # Get features (Find out a way to change attribute values using another field)
        feats = self.layer.getFeatures()
        self.layer.startEditing()

        # add row number
        for f, mf_rch in zip(feats, mf_rchs):
            self.layer.changeAttributeValue(f.id(), mf_rchs_idx, mf_rch)
            # self.layer.changeAttributeValue(f[grid_id] - 1, row, r)
            # self.layer.changeAttributeValue(f[grid_id] - 1, col, c)
        self.layer.commitChanges()

        # Update progress bar         
        per += 1
        progress = (100*per) / len(dateList_f)
        self.dlg.progressBar_mf_results.setValue(progress)
        QCoreApplication.processEvents()
        self.dlg.raise_()

    msgBox = QMessageBox()
    msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
    msgBox.setWindowTitle("Exported!")
    msgBox.setText("mf_recharge results were exported successfully!")
    msgBox.exec_()
