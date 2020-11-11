import time

# Get Layer and Feautures
activelayer = iface.activeLayer()
layer_name = "Memory Layer"

def MemoryPolygonLayer(layer):
    #Create Memory Layer
    memory_layer = QgsVectorLayer("Polygon?crs=epsg:4326", layer_name, "memory")
    memory_layer_data = memory_layer.dataProvider()
    attr = layer.dataProvider().fields().toList()
    memory_layer_data.addAttributes(attr)
    memory_layer.updateFields()
    
    feats = [feat for feat in layer.getFeatures()]
    memory_layer_data.addFeatures(feats)
    return memory_layer

def SpatialIndex(mem_layer):
    #Create Spatial Index
    index = QgsSpatialIndex()
    for f in mem_layer.getFeatures():
        index.insertFeature(f)
    return index

def GeometryControl(geom):
    # Check Geometry Type and Return Biggest Polygon
    areas = []
    geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
    
    if geomSingleType:
        return geom
        
    elif geom.isEmpty():
        print("Geometry Error !")
        return geom
    else:
        for i in geom.asGeometryCollection():
            if i.type() == QgsWkbTypes.PointGeometry:
                print("Point geometry removed")
            elif i.type() == QgsWkbTypes.LineGeometry:
                print("Line geometry removed")
            elif i.type() == QgsWkbTypes.PolygonGeometry:
                areas.append([i.area(),i])
            elif i.type() == QgsWkbTypes.UnknownGeometry:
                print("Unknown geometry removed")
        print("Biggest area selected")
        return (max(areas)[1])
    
    
def feature_difference(layer):
    # Get the intersects polygons and difference from neihghboor
    start = time.time()
    
    mem_layer = MemoryPolygonLayer(layer)
    index = SpatialIndex(mem_layer)
     
    for f1 in mem_layer.getFeatures():
        geom1 = f1.geometry()
        intersecting_ids = index.intersects(geom1.boundingBox())

        request = QgsFeatureRequest()
        request.setFilterFids(intersecting_ids)
        features = mem_layer.getFeatures(request)
        
        for f2 in features:
            if f1['id'] != f2['id'] and f2['id'] is not None:
                geom2 = f2.geometry()
                new_geom = geom1.difference(geom2)

                if new_geom.area() != geom1.area():
                    if new_geom.type() == QgsWkbTypes.UnknownGeometry:
                        print("Unknown Geometry Type Detected !", "in id: ",f1['id'])
                        new_geom = GeometryControl(new_geom)
                        new_geom = new_geom if new_geom.isEmpty() == False else geom1

                    mem_layer.dataProvider().changeGeometryValues({f1.id(): new_geom})
                    geom1 = new_geom
                    
    mem_layer.updateFields()
    end = time.time()
    print(round(end-start,6)," time elapsed for difference")
    
    return mem_layer


def featurebuffer(layer):
    mem_layer = MemoryPolygonLayer(layer)
    
    for f1 in mem_layer.getFeatures():
        geom1 = f1.geometry()
        buffer= geom1.buffer(0.00001,5)
        mem_layer.dataProvider().changeGeometryValues({f1.id(): buffer})

    mem_layer.updateFields()
    end = time.time()
    
    return mem_layer
   
   
buffered_layer = featurebuffer(activelayer)
memory_layer = feature_difference(buffered_layer)

QgsProject.instance().addMapLayer(memory_layer)

#if iface.mapCanvas().isCachingEnabled():
#    layer.triggerRepaint()
#else:
#    iface.mapCanvas().refresh()

