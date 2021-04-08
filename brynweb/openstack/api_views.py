from operator import methodcaller

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response

from core import hashids
from core.permissions import IsOwner
from userdb.models import TeamMember
from userdb.permissions import IsTeamMemberPermission

from .service import OpenstackService, ServiceUnavailable, OpenstackException
from .models import HypervisorStats, KeyPair, ServerLease, ServerLeaseRequest, Tenant
from .serializers import (
    AttachmentSerializer,
    FlavorSerializer,
    HypervisorStatsSerializer,
    ImageSerializer,
    InstanceSerializer,
    KeyPairSerializer,
    ServerLeaseRequestSerializer,
    TenantSerializer,
    VolumeSerializer,
    VolumeTypeSerializer,
)

User = get_user_model()


class InvalidTenant(drf_exceptions.PermissionDenied):
    default_detail = (
        "The specified tenant does not exist, or user does not have team membership."
    )


def get_tenants_for_user(
    user: User, team_id: int = None, tenant_id: int = None
) -> QuerySet:
    """
    Return queryset for all tenant(s) owned by teams that the authenticated user is a member of.
    If tenant_id is specified: returns a single member queryset (only if the user is a team member).
    If team_id is specified: returns tenants belonging to this team (only if the user is a team member)
    """
    teams = user.teams.filter(pk=team_id) if team_id else user.teams.all()
    all_tenants = Tenant.objects.filter(team__in=teams).all()
    return all_tenants.filter(pk=tenant_id) if tenant_id else all_tenants


def get_tenant_for_user(user: User, tenant_id: int, team_id: int = None) -> Tenant:
    """
    Return a tenant for a given user, only if that user is a team member.
    If team_id is specified: will raise if the specified tenant does not belong to this team.
    If admin is specified: will raise if the user is not a team admin.
    """
    tenant = get_tenants_for_user(user, tenant_id=tenant_id, team_id=team_id).first()

    if not tenant:
        raise InvalidTenant

    if tenant.region.disabled:
        raise ServiceUnavailable

    return tenant


class OpenstackAPIView(APIView):
    """
    Base class for openstack api views.
    """

    # You'll need to set these attributes on subclass
    service = None
    serializer_class = None

    def get_transform_func(self, tenant):
        """
        Returns a func to map openstack response to required serializer data structure
        Override as required
        """

        def transform_func(obj):
            obj.tenant = tenant.pk
            obj.team = tenant.team.pk
            return obj

        return transform_func


class OpenstackRetrieveView(OpenstackAPIView):
    """
    Base class for simple openstack detail views.
    """

    def get(self, request, team_id, tenant_id, pk):
        tenant = get_tenant_for_user(
            request.user, tenant_id=tenant_id, team_id=team_id
        )  # may raise

        openstack = OpenstackService(tenant=tenant)
        transform_func = self.get_transform_func(tenant)
        try:
            response = methodcaller("get", pk)(getattr(openstack, self.service.value))
            data = transform_func(response)
            serialized = self.serializer_class(data)
        except Exception as e:
            if getattr(e, "code", None) == 404:
                raise drf_exceptions.NotFound
            raise OpenstackException(detail=str(e))

        return Response(serialized.data)


class OpenstackListView(OpenstackAPIView):
    """
    Base class for simple openstack collection views.
    """

    def get(self, request, team_id, tenant_id):
        tenant = get_tenant_for_user(
            request.user, team_id=team_id, tenant_id=tenant_id
        )  # may raise

        openstack = OpenstackService(tenant=tenant)
        transform_func = self.get_transform_func(tenant)
        try:
            response = methodcaller("get_list")(getattr(openstack, self.service.value))
            data = map(transform_func, response)
            serialized = self.serializer_class(data, many=True)
        except Exception as e:
            raise OpenstackException(detail=str(e))

        return Response(serialized.data)


class OpenstackCreateMixin(OpenstackAPIView):
    """
    Mixin to add create/post method to openstack api views.
    """

    def post(self, request, team_id, tenant_id):
        tenant = get_tenant_for_user(
            request.user, team_id=team_id, tenant_id=tenant_id
        )  # may raise
        openstack = OpenstackService(tenant=tenant)
        transform_func = self.get_transform_func(tenant)

        serialized = self.serializer_class(data=request.data)
        serialized.is_valid(raise_exception=True)

        try:
            response = methodcaller("create", serialized.data)(
                getattr(openstack, self.service.value)
            )
            transformed_response = transform_func(response)
            return Response(self.serializer_class(transformed_response).data)
        except Exception as e:
            raise OpenstackException(detail=str(e))


