from Droit.views.AbacGeography import AbacGeography
from Droit.views.GeographyBase import GeographyBase

def GetIntersectionForCoordinates(coordinates, level):
    abacGeography = AbacGeography(level, None)
    return abacGeography.Intersects(coordinates)

def GetIntersectionForBoundingBoxCoordinates(level, level_bb_coordinates, coordinates):
    abacGeography = AbacGeography(level, level_bb_coordinates)
    return abacGeography.Intersects(coordinates)


def AddLevelBoundingBox(level, bounding_box_polygon):
    abacGeography = AbacGeography(level, bounding_box_polygon)
    abacGeography.AddOrUpdateBoundingBox()

def GetCoordinatesForLevel(level):
    abacGeography = AbacGeography(level, None)
    return abacGeography.coordinates

def GeoCoordinatesFromPolygon(p):
    abacGeography = AbacGeography(None, None, False)
    return abacGeography.GeoCoordinatesFromPolygon(p)