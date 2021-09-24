"""
    Geo conditions base class
"""
import logging

from marshmallow import Schema, fields

from py_abac.policy.conditions.base import ConditionBase, ABCMeta, abstractmethod

from shapely.geometry import LineString, Point, Polygon

LOG = logging.getLogger(__name__)

def is_location(value) -> bool:
    return isinstance(value, list)

class GeoCondition(ConditionBase, metaclass=ABCMeta):
    """
        Base class for geo location conditions
    """

    def __init__(self, values):
        self.values = values
        if values == None:
            return
        if not is_location(values):
            raise Exception("coordinates is not a list")
        polygon = Polygon(values)
        if not polygon.is_valid:
            raise Exception("Invalid coordinates in policy")

    def is_satisfied(self, ctx) -> bool:
        if not is_location(ctx.attribute_value):
            LOG.debug(
                "Invalid type '%s' for attribute value at path '%s' for element '%s'."
                " Condition not satisfied.",
                type(ctx.attribute_value),
                ctx.attribute_path,
                ctx.ace
            )
            return False
        return self._is_satisfied(ctx.attribute_value)

    @abstractmethod
    def _is_satisfied(self, what) -> bool:
        raise NotImplementedError()


class GeoConditionSchema(Schema):
    """
        Base JSON schema for GeoConditionSchema
    """
    values = fields.List(
        fields.Raw(required=True, allow_none=False),
        required=True,
        allow_none=False
    )
