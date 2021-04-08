from rest_framework import serializers

from core.serializers import HashidsIntegerField
from . import INSTANCE_STATUS_VALUES
from .models import (
    HypervisorStats,
    KeyPair,
    Region,
    RegionSettings,
    ServerLease,
    ServerLeaseRequest,
    Tenant,
)


class RegionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionSettings
        fields = ["max_volume_size_gb"]
        read_only_fields = ["max_volume_size_gb"]


class RegionSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    settings = RegionSettingsSerializer(source="regionsettings")

    class Meta:
        model = Region
        fields = [
            "id",
            "name",
            "description",
            "disabled",
            "new_instances_disabled",
            "unshelving_disabled",
            "settings",
        ]


class TenantSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    team = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )
    region = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )

    class Meta:
        model = Tenant
        fields = ["id", "region", "team"]


class OpenstackBaseSerializer(serializers.Serializer):
    team = HashidsIntegerField(read_only=True)
    tenant = HashidsIntegerField(read_only=True)


class InstanceSerializer(OpenstackBaseSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    flavor = serializers.UUIDField()
    image = serializers.UUIDField(required=False)
    keypair = serializers.UUIDField(required=False)
    public_key = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=INSTANCE_STATUS_VALUES, required=False)
    ip = serializers.IPAddressField(read_only=True, required=False, allow_null=True)
    created = serializers.DateTimeField(read_only=True)
    lease_expiry = serializers.DateTimeField(
        read_only=True, required=False, allow_null=True
    )
    lease_renewal_url = serializers.URLField(
        read_only=True, required=False, allow_null=True
    )
    lease_assigned_teammember = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )


class ImageSerializer(OpenstackBaseSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()


class FlavorSerializer(OpenstackBaseSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    ram = serializers.IntegerField()
    vcpus = serializers.IntegerField()


class KeyPairSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = KeyPair
        fields = ["id", "user", "name", "public_key", "fingerprint"]


class AttachmentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    attachment_id = serializers.UUIDField(read_only=True)
    server_id = serializers.UUIDField()
    device = serializers.CharField(read_only=True)
    attached_at = serializers.DateTimeField(read_only=True)


class VolumeSerializer(OpenstackBaseSerializer):
    attachments = AttachmentSerializer(many=True, required=False)
    bootable = serializers.BooleanField(required=False, default=False)
    created_at = serializers.DateTimeField(read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(required=False, allow_null=True)
    size = serializers.IntegerField()
    status = serializers.CharField(read_only=True)
    volume_type = serializers.CharField(required=False)


class VolumeTypeSerializer(OpenstackBaseSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    is_default = serializers.BooleanField(read_only=True, default=False)


class HypervisorStatsSerializer(serializers.ModelSerializer):
    region = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )

    class Meta:
        model = HypervisorStats
        exclude = ["id"]


class ServerLeaseSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )

    class Meta:
        model = ServerLease
        fields = [
            "server_id",
            "server_name",
            "tenant",
            "user",
            "created_at",
            "last_renewed_at",
            "expiry",
            "renewal_count",
            "renewal_url",
        ]
        read_only_fields = [
            "server_id",
            "server_name",
            "tenant",
            "user",
            "expiry",
            "renewal_url",
        ]


class ServerLeaseRequestSerializer(serializers.ModelSerializer):
    server_lease = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )

    class Meta:
        model = ServerLeaseRequest
        fields = ["server_lease", "message", "user"]
