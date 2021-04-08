// Axios config
import axios from "axios";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.timeout = 30000;

const apiBase = "/api/";
const teamBase = apiBase + "teams/TEAM_ID/";
const tenantBase = teamBase + "tenants/TENANT_ID/";
const instanceBase = tenantBase + "instances/INSTANCE_ID/";

const apiRoutes = {
  announcements: apiBase + "announcements/",
  hypervisorStats: apiBase + "hypervisor-stats/",
  images: tenantBase + "images/",
  instances: tenantBase + "instances/",
  invitations: teamBase + "invitations/",
  faqs: apiBase + "faqs/",
  flavors: tenantBase + "flavors/",
  keyPairs: apiBase + "keypairs/",
  licenceAcceptances: teamBase + "licence-acceptances/",
  messages: apiBase + "messages/",
  serverLeaseRequest: instanceBase + "lease-requests/",
  teams: apiBase + "teams/",
  teamMembers: teamBase + "members/",
  userProfile: apiBase + "userprofile/",
  volumes: tenantBase + "volumes/",
  volumeTypes: tenantBase + "volumetypes/",
};

const getAPIRoute = (
  routeName,
  teamId = null,
  tenantId = null,
  instanceId = null
) => {
  let route = apiRoutes[routeName];
  if (teamId != null) {
    route = route.replace("TEAM_ID", teamId);
  }
  if (tenantId != null) {
    route = route.replace("TENANT_ID", tenantId);
  }
  if (instanceId != null) {
    route = route.replace("INSTANCE_ID", instanceId);
  }
  return route;
};

export { axios, apiRoutes, getAPIRoute };
