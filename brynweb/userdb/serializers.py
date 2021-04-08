from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from core.serializers import HashidsIntegerField
from openstack.serializers import TenantSerializer
from .models import (
    Invitation,
    LicenceAcceptance,
    LicenceVersion,
    TeamMember,
    Team,
    Profile,
)


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    default_team_membership = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), queryset=TeamMember.objects.all()
    )

    class Meta:
        model = Profile
        fields = [
            "default_keypair",
            "default_team_membership",
            "email_validated",
            "new_email_pending_verification",
        ]
        read_only_fields = ["email_validated", "new_email_pending_verification"]


class UserTeamMembershipsSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    team = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )

    class Meta:
        model = TeamMember
        fields = ["id", "team"]


class UserSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    profile = ProfileSerializer(many=False, read_only=False)
    team_memberships = UserTeamMembershipsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "team_memberships",
        ]
        read_only_fields = ["username"]

    def update(self, instance, validated_data):
        is_new_email = instance.email != validated_data.get("email", instance.email)

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        profile = instance.profile
        profile_data = validated_data.get("profile", None)

        if profile_data:
            profile.default_keypair = profile_data.get(
                "default_keypair", profile.default_keypair
            )
            profile.default_team_membership = profile_data.get(
                "default_team_membership", profile.default_team_membership
            )
            profile.save()

        if is_new_email:
            try:
                new_email = validated_data.get("email")
                profile.initiate_email_change(self.context["request"], new_email)
            except ValueError:
                raise serializers.ValidationError(
                    "An existing account is already associated with the new email address."
                )

        return instance


class TeamMemberUserSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class TeamMemberSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    team = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )
    user = TeamMemberUserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "user", "team", "is_admin"]


class InvitationSerializer(serializers.ModelSerializer):
    to_team = serializers.PrimaryKeyRelatedField(
        pk_field=HashidsIntegerField(), read_only=True
    )
    made_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Invitation
        fields = ["uuid", "email", "date", "message", "made_by", "to_team"]

    def validate(self, data):
        team = get_object_or_404(
            Team, pk=self.context["request"].resolver_match.kwargs["team_id"]
        )
        email = data["email"]
        team_users = team.users
        if Invitation.objects.filter(email=email, to_team=team, accepted=False).count():
            raise serializers.ValidationError(
                "There is already a pending invitation for this team and email address."
            )
        if team_users.filter(email=email).count():
            raise serializers.ValidationError(
                "There is already a current team member with this email address."
            )

        return data


class TeamSerializer(serializers.ModelSerializer):
    id = HashidsIntegerField(read_only=True)
    default_region = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )
    tenants = TenantSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "institution",
            "department",
            "phone_number",
            "verified",
            "default_region",
            "tenants_available",
            "tenants",
            "licence_expiry",
            "licence_is_valid",
        ]
        read_only_fields = [
            "id",
            "name",
            "verified",
            "tenants_available",
            "tenants",
            "licence_expiry",
            "licence_is_valid",
        ]


class LicenceVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenceVersion
        fields = ["version_number", "effective_date", "validity_period_days"]


class LicenceAcceptanceSerializer(serializers.ModelSerializer):
    team = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, pk_field=HashidsIntegerField()
    )
    version = LicenceVersionSerializer(read_only=True)

    class Meta:
        model = LicenceAcceptance
        fields = ["team", "user", "version", "accepted_at", "expiry"]
        read_only_fields = ["team", "user", "accepted_at", "version", "expiry"]
