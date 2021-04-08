from rest_framework import exceptions, serializers

from . import hashids


class HashidsFieldMixin:
    def to_representation(self, value):
        """Convert id to hashid"""
        rep = super().to_representation(value)
        return hashids.encode(rep)

    def to_internal_value(self, data):
        """Convert hashid to id"""
        try:
            decoded = hashids.decode(data)
        except ValueError:
            raise exceptions.NotFound
        return super().to_internal_value(decoded)


class HashidsIntegerField(HashidsFieldMixin, serializers.IntegerField):
    pass


class MessageSerializer(serializers.Serializer):
    level = serializers.IntegerField()
    level_tag = serializers.CharField()
    message = serializers.CharField()
    extra_tags = serializers.CharField()