class OpenstackDeleteMixin(OpenstackAPIView):
    """
    Mixin to add delete method to openstack api views.
    """

    def delete(self, request, team_id, tenant_id, pk):
        tenant = get_tenant_for_user(
            request.user, team_id=team_id, tenant_id=tenant_id
        )  # may raise

        openstack = OpenstackService(tenant=tenant)
        try:
            methodcaller("delete", pk)(getattr(openstack, self.service.value))
        except Exception as e:
            if getattr(e, "code", None) == 404:
                raise drf_exceptions.NotFound
            raise OpenstackException(detail=str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)


class TenantListView(generics.ListAPIView):
    """
    Tenant list view.
    """

    serializer_class = TenantSerializer

    def get_queryset(self):
        return get_tenants_for_user(
            self.request.user, team_id=self.kwargs.get("team_id")
        )


def get_instance_transform_func(self, tenant):
    """
    Transform function factory for Instance views.
    """
    public_netname = tenant.region.regionsettings.public_network_name

    def transform_func(obj):
        obj.tenant = tenant.pk
        obj.team = tenant.team.pk
        obj.flavor = obj.flavor["id"]

        if self.request.method == "GET":
            # 'Missing' lease for a legacy server: assign team admin member
            assigned_teammember = TeamMember.objects.filter(
                team=tenant.team, is_admin=True
            ).first()
        else:
            # New server: assign logged in user's team membership
            assigned_teammember = TeamMember.objects.get(
                team=tenant.team, user=self.request.user
            )

        lease_defaults = {
            "server_id": obj.id,
            "server_name": obj.name,
            "tenant": tenant,
            "assigned_teammember": assigned_teammember,
            "shelved": True if "SHELVED" in obj.status else False,
        }
        lease, _created = ServerLease.objects.get_or_create(
            server_id=obj.id, defaults=lease_defaults
        )
        obj.lease_expiry = lease.expiry
        obj.lease_renewal_url = lease.renewal_url
        obj.lease_assigned_teammember = lease.assigned_teammember

        if public_netname in obj.addresses.keys():
            obj.ip = obj.addresses[public_netname][0]["addr"]
        else:
            obj.ip = None

        return obj

    return transform_func


class InstanceListView(OpenstackCreateMixin, OpenstackListView):
    """
    Instance list view.
    """

    serializer_class = InstanceSerializer
    service = OpenstackService.Services.SERVERS
    get_transform_func = get_instance_transform_func

    def post(self, request, *args, **kwargs):
        # Grab local keypair, append public key to data dict
        keypair_local = get_object_or_404(KeyPair, pk=request.data["keypair"])
        request.data["public_key"] = keypair_local.public_key
        return super().post(request, *args, **kwargs)


class InstanceDetailView(OpenstackDeleteMixin, OpenstackRetrieveView):
    """
    Instance detail view.
    """

    serializer_class = InstanceSerializer
    service = OpenstackService.Services.SERVERS
    get_transform_func = get_instance_transform_func

    # Define allowed state transitions & associated method names
    # top level is current status, 1st level is target status
    state_transitions = {
        "ACTIVE": {"ACTIVE": "reboot", "SHUTOFF": "stop", "SHELVED": "shelve"},
        "SHUTOFF": {"ACTIVE": "start", "SHELVED": "shelve"},
        "SHELVED": {"ACTIVE": "unshelve"},
        "SHELVED_OFFLOADED": {"ACTIVE": "unshelve"},
    }

    def delete(self, request, team_id, tenant_id, pk):
        # Update lease before delete
        lease = get_object_or_404(ServerLease, server_id=pk)
        lease.deleted = True
        lease.save()
        return super().delete(request, team_id, tenant_id, pk)

    def patch(self, request, team_id, tenant_id, pk):
        # Check for allowed updates
        target_status = request.data.get("status")
        lease_assigned_teammember = request.data.get("lease_assigned_teammember")

        if not (target_status or lease_assigned_teammember):
            raise drf_exceptions.ValidationError(
                "Only 'status' and 'leaseAssignedTeammember' fields can be updated via PATCH."
            )

        # Status transition
        if target_status:
            tenant = get_tenant_for_user(
                request.user, team_id=team_id, tenant_id=tenant_id
            )  # may raise
            openstack = OpenstackService(tenant=tenant)
            service = getattr(openstack, self.service.value)
            try:
                server = service.get(pk)
                current_status = server.status
                if (
                    current_status in ["SHELVED", "SHELVED_OFFLOADED"]
                    and tenant.region.unshelving_disabled
                ):
                    raise drf_exceptions.PermissionDenied(
                        f"Unshelving is disabled at {tenant.region.description}"
                    )
                method_name = self.state_transitions[current_status][target_status]
                methodcaller(method_name, server)(service)
            except Exception as e:
                if getattr(e, "code", None) == 404:
                    raise drf_exceptions.NotFound
                raise OpenstackException(detail=str(e))

            if "SHELVED" in target_status or "SHELVED" in current_status:
                # Update lease
                lease = get_object_or_404(ServerLease, server_id=pk)
                lease.shelved = "SHELVED" in target_status
                lease.save()
                if "SHELVED" in current_status:
                    # Renew lease on unshelve
                    lease.renew_lease(user=request.user)

        # Lease TeamMember assignment
        if lease_assigned_teammember:
            # Check request user is team admin
            try:
                TeamMember.objects.get(
                    user=request.user, team_id=team_id, is_admin=True
                )
            except TeamMember.DoesNotExist:
                raise drf_exceptions.PermissionDenied

            # Check assigned user is team member
            try:
                teammember_id = hashids.decode(lease_assigned_teammember)
                teammember = TeamMember.objects.get(pk=teammember_id, team_id=team_id)
            except TeamMember.DoesNotExist:
                raise drf_exceptions.ValidationError(
                    "Not a member of the team to which this server belongs"
                )

            # Update lease
            lease = ServerLease.objects.get(server_id=pk)
            lease.assigned_teammember = teammember
            lease.save()

        # Don't return detail representation, to avoid extra openstack api call
        return Response(status=status.HTTP_204_NO_CONTENT)


