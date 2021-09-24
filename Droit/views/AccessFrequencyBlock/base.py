"""
    Access frequency base class
"""
import logging

from marshmallow import Schema, fields

from py_abac.policy.conditions.base import ConditionBase, ABCMeta, abstractmethod

from shapely.geometry import LineString, Point, Polygon

LOG = logging.getLogger(__name__)

def is_valid_argument(value) -> bool:
    isValid = isinstance(value, list) and len(value) == 2
    isValid = isValid & value[0] > 0 and value[1] > 0
    return isValid

class AccessFrequency(ConditionBase, metaclass=ABCMeta):
    """
        Base class for AccessFrequency conditions
    """

    def __init__(self, values):
        self.values = values
        if values == None:
            return
        if not is_valid_argument(values):
            raise Exception("Arguments in the access frequency policy must be a list of length 2. The element value must be greater than zero")

    def is_satisfied(self, ctx) -> bool:
        return self._is_satisfied(ctx.attribute_value)

    @abstractmethod
    def _is_satisfied(self, what) -> bool:
        raise NotImplementedError()


class AccessFrequencySchema(Schema):
    """
        Base JSON schema for AccessFrequencySchema
    """
    values = fields.List(
        fields.Raw(required=True, allow_none=False),
        required=True,
        allow_none=False
    )
