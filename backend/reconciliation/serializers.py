
from rest_framework import serializers


class DisagreementSerializer(serializers.Serializer):
    reason = serializers.CharField()
    record_id = serializers.CharField()
    organization = serializers.CharField()
    system_a_value = serializers.CharField(
        allow_null=True
    )
    system_b_value = serializers.CharField(
        allow_null=True
    )
    location = serializers.CharField()
    entry_id = serializers.CharField(
        allow_null=True
    )
