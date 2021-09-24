"""
    Geo inside conditions
"""

from marshmallow import post_load

from .base import AccessFrequency, AccessFrequencySchema

from Droit.models import DynamicAttributes

from datetime import datetime, timedelta

from flask_login import current_user


class AccessFrequencyLte(AccessFrequency):
    """
        Condition for checking access frequency is less than the number of times already accessed
    """

    def _is_satisfied(self, what) -> bool:
        policy_attributes = self.values
        request_attributes = what
        delete_old_dynamic_attributes(policy_attributes[1])
        thing_id = request_attributes[0]
        user_id = request_attributes[1]
        access_frequency = get_access_frequency(thing_id, user_id)
        #After validation only, the number of attempts is incremented
        #The current attempt is one more than the # of attempts stored in DB
        if access_frequency + 1 <= int(policy_attributes[0]):
            return True
        return False


class AccessFrequencyLteSchema(AccessFrequencySchema):
    """
        JSON schema for GeoInside numeric condition
    """

    @post_load
    def post_load(self, data, **_):  # pylint: disable=missing-docstring,no-self-use
        return AccessFrequencyLte(**data)

def delete_old_dynamic_attributes(m):
    delete_date_time = datetime.now() - timedelta(minutes= m)
    raw_query = {'attribute_date': {'$lte': delete_date_time}}
    dynamic_attributes = DynamicAttributes.objects(__raw__=raw_query)
    for dynamic_attribute in dynamic_attributes:
        dynamic_attribute.delete()

def get_access_frequency(thing_id, user_id):
    thing_access_frequency = DynamicAttributes.objects(attribute_id = thing_id,user_id = user_id).count()
    return thing_access_frequency
