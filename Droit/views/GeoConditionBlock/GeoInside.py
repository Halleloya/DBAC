"""
    Geo inside conditions
"""

from marshmallow import post_load

from .base import GeoCondition, GeoConditionSchema

from shapely.geometry import LineString, Point, Polygon


class GeoInside(GeoCondition):
    """
        Condition for polygon point 'what' is enclosed in polygon 'self.values'
    """

    def _is_satisfied(self, what) -> bool:
        shapely_polygon = Polygon(self.values)
        shapely_coordinate = Point(what)
        result = shapely_polygon.contains(shapely_coordinate)
        return result


class GeoInsideSchema(GeoConditionSchema):
    """
        JSON schema for GeoInside numeric condition
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        return GeoInside(**data)
