import os
import os.path
from PyQt4.QtCore import *
from PyQt4.QtGui import * # @UnusedWildImport
from PyQt4 import QtCore, QtGui, QtSql
import processing
from qgis.core import (QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeatureIterator,
                        QgsFeatureRequest, QgsProject, QgsLayerTreeLayer)
import glob
import subprocess
import shutil
import csv

def calculate_hru_area(self): 
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("hru (SWAT)")[0]
    provider = self.layer.dataProvider()
    from PyQt4.QtCore import QVariant
    from qgis.core import QgsField, QgsExpression, QgsFeature

    if self.layer.dataProvider().fields().indexFromName( "hru_area" ) == -1:
        # field = QgsField("hru_area", QVariant.Double)
        field = QgsField("hru_area", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()

    feats = self.layer.getFeatures()
    self.layer.startEditing()

    #feats_count = len(list(self.layer.getFeatures()))
    #self.dlg.progressBar_calculate_hru_area.setMaximum(feats_count)
    # count = 0
    for feat in feats:            
       area = feat.geometry().area()
       #score = scores[i]
       feat['hru_area'] = area
       self.layer.updateFeature(feat)
       # count += 1
       # perc = (count / feats_count )*100

    self.layer.commitChanges()
    # put ok! to DB


def multipart_to_singlepart(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    #http://gis.stackexchange.com/questions/174429/converting-selected-multipart-features-to-single-parts-in-qgis
    layer = QgsMapLayerRegistry.instance().mapLayersByName("hru (SWAT)")[0]
    name = "dhru"
    name_ext = "dhru.shp"
    output_dir = QSWATMOD_path_dict['SMshps']    
    # output_dir_1 = os.path.normpath(output_dir + "/" + "shapefiles_out")
    output_file = os.path.normpath(output_dir + "/" + name )
    # runinng the actual routine:        
    processing.runalg("qgis:multiparttosingleparts", layer, output_file)
    # defining the outputfile to be loaded into the canvas        
    dhru_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(dhru_shapefile, '{0} ({1})'.format("dhru","SWAT-MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    sm_group = root.findGroup("SWAT-MODFLOW")   
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    sm_group.insertChildNode(1, QgsLayerTreeLayer(layer))
    # layer.commitChanges()
    # self.add_dhru_id_to_shp()

       
def create_dhru_id(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]  # get active layer
    # create list of tupels of area and feature-id
    provider = self.layer.dataProvider()
    if self.layer.dataProvider().fields().indexFromName( "dhru_id" ) == -1:
        field = QgsField("dhru_id", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()

    #field1Id = self.layer.dataProvider().fields().indexFromName( "hru_id" ) # for SWAT+
    field1Id = self.layer.dataProvider().fields().indexFromName( "HRU_ID" ) # for origin SWAT
    attrIdx = self.layer.dataProvider().fields().indexFromName( "dhru_id" )
    
    # aList = list( aLayer.getFeatures() )
    aList = self.layer.getFeatures()     

    #aList= [(feat.geometry().area(), feat.id()) for feat in aLayer.getFeatures()]
    #aList= [(feat.geometry().area(), feat.feature['HRU_ID']) for feat in aLayer.getFeatures()]
    #aList.sort()  # sort list of tupels

    featureList = sorted(aList, key=lambda f: f[field1Id])
    self.layer.startEditing()
    for i, f in enumerate(featureList):
        #print f.id()
        self.layer.changeAttributeValue(f.id(), attrIdx, i+1)
    self.layer.commitChanges()


# calculate the dhru area    
def calculate_dhru_area(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    from PyQt4.QtCore import QVariant
    from qgis.core import QgsField, QgsExpression, QgsFeature
    

    if self.layer.dataProvider().fields().indexFromName( "dhru_area" ) == -1:
    
        # field = QgsField("dhru_area", QVariant.Double)
        field = QgsField("dhru_area", QVariant.Int)
        provider.addAttributes([field])
        self.layer.updateFields()
    
    feats = self.layer.getFeatures()
    self.layer.startEditing()
    for feat in feats:
       area = feat.geometry().area()
       #score = scores[i]
       feat['dhru_area'] = abs(area)
       self.layer.updateFeature(feat)
    self.layer.commitChanges()

# def calculate_dhru_area(self):
#   # self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]
#   # provider = self.layer.dataProvider()
#   from PyQt4.QtCore import QVariant
#   from qgis.core import QgsField, QgsExpression, QgsFeature


#   # if self.layer.dataProvider().fields().indexFromName( "dhru_area" ) == -1:
    
#   #   # field = QgsField("dhru_area", QVariant.Double)
#   #   field = QgsField("dhru_area", QVariant.Double, 'double', 20, 5)
#   #   provider.addAttributes([field])
#   #   self.layer.updateFields()
    
#   # feats = self.layer.getFeatures()
#   # self.layer.startEditing()

#   # for feat in feats:
#   #    area = feat.geometry().area()
#   #    #score = scores[i]
#   #    feat['dhru_area'] = area
#   #    self.layer.updateFeature(feat)
#   # self.layer.commitChanges()



#   self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]
#   provider = self.layer.dataProvider()

#   # layer = iface.activeLayer()
#   # provider = layer.dataProvider()

#   areas = [ feat.geometry().area() 
#             for feat in self.layer.getFeatures() ]
#   self.layer.startEditing()
#   if self.layer.dataProvider().fields().indexFromName( "dhru_area" ) == -1:
    
#       # field = QgsField("dhru_area", QVariant.Double)
#       field = QgsField("dhru_area", QVariant.Double, 'double', 20, 5)
#       provider.addAttributes([field])
#       self.layer.updateFields()

#       # field = QgsField("area", QVariant.Double)
#       # provider.addAttributes([field])
#       # layer.updateFields()

#       idx = self.layer.fieldNameIndex('dhru_area')

#       for area in areas:
#           new_values = {idx : float(area)}
#           provider.changeAttributeValues({areas.index(area):new_values})
#   self.layer.commitChanges()


def hru_dhru(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]
    input2 = QgsMapLayerRegistry.instance().mapLayersByName("sub (SWAT)")[0]    
    name = "hru_dhru_"
    name_ext = "hru_dhru_.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file = os.path.normpath(output_dir + "/" + name)

    #output_dir_1 = os.path.normpath(output_dir + "/" + "shapefiles_out")        

    # output = os.path.normpath(output_dir + "/" + "shapefiles_out" + "/" + name )

    # runinng the actual routine: 
    #processing.runalg('qgis:union', input, input2, output)
    # processing.runalg('qgis:intersect', input1, input2, True, output_file)

    processing.runalg('saga:intersect', input1, input2, True, output_file)

    # defining the outputfile to be loaded into the canvas        
    hru_dhru_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(hru_dhru_shapefile, '{0} ({1})'.format("hru_dhru","--"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    sm_group = root.findGroup("SWAT-MODFLOW")   
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    sm_group.insertChildNode(1, QgsLayerTreeLayer(layer))

def hru_dhru_dissolve(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (--)")[0]
    name = "hru_dhru"
    name_ext = "hru_dhru.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file = os.path.normpath(output_dir + "/" + name)
    fieldName = "dhru_id"

    # runinng the actual routine: 
    processing.runalg('qgis:dissolve', input1, False, fieldName, output_file)

    # defining the outputfile to be loaded into the canvas        
    hru_dhru_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(hru_dhru_shapefile, '{0} ({1})'.format("hru_dhru","SWAT-MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    sm_group = root.findGroup("SWAT-MODFLOW")   
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    sm_group.insertChildNode(1, QgsLayerTreeLayer(layer))



##### This qgis:dissolve produces 'Null' row which causes an error.
# def dissolve_hru_dhru(self):
#   org_shps, SMshps, SMfolder, Table, SM_exes = self.dirs_and_paths()

#   name_ext = "hru_dhru.shp"
#   output_dir = SMshps
#   out_name = "hru_dhru_f.shp"

#   hru_dhru_shapefile = os.path.join(output_dir, name_ext)
#   output_file = os.path.normpath(output_dir + "/" + out_name)
    
#   processing.runalg('qgis:dissolve', hru_dhru_shapefile, False, "dhru_id", output_file)
#   layer = QgsVectorLayer(output_file, '{0} ({1})'.format("hru_dhru","SWAT-MODFLOW"), 'ogr')
#   layer = QgsMapLayerRegistry.instance().addMapLayer(layer)
####

# Create a field for filtering rows on area
def create_hru_dhru_filter(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (--)")[0]
    provider = self.layer.dataProvider()

    if self.layer.dataProvider().fields().indexFromName( "area_f" ) == -1:
        # field = QgsField("area_f", QVariant.Double, 'double', 20, 5)
        field = QgsField("area_f", QVariant.Double, 'double', 20, 5)

        provider.addAttributes([field])
        self.layer.updateFields()

    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
        area = feat.geometry().area()
        #score = scores[i]
        feat['area_f'] = area # abs function for negative area a bug produces same dhru_id
        self.layer.updateFeature(feat)
    self.layer.commitChanges()


def delete_hru_dhru_with_zero(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (--)")[0]
    provider = self.layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression('"area_f" < 1')
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    self.layer.startEditing()
    for f in self.layer.getFeatures(request):
        self.layer.deleteFeature(f.id())
    self.layer.commitChanges()

def dhru_grid(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("dhru (SWAT-MODFLOW)")[0]
    input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_grid (MODFLOW)")[0]

    name = "dhru_grid"
    name_ext = "dhru_grid.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file = os.path.normpath(output_dir + "/" + name)

    #output_dir_1 = os.path.normpath(output_dir + "/" + "shapefiles_out")        

    # output = os.path.normpath(output_dir + "/" + "shapefiles_out" + "/" + name )

    # runinng the actual routine: 
    #processing.runalg('qgis:union', input, input2, output)        
    processing.runalg('saga:intersect', input1, input2, True, output_file)

    # defining the outputfile to be loaded into the canvas        
    dhru_grid_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(dhru_grid_shapefile, '{0} ({1})'.format("dhru_grid","SWAT-MODFLOW"), 'ogr')

    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    sm_group = root.findGroup("SWAT-MODFLOW")   
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    sm_group.insertChildNode(1, QgsLayerTreeLayer(layer))

# Create a field for filtering rows on area
def create_dhru_grid_filter(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()

    # field = QgsField("ol_area", QVariant.Double, 'double', 20, 5)
    field = QgsField("ol_area", QVariant.Int)
    provider.addAttributes([field])
    self.layer.updateFields()

    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
        area = feat.geometry().area()
        #score = scores[i]
        feat['ol_area'] = area
        self.layer.updateFeature(feat)
    self.layer.commitChanges()


def delete_dhru_grid_with_zero(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression('"ol_area" < 1')
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    self.layer.startEditing()
    for f in self.layer.getFeatures(request):
        self.layer.deleteFeature(f.id())
    self.layer.commitChanges()


# Used for both SWAT and SWAT+
def river_grid(self): #step 1
    QSWATMOD_path_dict = self.dirs_and_paths()

    # Initiate rive_grid shapefile
    # if there is an existing river_grid shapefile, it will be removed
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.name() == ("river_grid (SWAT-MODFLOW)"):
            QgsMapLayerRegistry.instance().removeMapLayers([lyr.id()])
    if self.dlg.radioButton_mf_riv1.isChecked():
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("riv (SWAT)")[0]
        input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv1 (MODFLOW)")[0]
    elif self.dlg.radioButton_mf_riv2.isChecked():
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("riv (SWAT)")[0]
        input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv2 (MODFLOW)")[0]
    elif self.dlg.radioButton_mf_riv3.isChecked():
        input1 = QgsMapLayerRegistry.instance().mapLayersByName("riv (SWAT)")[0]
        input2 = QgsMapLayerRegistry.instance().mapLayersByName("mf_riv3 (MODFLOW)")[0]
    else:
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(':/newPrefix/pics/logo.png'))
        msgBox.setMaximumSize(1000, 200) # resize not working
        msgBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred) # resize not working
        msgBox.setWindowTitle("Hello?")
        msgBox.setText("Please, select one of the river options!")
        msgBox.exec_()

    name = "river_grid"
    name_ext = "river_grid.shp"
    output_dir = QSWATMOD_path_dict['SMshps']    
    output_file = os.path.normpath(output_dir + "/" + name_ext)

    # runinng the actual routine: 
    processing.runalg('qgis:union', input1, input2, output_file)        
    # processing.runalg('qgis:intersection', input1, input2, True, output_file) --> cause invalid geometry
    
    # defining the outputfile to be loaded into the canvas        
    river_grid_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(river_grid_shapefile, '{0} ({1})'.format("river_grid","SWAT-MODFLOW"), 'ogr')    
    # Put in the group
    root = QgsProject.instance().layerTreeRoot()
    sm_group = root.findGroup("SWAT-MODFLOW")   
    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    sm_group.insertChildNode(1, QgsLayerTreeLayer(layer))


def river_grid_delete_NULL(self):
    layer = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider = layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression("grid_id IS NULL" )
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    request2 = QgsFeatureRequest().setFilterExpression("subbasin IS NULL" )
    request2.setSubsetOfAttributes([])
    request2.setFlags(QgsFeatureRequest.NoGeometry)

    layer.startEditing()
    for f in layer.getFeatures(request):
        layer.deleteFeature(f.id())
    for f in layer.getFeatures(request2):
        layer.deleteFeature(f.id())

    layer.commitChanges()


# SWAT+
# Create a field for filtering rows on area
def create_river_grid_filter(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    field = QgsField("ol_length", QVariant.Double, 'double', 20, 5)
    #field = QgsField("ol_area", QVariant.Int)
    provider.addAttributes([field])
    self.layer.updateFields()

    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
       length = feat.geometry().length()
       #score = scores[i]
       feat['ol_length'] = length
       self.layer.updateFeature(feat)
    self.layer.commitChanges()


def delete_river_grid_with_threshold(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression('"rgrid_len" < 0.5')
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    self.layer.startEditing()
    for f in self.layer.getFeatures(request):
        self.layer.deleteFeature(f.id())
    self.layer.commitChanges()


def rgrid_len(self):

    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    from PyQt4.QtCore import QVariant
    from qgis.core import QgsField, QgsExpression, QgsFeature

    field = QgsField("rgrid_len", QVariant.Double, 'double', 20, 5)
    provider.addAttributes([field])
    self.layer.updateFields()
    
    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
       length = feat.geometry().length()
       #score = scores[i]
       feat['rgrid_len'] = length
       self.layer.updateFeature(feat)
    self.layer.commitChanges()


# SWAT+
def river_sub(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]
    input2 = QgsMapLayerRegistry.instance().mapLayersByName("sub (SWAT)")[0]
    name = "river_sub_union"
    name_ext = "river_sub_union.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file = os.path.normpath(output_dir + "/" + name)

    processing.runalg('qgis:union', input1, input2, output_file)

    # defining the outputfile to be loaded into the canvas        
    river_sub_union_shapefile = os.path.join(output_dir, name_ext)
    layer = QgsVectorLayer(river_sub_union_shapefile, '{0} ({1})'.format("river_sub","SWAT-MODFLOW"), 'ogr')
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)   

# SWAT+
def river_sub_delete_NULL(self):
    layer = QgsMapLayerRegistry.instance().mapLayersByName("river_sub (SWAT-MODFLOW)")[0]
    provider = layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression("grid_id IS NULL" )
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    request2 = QgsFeatureRequest().setFilterExpression("subbasin IS NULL" )
    request2.setSubsetOfAttributes([])
    request2.setFlags(QgsFeatureRequest.NoGeometry)

    layer.startEditing()
    for f in layer.getFeatures(request):
        layer.deleteFeature(f.id())
    for f in layer.getFeatures(request2):
        layer.deleteFeature(f.id())

    layer.commitChanges()

# SWAT+
def _create_river_sub_filter(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_sub (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    field = QgsField("ol_length", QVariant.Double, 'double', 20, 5)
    #field = QgsField("ol_area", QVariant.Int)
    provider.addAttributes([field])
    self.layer.updateFields()

    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
       length = feat.geometry().length()
       #score = scores[i]
       feat['ol_length'] = length
       self.layer.updateFeature(feat)
    self.layer.commitChanges()

def _delete_river_sub_with_threshold(self):
    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_sub (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    request =  QgsFeatureRequest().setFilterExpression('"ol_length" < 1.0')
    request.setSubsetOfAttributes([])
    request.setFlags(QgsFeatureRequest.NoGeometry)
    self.layer.startEditing()
    for f in self.layer.getFeatures(request):
        self.layer.deleteFeature(f.id())
    self.layer.commitChanges()


def _rgrid_len(self):

    self.layer = QgsMapLayerRegistry.instance().mapLayersByName("river_sub (SWAT-MODFLOW)")[0]
    provider = self.layer.dataProvider()
    from PyQt4.QtCore import QVariant
    from qgis.core import QgsField, QgsExpression, QgsFeature

    field = QgsField("rgrid_len", QVariant.Double, 'double', 20, 5)
    provider.addAttributes([field])
    self.layer.updateFields()
    
    feats = self.layer.getFeatures()
    self.layer.startEditing()

    for feat in feats:
       length = feat.geometry().length()
       #score = scores[i]
       feat['rgrid_len'] = length
       self.layer.updateFeature(feat)
    self.layer.commitChanges()

""" 
/********************************************************************************************
 *                                                                                          *
 *                              Export GIS Table for original SWAT                          *
 *                                                                                          *
 *******************************************************************************************/
"""

def export_hru_dhru(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    #sort by hru_id and then by dhru_id and save down 
    #read in the hru_dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (SWAT-MODFLOW)")[0]

    # Get the index numbers of the fields
    dhru_id_index = layer.dataProvider().fields().fieldNameIndex("dhru_id")
    dhru_area_index = layer.dataProvider().fields().fieldNameIndex("dhru_area")
    hru_id_index = layer.dataProvider().fields().fieldNameIndex("HRU_ID")
    hru_area_index = layer.dataProvider().fields().fieldNameIndex("hru_area")
    subbasin_index = layer.dataProvider().fields().fieldNameIndex("Subbasin")

    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(hru_id_index, dhru_id_index))
    dhru_number = len(l_sorted) # number of lines


    # Get hru number
    hru =[]
    # slice the column of interest in order to count the number of hrus
    for h in l:
        hru.append(h[hru_id_index])
 
    # Wow nice!!!
    hru_unique = []    
        
    for h in hru:
        if h not in hru_unique:
          hru_unique.append(h)
    hru_number = max(hru_unique)

#-----------------------------------------------------------------------#
    # exporting the file 
    name = "hru_dhru"
    output_dir = QSWATMOD_path_dict['Table']
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter='\t')
        first_row = [str(dhru_number)]  # prints the dhru number to the first row
        second_row = [str(hru_number)]  # prints the hru number to the second row
        
        third_row = ["dhru_id dhru_area hru_id subbasin hru_area"]
        
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)
        
        for item in l_sorted:
        
        # Write item to outcsv. the order represents the output order
            writer.writerow([item[dhru_id_index], item[dhru_area_index], item[hru_id_index],
                item[subbasin_index], item[hru_area_index]])


def export_dhru_grid(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]

    # Get the index numbers of the fields
    dhru_id_index = layer.dataProvider().fields().fieldNameIndex("dhru_id")
    dhru_area_index = layer.dataProvider().fields().fieldNameIndex("dhru_area")
    grid_id_index = layer.dataProvider().fields().fieldNameIndex("grid_id")
    overlap_area_index = layer.dataProvider().fields().fieldNameIndex("ol_area")

    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(grid_id_index, dhru_id_index))
    
    #l.sort(key=itemgetter(6))
    #add a counter as index for the dhru id
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nrow = int(data[0][1])
        ncol = int(data[0][2])
        delr = float(data[2][1]) # is the cell width along rows (x spacing)
        delc = float(data[3][1]) # is the cell width along columns (y spacing).

    cell_size = delr * delc
    number_of_grids = nrow * ncol

    for i in l_sorted:     
        i.append(str(int(cell_size))) # area of the grid
        
    ''' I don't know what this is for
    gridcell =[]
    # slice the column of interest in order to count the number of grid cells
    for h in l_sorted:
        gridcell.append(h[6])
  
    gridcell_unique = []    
        
    for h in gridcell:
        if h not in gridcell_unique:
          gridcell_unique.append(h)
    
    gridcell_number = len(gridcell_unique) # number of hrus
    '''

    info_number = len(l_sorted) # number of lines with information
    #-----------------------------------------------------------------------#
    # exporting the file 
    name = "dhru_grid"
    output_dir = QSWATMOD_path_dict['Table'] 
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dhru number to the file
        second_row = [str(number_of_grids)] # prints the total number of grid cells
        third_row = ["grid_id grid_area dhru_id overlap_area dhru_area"]
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)

        for item in l_sorted:
        #Write item to outcsv. the order represents the output order
            writer.writerow([
                item[grid_id_index], item[overlap_area_index + 1],
                item[dhru_id_index], item[overlap_area_index], item[dhru_area_index]])


def export_grid_dhru(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]
    layer2 = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (SWAT-MODFLOW)")[0]

    # Get max number of dhru id
    dhrus2 = [f.attribute("dhru_id") for f in layer2.getFeatures()]

    # Get the index numbers of the fields
    dhru_id_index = layer.dataProvider().fields().fieldNameIndex("dhru_id")
    dhru_area_index = layer.dataProvider().fields().fieldNameIndex("dhru_area")
    grid_id_index = layer.dataProvider().fields().fieldNameIndex("grid_id")
    overlap_area_index = layer.dataProvider().fields().fieldNameIndex("ol_area")

    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(dhru_id_index, grid_id_index))
    
    #l.sort(key=itemgetter(6))
    #add a counter as index for the dhru id
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nrow = int(data[0][1])
        ncol = int(data[0][2])
        delr = float(data[2][1]) # is the cell width along rows (x spacing)
        delc = float(data[3][1]) # is the cell width along columns (y spacing).

    cell_size = delr * delc
    number_of_grids = nrow * ncol

    for i in l_sorted:
        i.append(str(int(cell_size))) # area of the grid
        
    # # It
    # dhru_id =[]
    # # slice the column of interest in order to count the number of grid cells
    # for h in l_sorted:
    #   dhru_id.append(h[dhru_id_index])
  
    # dhru_id_unique = []    
        
    # for h in dhru_id:
    #   if h not in dhru_id_unique:
    #     dhru_id_unique.append(h)
    

    # It seems we need just total number of DHRUs not the one used in study area
    # dhru_number = len(dhru_id_unique) # number of dhrus
    dhru_number = max(dhrus2) # number of dhrus
    info_number = len(l_sorted) # number of lines with information
    #-----------------------------------------------------------------------#
    # exporting the file 
    name = "grid_dhru"
    output_dir = QSWATMOD_path_dict['Table'] 
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dnumber of lines with information
        second_row = [str(dhru_number)] # prints the total number of dhru
        third_row = [str(nrow)] # prints the row number to the file
        fourth_row = [str(ncol)] # prints the column number to the file     
        fifth_row = ["grid_id grid_area dhru_id overlap_area dhru_area"]
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)
        writer.writerow(fourth_row)
        writer.writerow(fifth_row)

        for item in l_sorted:
        #Write item to outcsv. the order represents the output order
            writer.writerow([item[grid_id_index], item[overlap_area_index + 1],
                item[dhru_id_index], item[overlap_area_index], item[dhru_area_index]])


def export_rgrid_len(self):
    QSWATMOD_path_dict = self.dirs_and_paths()  
    ### sort by dhru_id and then by grid and save down ### 
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("river_grid (SWAT-MODFLOW)")[0]

    # Get the index numbers of the fields
    grid_id_index = layer.dataProvider().fields().fieldNameIndex("grid_id")
    subbasin_index = layer.dataProvider().fields().fieldNameIndex("Subbasin")
    ol_length_index = layer.dataProvider().fields().fieldNameIndex("ol_length")
    
    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(grid_id_index))
    
    info_number = len(l_sorted) # number of lines
            
    #-----------------------------------------------------------------------#
    # exporting the file 
    
    name = "river_grid"
    output_dir = QSWATMOD_path_dict['Table']   
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dhru number to the file
        second_row = ["grid_id subbasin rgrid_len"]
        writer.writerow(first_row)
        writer.writerow(second_row)
        for item in l_sorted:
            # Write item to outcsv. the order represents the output order
            writer.writerow([item[grid_id_index], item[subbasin_index], item[ol_length_index]])



def run_CreateSWATMF(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    output_dir = QSWATMOD_path_dict['Table']

    #Out_folder_temp = self.dlg.lineEdit_output_folder.text()
    #swatmf = os.path.normpath(output_dir + "/" + "SWATMF_files")

    name = "CreateSWATMF.exe"
    
    exe_file = os.path.normpath(output_dir + "/" + name )
   
    #os.startfile(File_Physical)    
    p = subprocess.Popen(exe_file , cwd = output_dir) # cwd -> current working directory    
    p.wait()

def copylinkagefiles(self):
    QSWATMOD_path_dict = self.dirs_and_paths()
    source_dir = QSWATMOD_path_dict['Table']
    dest_dir = QSWATMOD_path_dict['SMfolder']
    for filename in glob.glob(os.path.join(source_dir, '*.txt')):
        shutil.copy(filename, dest_dir)




'''
grid_id = []
for feat in features:
    attrs = feat.attributes()
    grid_id.append(attrs[grid_id_index])

info_number = len(l) # Number of observation cells



# ------------ Export Data to file -------------- #
name = "modflow.obs"
output_dir = SMfolder
output_file = os.path.normpath(output_dir + "/" + name)
with open(output_file, "wb") as f:
    writer = csv.writer(f, delimiter = '\t')
    first_row = ["test"]
    second_row = [str(info_number)]
    for item in grid_id:
        writer.writerow([item])
'''

    
#*******************************************************************************************                                                                                        *
#                                                                                           *
#                               Export GIS Table for SWAT+ MODFLOW
#                          
#*******************************************************************************************/


def _export_hru_dhru(self): 
    #sort by hru_id and then by dhru_id and save down 
    #read in the hru_dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("hru_dhru (SWAT-MODFLOW)")[0]
    
    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(2, 0))
    dhru_number = len(l_sorted) # number of lines


    # Get hru number
    hru =[]
    # slice the column of interest in order to count the number of hrus
    for h in l:
        hru.append(h[0])
 
    # Wow nice!!!
    hru_unique = []    
        
    for h in hru:
        if h not in hru_unique:
          hru_unique.append(h)
    hru_number =  max(hru_unique)


#-----------------------------------------------------------------------#
    # exporting the file 
    name = "hru_dhru"
    output_dir = QSWATMOD_path_dict['Table']
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(dhru_number)] # prints the dhru number to the first row
        second_row = [str(hru_number)] # prints the hru number to the second row
        
        third_row = ["dhru_id dhru_area hru_id subbasin hru_area"]
        
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)
        
        for item in l_sorted:
        
        #Write item to outcsv. the order represents the output order
            writer.writerow([item[2], item[3], item[0], item[4], item[1]])


def _export_dhru_grid(self):
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]

    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(9, 2))
    
    #l.sort(key=itemgetter(6))
    #add a counter as index for the dhru id
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nrow = int(data[0][1])
        ncol = int(data[0][2])
        delr = float(data[2][1]) # is the cell width along rows (x spacing)
        delc = float(data[3][1]) # is the cell width along columns (y spacing).

    cell_size = delr * delc
    number_of_grids = nrow * ncol

    for i in l_sorted:     
        i.append(str(int(cell_size))) # area of the grid
        
    ''' I don't know what this is for
    gridcell =[]
    # slice the column of interest in order to count the number of grid cells
    for h in l_sorted:
        gridcell.append(h[6])
  
    gridcell_unique = []    
        
    for h in gridcell:
        if h not in gridcell_unique:
          gridcell_unique.append(h)
    
    gridcell_number = len(gridcell_unique) # number of hrus
    '''

    info_number = len(l_sorted) # number of lines with information
    #-----------------------------------------------------------------------#
    # exporting the file 
    name = "dhru_grid"
    output_dir = QSWATMOD_path_dict['Table'] 
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dhru number to the file
        second_row = [str(number_of_grids)] # prints the total number of grid cells
        third_row = ["grid_id grid_area dhru_id overlap_area dhru_area"]
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)

        for item in l_sorted:
        #Write item to outcsv. the order represents the output order
            writer.writerow([item[9], item[11], item[2], item[10], item[3]])



def _export_grid_dhru(self):    
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("dhru_grid (SWAT-MODFLOW)")[0]

    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(2, 9))
    
    #l.sort(key=itemgetter(6))
    #add a counter as index for the dhru id
    for filename in glob.glob(str(QSWATMOD_path_dict['SMfolder'])+"/*.dis"):
        with open(filename, "r") as f:
            data = []
            for line in f.readlines():
                if not line.startswith("#"):
                    data.append(line.replace('\n', '').split())
        nrow = int(data[0][1])
        ncol = int(data[0][2])
        delr = float(data[2][1]) # is the cell width along rows (x spacing)
        delc = float(data[3][1]) # is the cell width along columns (y spacing).

    cell_size = delr * delc
    number_of_grids = nrow * ncol

    for i in l_sorted:     
        i.append(str(int(cell_size))) # area of the grid
        

    dhru_id =[]
    # slice the column of interest in order to count the number of grid cells
    for h in l_sorted:
        dhru_id.append(h[2])
  
    dhru_id_unique = []    
        
    for h in dhru_id:
        if h not in dhru_id_unique:
          dhru_id_unique.append(h)
    
    dhru_number = len(dhru_id_unique) # number of dhrus
    info_number = len(l_sorted) # number of lines with information
    #-----------------------------------------------------------------------#
    # exporting the file 
    name = "grid_dhru"
    output_dir = QSWATMOD_path_dict['Table'] 
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dnumber of lines with information
        second_row = [str(dhru_number)] # prints the total number of dhru
        third_row = [str(nrow)] # prints the row number to the file
        fourth_row = [str(ncol)] # prints the column number to the file     
        fifth_row = ["grid_id grid_area dhru_id overlap_area dhru_area"]
        writer.writerow(first_row)
        writer.writerow(second_row)
        writer.writerow(third_row)
        writer.writerow(fourth_row)
        writer.writerow(fifth_row)

        for item in l_sorted:
        #Write item to outcsv. the order represents the output order
            writer.writerow([item[9], item[11], item[2], item[10], item[3]])


def _export_rgrid_len(self): 

    """
    sort by dhru_id and then by grid and save down 
    """
    #read in the dhru shapefile
    layer = QgsMapLayerRegistry.instance().mapLayersByName("river_sub (SWAT-MODFLOW)")[0]
    
    # transfer the shapefile layer to a python list
    l = []
    for i in layer.getFeatures():
        l.append(i.attributes())
    
    # then sort by columns
    import operator
    l_sorted = sorted(l, key=operator.itemgetter(22))
    
    info_number = len(l_sorted) # number of lines
            
    #-----------------------------------------------------------------------#
    # exporting the file 
    
    name = "river_grid"
    output_dir = QSWATMOD_path_dict['Table']   
    output_file = os.path.normpath(output_dir + "/" + name)

    with open(output_file, "wb") as f:
        writer = csv.writer(f, delimiter = '\t')
        first_row = [str(info_number)] # prints the dhru number to the file
        
        second_row = ["grid_id subbasin rgrid_len"]
        
        writer.writerow(first_row)
        writer.writerow(second_row)
        
        for item in l_sorted:
        
        #Write item to outcsv. the order represents the output order
            writer.writerow([item[22], item[23], item[25]])



'''
grid_id = []
for feat in features:
    attrs = feat.attributes()
    grid_id.append(attrs[grid_id_index])

info_number = len(l) # Number of observation cells



# ------------ Export Data to file -------------- #
name = "modflow.obs"
output_dir = QSWATMOD_path_dict['SMfolder']
output_file = os.path.normpath(output_dir + "/" + name)
with open(output_file, "wb") as f:
    writer = csv.writer(f, delimiter = '\t')
    first_row = ["test"]
    second_row = [str(info_number)]
    for item in grid_id:
        writer.writerow([item])
'''


def convert_r_v(self):
    input1 = QgsMapLayerRegistry.instance().mapLayersByName("HRU_swat")[0]
    fieldName = "hru_id"
            
    name1 = "hru_S"
    name_ext1 = "hru_S.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file1 = os.path.normpath(output_dir + "/" + name1)

    # runinng the actual routine: 
    processing.runalg('gdalogr:polygonize', input1, fieldName, output_file1)

    # defining the outputfile to be loaded into the canvas        
    hru_shapefile = os.path.join(output_dir, name_ext1)
    layer = QgsVectorLayer(hru_shapefile, '{0} ({1})'.format("hru","--"), 'ogr')
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)

def dissolve_hru(self):
    import ntpath
    import posixpath

    input2 = QgsMapLayerRegistry.instance().mapLayersByName("hru (--)")[0]
    fieldName = "hru_id"
            
    name2 = "hru_SM"
    name_ext2 = "hru_SM.shp"
    output_dir = QSWATMOD_path_dict['SMshps']
    output_file2 = os.path.normpath(output_dir + "/" + name2)

    # runinng the actual routine: 

    processing.runalg('qgis:dissolve', input2,False, fieldName, output_file2)
    # defining the outputfile to be loaded into the canvas        
    hru_shapefile = os.path.join(output_dir, name_ext2)
    layer = QgsVectorLayer(hru_shapefile, '{0} ({1})'.format("hru","SWAT"), 'ogr')
    layer = QgsMapLayerRegistry.instance().addMapLayer(layer)

    if os.name == 'nt':
        hru_shp = ntpath.join(output_dir, name2 + ".shp")
    else:
        hru_shp = posixpath.join(output_dir, name2 + ".shp")
    self.dlg.lineEdit_hru_rasterfile.setText(hru_shp)  