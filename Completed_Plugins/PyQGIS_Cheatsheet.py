### KOMŞU POLİGONLARIN ID LERİNİ YAZDIRMA ###

from qgis.utils import iface
from PyQt5.QtCore import QVariant

_NAME_FIELD = 'id'
_NEW_NEIGHBORS_FIELD = 'Neighboors'

layer = iface.activeLayer()
layer.startEditing()
layer.dataProvider().addAttributes(
        [QgsField(_NEW_NEIGHBORS_FIELD, QVariant.String)])
layer.updateFields()
feature_dict = {f.id(): f for f in layer.getFeatures()}

index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)
for f in feature_dict.values():
    print('Working on %s' % f[_NAME_FIELD])
    geom = f.geometry()

    intersecting_ids = index.intersects(geom.boundingBox())

    neighbors = []

    for intersecting_id in intersecting_ids:
        intersecting_f = feature_dict[intersecting_id]
        print(intersecting_f[_NAME_FIELD])

        if (f != intersecting_f and
                intersecting_f.geometry().intersects(geom)):
            neighbors.append(str(intersecting_f[_NAME_FIELD]))

    f[_NEW_NEIGHBORS_FIELD] = ','.join(neighbors)

    layer.updateFeature(f)

layer.commitChanges()
print('Processing complete.')