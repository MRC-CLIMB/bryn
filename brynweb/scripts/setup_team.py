# from django.contrib.auth.models import User
# from userdb.models import Team
# from openstack.client import OpenstackClient, get_admin_credentials
# from openstack.models import Region, Tenant

# # from scripts.set_quotas import set_quota


# def setup_network(client, region, tenant_id):
#     neutron = client.get_neutron()

#     network = {
#         "tenant_id": tenant_id,
#         "name": "bryn:tenant-private",
#         "admin_state_up": True,
#     }
#     n = neutron.create_network({"network": network})

#     router = {
#         "tenant_id": tenant_id,
#         "name": "bryn:tenant-router",
#         "admin_state_up": True,
#     }
#     r = neutron.create_router({"router": router})

#     public_network = region.regionsettings.public_network_id

#     neutron.add_gateway_router(r["router"]["id"], {"network_id": public_network})

#     # add subnet

#     subnet = {
#         "name": "tenant1-192.168.0.0/24",
#         "enable_dhcp": True,
#         "network_id": n["network"]["id"],
#         "tenant_id": tenant_id,
#         "allocation_pools": [{"start": "192.168.0.50", "end": "192.168.0.200"}],
#         "gateway_ip": "192.168.0.1",
#         "ip_version": 4,
#         "cidr": "192.168.0.0/24",
#     }

#     # add name servers

#     s = neutron.create_subnet({"subnet": subnet})

#     # router-interface-add

#     neutron.add_interface_router(r["router"]["id"], {"subnet_id": s["subnet"]["id"]})

#     return n["network"]["id"]


# def setup_tenant(team, region):
#     client = OpenstackClient(region.name, **get_admin_credentials(region.name))
#     nova = client.get_nova()
#     keystone = client.get_keystone()

#     tenant = Tenant(team=team, region=region)

#     tenant_name = tenant.get_tenant_name()
#     tenant_description = tenant.get_tenant_description()

#     openstack_tenant = keystone.tenants.create(
#         tenant_name=tenant_name, description=tenant_description, enabled=True
#     )

#     username = tenant.get_auth_username()
#     password = User.objects.make_random_password(length=16)

#     keystone.users.create(
#         name=username, password=password, tenant_id=openstack_tenant.id
#     )

#     tenant.created_tenant_id = openstack_tenant.id
#     tenant.auth_password = password

#     # flip to user tenant
#     client = OpenstackClient(
#         region.name,
#         username=tenant.get_auth_username(),
#         password=tenant.auth_password,
#         project_name=tenant.get_tenant_name(),
#     )
#     nova = client.get_nova()

#     # security_group_name = "bryn:default"
#     #    group = nova.security_groups.create(
#     #        security_group_name,
#     #        'Automatic security group for %s' % (tenant_name)
#     #    )
#     group = nova.security_groups.find(name="default")

#     nova.security_group_rules.create(
#         group.id, ip_protocol="tcp", from_port=22, to_port=22
#     )
#     nova.security_group_rules.create(
#         group.id, ip_protocol="tcp", from_port=80, to_port=80
#     )
#     nova.security_group_rules.create(
#         group.id, ip_protocol="tcp", from_port=443, to_port=443
#     )

#     if region.regionsettings.requires_network_setup:
#         tenant.created_network_id = setup_network(
#             client, region, tenant.created_tenant_id
#         )

#     set_quota(tenant)

#     tenant.save()

#     team.tenants_available = True
#     team.save()


# # openstack quota set --cores 128 --ram 650000 --gigabytes 10000
# # --snapshots 100 6a0797bfd90d4aba820c427d4e8a60d9


# def run():
#     t = Team.objects.get(pk=1)
#     setup_tenant(t, Region.objects.get(name="bham"))


def setup_team():
    pass


def setup_tenant():
    pass
