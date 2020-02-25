from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.constants import STRING
from pynamodb.models import Model

AGENT_STATUS = ("OFF", "READY", "IN_CALL", "INACTIVE")


class EnumUnicodeAttribute(UnicodeAttribute):

    attr_type = STRING

    def serialize(self, value):
        if value not in AGENT_STATUS:
            raise ValueError(
                f"{self.attr_name} must be one of {AGENT_STATUS}, not '{value}'"
            )
        else:
            return UnicodeAttribute.serialize(self, value)


class AgentState(Model):
    class Meta:

        table_name = "agent_state"
        host = "http://localhost:8000"

    agent_id = UnicodeAttribute(hash_key=True)
    status = EnumUnicodeAttribute(null=True, default="OFF")
    cdc = NumberAttribute(null=True)
    latest_lead = UnicodeAttribute(null=True)
    last_action_time = UTCDateTimeAttribute(null=True)
