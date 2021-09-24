from shapely.geometry import Polygon
class GeographyBase:
    def __init__(self, level : str , coordinates : list, validate : bool):
        self.level = level
        p = Polygon(coordinates)
        if validate:
            if not isinstance(coordinates, list):
                raise TypeError("Coordinates must be a list")
            if not len(coordinates) > 0:
                raise TypeError("There should atleast be more than one element in the list")
            if not p.is_valid:
                raise TypeError("Cannot construct a valid polygon from the input coordinates")
        self.coordinates = coordinates
        self.polygon = p

    def AddOrUpdateBoundingBox(self):
        raise NotImplementedError()

    def Intersects(self, coordinates: list) -> list:
        raise NotImplementedError()

    def GetThingsInPolygon(self, coordinates: list) -> list:
        raise NotImplementedError()

    def GeoCoordinatesFromPolygon(self, p):
        x, y = p.exterior.coords.xy
        coords = []
        for idx, val in enumerate(x):
            point = []
            point.append(x[idx])
            point.append(y[idx])
            coords.append(point)
        return coords