class FlavorListView(OpenstackListView):
    """
    Flavor list view.
    """

    serializer_class = FlavorSerializer
    service = OpenstackService.Services.FLAVORS


class ImageListView(OpenstackListView):
    """
    Image list view.
    """

    serializer_class = ImageSerializer
    service = OpenstackService.Services.IMAGES


class KeyPairListView(generics.ListCreateAPIView):
    """
    SSH key pair list view.
    """

    serializer_class = KeyPairSerializer

    def get_queryset(self):
        user = self.request.user
        return user.keypairs.all()


class KeyPairDetailView(generics.RetrieveDestroyAPIView):
    """
    SSH key pair detail view.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = KeyPairSerializer

    def get_queryset(self):
        user = self.request.user
        return user.keypairs.all()


def get_volume_transform_func(self, tenant):
    """
    Transform function factory for Volume views
    """

    def transform_func(obj):
        as_dict = obj.to_dict()
        as_dict["tenant"] = tenant.pk
        as_dict["team"] = tenant.team.pk
        as_dict["name"] = (
            obj.name.replace(tenant.created_tenant_name, "")
            if obj.name
            else str(obj.id)
        )
        return as_dict

    return transform_func


class VolumeDetailView(OpenstackDeleteMixin, OpenstackRetrieveView):
    """
    Volume detail view.
    """

    serializer_class = VolumeSerializer
    service = OpenstackService.Services.VOLUMES
    get_transform_func = get_volume_transform_func

    def patch(self, request, team_id, tenant_id, pk):
        tenant = get_tenant_for_user(
            request.user, team_id=team_id, tenant_id=tenant_id
        )  # may raise

        openstack = OpenstackService(tenant=tenant)
        service = getattr(openstack, self.service.value)
        attachments = request.data.get("attachments")
        try:
            if attachments is not None and len(attachments) == 0:
                # Detach
                methodcaller("detach", pk)(service)
            elif attachments:
                # Create attachment
                serialized_attachment = AttachmentSerializer(attachments[0])
                methodcaller("attach", pk, serialized_attachment.data["server_id"])(
                    service
                )
        except Exception as e:
            if getattr(e, "code", None) == 404:
                raise drf_exceptions.NotFound
            raise OpenstackException(detail=str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)


class VolumeListView(OpenstackCreateMixin, OpenstackListView):
    """
    Volume list view.
    """

    serializer_class = VolumeSerializer
    service = OpenstackService.Services.VOLUMES
    get_transform_func = get_volume_transform_func


class VolumeTypeListView(OpenstackListView):
    """
    Volume type list view.
    """

    serializer_class = VolumeTypeSerializer
    service = OpenstackService.Services.VOLUME_TYPES


class HypervisorStatsListView(generics.ListAPIView):
    """
    Hypervisor stats list view.
    """

    serializer_class = HypervisorStatsSerializer
    queryset = HypervisorStats.objects.all()


class ServerLeaseRequestCreateView(generics.CreateAPIView):
    """
    ServerListRequest create view.
    """

    permissions = [permissions.IsAuthenticated, IsTeamMemberPermission]
    serializer_class = ServerLeaseRequestSerializer
    queryset = ServerLeaseRequest.objects.all()

    def perform_create(self, serializer):
        """
        Set server_lease id from instance_id lookup, user from request.
        Send admin notification email.
        """
        server_lease = get_object_or_404(
            ServerLease, server_id=self.request.resolver_match.kwargs["instance_id"]
        )
        server_lease_request = serializer.save(
            server_lease=server_lease, user=self.request.user
        )
        server_lease_request.send_admin_notification_email()
