from .GeographyBase import GeographyBase
from Droit.models import LevelBoundingBox, ThingDescription
from shapely.geometry import Polygon
from mongoengine.fields import PolygonField, LineStringField

class AbacGeography(GeographyBase):
    def __init__(self, level: str, coordinates : list, validate = False):
        if coordinates == None and level != None:
            coordinates = self.GetCoordinatesForLevel(level)
        GeographyBase.__init__(self, level, coordinates, validate)

    def AddOrUpdateBoundingBox(self):
        dict_coordinates = {}
        dict_coordinates['type'] = 'Polygon'
        list_wrapper = []
        list_wrapper.append(self.coordinates)
        #list_wrapper is necessary because the
        #shapely expects a list of points as a polygon
        #and the database expects a list of list of points
        #as polygon
        dict_coordinates['coordinates'] = list_wrapper
        level_bounding_box = LevelBoundingBox.objects(level = self.level.lower()).first()
        if level_bounding_box == None:
            LevelBoundingBox(level = self.level.lower(), geometry = dict_coordinates).save()
        else:
            level_bounding_box.geometry = dict_coordinates
            level_bounding_box.save()

    def Intersects(self, coordinates: list) -> list:
        p = Polygon(coordinates)
        if not p.is_valid:
            raise TypeError("Invalid Coordinates to construct polygon")
        #No intersection
        if not self.polygon.intersects(p):
            return None
        return self.polygon.intersection(p)

    def GetThingsInPolygon(self , coordinates: list) -> list:
         raw_query = {'properties.geo.coordinates': { '$geoWithin': {'$polygon': coordinates}}}
         things = ThingDescription.objects(__raw__=raw_query)
         return things

    def GetCoordinatesForLevel(self, level):
        level_bounding_box = LevelBoundingBox.objects(level = level.lower()).first()
        if level_bounding_box == None:
            print(f'Bounding box not configured for {level}')
            return None
        return level_bounding_box.geometry['coordinates'][0]

    def GeoCoordinatesFromPolygon(self, p):
        return GeographyBase.GeoCoordinatesFromPolygon(self, p)