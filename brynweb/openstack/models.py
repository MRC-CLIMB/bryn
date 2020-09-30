from django.db import models
from django.contrib.auth.models import User

from django_slack import slack_message
from openstack.client import OpenstackClient

from userdb.models import Team, Region


class Tenant(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    created_tenant_id = models.CharField(max_length=50)
    auth_password = models.CharField(max_length=50)
    created_network_id = models.CharField(max_length=50, blank=True)

    def get_tenant_name(self):
        return "bryn:%d_%s" % (self.team.pk, self.team.name)

    def get_tenant_description(self):
        return "%s (%s)" % (self.team.name, self.team.creator.last_name)

    def get_client(self):
        client = OpenstackClient(
            self.region.name,
            username=self.get_auth_username(),
            password=self.auth_password,
            project_name=self.get_tenant_name(),
        )
        return client

    def get_server(self, uuid):
        client = self.get_client()
        nova = client.get_nova()
        return nova.servers.get(uuid)

    def get_images(self):
        client = self.get_client()
        glance = client.get_glance()

        return [(i.id, i.name) for i in glance.images.list()]

    def get_keys(self):
        client = self.get_client()
        nova = client.get_nova()
        return [(k.name, k.name) for k in nova.keypairs.list()]

    def get_flavors(self):
        client = self.get_client()
        nova = client.get_nova()
        return [(fl.name, fl.name) for fl in nova.flavors.list()]

    def get_auth_username(self):
        return self.get_tenant_name()

    def start_server(self, uuid):
        server = self.get_server(uuid)
        server.start()

    def stop_server(self, uuid):
        server = self.get_server(uuid)
        server.stop()

    def terminate_server(self, uuid):
        server = self.get_server(uuid)
        server.delete()

    def unshelve_server(self, uuid):
        server = self.get_server(uuid)
        server.unshelve()

    def reboot_server(self, uuid):
        server = self.get_server(uuid)
        server.reboot(reboot_type="HARD")

    def get_network_id(self):
        if self.region.regionsettings.requires_network_setup:
            return self.created_network_id
        else:
            # i.e. warwick
            return self.region.regionsettings.public_network_id

    def __str__(self):
        return "%s" % (self.get_tenant_name())


class ActionLog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    error = models.BooleanField()

    def save(self, *args, **kwargs):
        super(ActionLog, self).save(self, *args, **kwargs)
        if self.error:
            slack_message("openstack/error.slack", {"log": self})
        else:
            slack_message("openstack/success.slack", {"log": self})

    def __str__(self):
        if self.error:
            error_type = "ERROR"
        else:
            error_type = "SUCCESS"
        return "%s %s %s %s" % (self.date, error_type, self.tenant, self.message)


class HypervisorStats(models.Model):
    region = models.OneToOneField(Region, on_delete=models.CASCADE)

    last_updated = models.DateTimeField(auto_now=True)

    hypervisor_count = models.IntegerField()
    disk_available_least = models.IntegerField()
    free_disk_gb = models.IntegerField()
    free_ram_mb = models.IntegerField()
    local_gb = models.IntegerField()
    local_gb_used = models.IntegerField()
    memory_mb = models.IntegerField()
    memory_mb_used = models.IntegerField()
    running_vms = models.IntegerField()
    vcpus = models.IntegerField()
    vcpus_used = models.IntegerField()


class RegionSettings(models.Model):
    region = models.OneToOneField(Region, on_delete=models.CASCADE)
    public_network_name = models.CharField(max_length=50)
    public_network_id = models.CharField(max_length=50)
    requires_network_setup = models.BooleanField(default=False)
    floating_ip_pool = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return str(self.region)


def get_tenant_for_team(team, region):
    tenant = Tenant.objects.filter(team=team, region=Region.objects.get(name=region))
    if not tenant:
        return None
    if len(tenant) > 1:
        return None
    return tenant[0]
