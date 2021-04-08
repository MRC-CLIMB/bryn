import time

from novaclient import client as novaclient
from keystoneauth1 import session as keystonesession
from keystoneauth1.identity import v3

# from keystoneclient.v2_0 import client as keystoneclient
from keystoneclient.v3 import client as keystoneclient
from glanceclient import Client as GlanceClient
from cinderclient import client as cinderclient

from enum import Enum
from rest_framework import exceptions as drf_exceptions
from rest_framework import status

from . import auth_settings


class ServiceUnavailable(drf_exceptions.APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class OpenstackException(drf_exceptions.APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected exception occurred."
    default_code = "openstack_exception"


class OpenstackService:
    class Services(Enum):
        IMAGES = "images"
        FLAVORS = "flavors"
        KEYPAIRS = "keypairs"
        SERVERS = "servers"
        VOLUMES = "volumes"
        VOLUME_TYPES = "volume_types"

    def __init__(self, tenant=None, region=None):
        if not (tenant or region):
            raise OpenstackException(
                "Either 'tenant' or 'region' is required to create an OpenstackService instance."
            )

        self.tenant = tenant
        if tenant:
            self.region = tenant.region
        else:
            self.region = region

        self._session = None
        self._nova = None
        self._cinder = None
        self._glance = None
        self._keystone = None

        self.auth_settings = auth_settings.AUTHENTICATION[self.region.name]
        self.images = ImagesService(self)
        self.flavors = FlavorsService(self)
        self.keypairs = KeypairsService(self)
        self.servers = ServersService(self)
        self.volumes = VolumesService(self)
        self.volume_types = VolumeTypesService(self)

    @property
    def session(self):
        if not self._session:
            if self.tenant:  # Service user for project operations
                username = self.auth_settings["SERVICE_USERNAME"]
                password = self.auth_settings["SERVICE_PASSWORD"]
                project_id = self.tenant.created_tenant_id
                project_name = None
            else:  # Admin user for domain operations
                username = self.auth_settings["ADMIN_USERNAME"]
                password = self.auth_settings["ADMIN_PASSWORD"]
                project_id = None
                project_name = self.auth_settings["TENANT_NAME"]
            auth = v3.Password(
                auth_url=self.auth_settings["AUTH_URL"],
                username=username,
                password=password,
                project_id=project_id,
                project_name=project_name,
                user_domain_id="default",
                project_domain_id="default",
            )
            self._session = keystonesession.Session(auth=auth)
        return self._session

    @property
    def nova(self):
        if not self._nova:
            self._nova = novaclient.Client(2, session=self.session)
        return self._nova

    @property
    def cinder(self):
        if not self._cinder:
            self._cinder = cinderclient.Client(3, session=self.session)
        return self._cinder

    @property
    def glance(self):
        if not self._glance:
            self._glance = GlanceClient(2, session=self.session)
        return self._glance

    @property
    def keystone(self):
        if not self._keystone:
            if "ADMIN_URL" in self.auth_settings:
                self._keystone = keystoneclient.Client(
                    token=self.session.get_token(),
                    endpoint=self.auth_settings["ADMIN_URL"],
                )
            else:
                self._keystone = keystoneclient.Client(session=self.session)
        return self._keystone


class KeypairsService:
    def __init__(self, openstack):
        self.openstack = openstack

    @property
    def nova(self):
        return self.openstack.nova

    def create(self, data):
        return self.nova.keypairs.create(
            name=data.get("name"), public_key=data.get("public_key")
        )

    def find_or_create(self, name, public_key):
        """
        Create an openstack KeyPair for the tenant, unless it already exists.
        Local instance id (UUID) used for the openstack name.
        """
        for existing in self.get_list():
            if existing.name == name:
                return existing
        return self.create({"name": name, "public_key": public_key})

    def get(self, keypair_id):
        return self.nova.keypairs.get(keypair_id)

    def get_list(self):
        return self.nova.keypairs.list()

    def delete(self, keypair_id):
        keypair = self.get(keypair_id)
        return keypair.delete()


class ImagesService:
    def __init__(self, openstack):
        self.openstack = openstack

    @property
    def glance(self):
        return self.openstack.glance

    def get_list(self):
        return self.glance.images.list()


class FlavorsService:
    def __init__(self, openstack):
        self.openstack = openstack

    @property
    def nova(self):
        return self.openstack.nova

    def get_list(self):
        return self.nova.flavors.list()


class VolumesService:
    def __init__(self, openstack):
        self.openstack = openstack

    @property
    def cinder(self):
        return self.openstack.cinder

    @property
    def nova(self):
        return self.openstack.nova

    def get(self, volume_id):
        return self.cinder.volumes.get(volume_id)

    def get_list(self):
        return self.cinder.volumes.list()

    def create(self, data):
        return self.cinder.volumes.create(
            imageRef=data.get("image"),
            name=data.get("name"),
            size=data.get("size"),
            volume_type=data.get("volumeType", self.openstack.volume_types.default),
        )

    def delete(self, volume_id):
        volume = self.get(volume_id)
        if volume.status != "available":
            raise OpenstackException(
                "Only volumes with 'available' status can be deleted."
            )
        return volume.delete()

    def attach(self, volume_id, server_id):
        return self.nova.volumes.create_server_volume(server_id, volume_id, None)

    def detach(self, volume_id):
        volume = self.get(volume_id)
        attachments = volume.attachments
        if not attachments:
            raise OpenstackException("Volume has no attachments to detach")
        server_id = attachments[0].get("server_id")
        return self.nova.volumes.delete_server_volume(server_id, volume_id)


class VolumeTypesService:
    def __init__(self, openstack):
        self.openstack = openstack
        self._default = None

    @property
    def cinder(self):
        return self.openstack.cinder

    @property
    def default(self):
        if not self._default:
            self._default = self.cinder.volume_types.default().id
        return self._default

    def get_list(self):
        volume_types = self.cinder.volume_types.list(is_public=True)
        for volume_type in volume_types:
            volume_type.is_default = volume_type.id == self.default
        return volume_types


class ServersService:
    def __init__(self, openstack):
        self.openstack = openstack

    @property
    def nova(self):
        return self.openstack.nova

    @property
    def cinder(self):
        return self.openstack.cinder

    @property
    def network_id(self):
        return self.openstack.tenant.get_network_id()

    def get(self, uuid):
        return self.nova.servers.get(uuid)

    def get_list(self):
        return self.nova.servers.list(detailed=True)

    def create(self, data):
        flavor = data["flavor"]
        image = data["image"]
        keypair = data["keypair"]
        public_key = data["public_key"]
        name = data["name"]

        # Create keypair if it doesn't yet exist for this tenant
        self.openstack.keypairs.find_or_create(keypair, public_key)

        # Create boot volume
        volume = self.cinder.volumes.create(
            imageRef=image, name=f"{name}: BOOT VOLUME", size=120,
        )
        self.cinder.volumes.set_bootable(volume, True)

        # Wait for boot volume availability
        for n in range(60):
            # TODO: move volume creation to frontend, otherwise tidy up a bit
            v = self.cinder.volumes.get(volume.id)
            if v.status == "available":
                break
            time.sleep(1)

        # Block device mapping
        bdm = [
            {
                "uuid": volume.id,
                "source_type": "volume",
                "destination_type": "volume",
                "boot_index": "0",
                "delete_on_termination": True,
            }
        ]

        # Create server
        return self.nova.servers.create(
            name,
            "",
            flavor=flavor,
            nics=[{"net-id": self.network_id}],
            key_name=keypair,
            block_device_mapping_v2=bdm,
        )

    def delete(self, server_id):
        server = self.get(server_id)
        if server.status not in ["SHELVED", "SHELVED_OFFLOADED"]:
            raise OpenstackException("Only SHELVED servers can be deleted via Bryn.")
        server.delete()

    def reboot(self, server):
        server.reboot(reboot_type="HARD")

    def stop(self, server):
        server.stop()

    def start(self, server):
        server.start()

    def shelve(self, server):
        server.shelve()

    def unshelve(self, server):
        server.unshelve()
