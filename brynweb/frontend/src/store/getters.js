import { createFindByIdGetter } from "@/utils/store";
import {
  ADMIN_TEAM_MEMBERS,
  DEFAULT_TEAM_ID,
  DEFAULT_TENANT,
  FILTER_TENANT,
  LOADING,
  TEAM,
  TENANTS,
  USER_IS_ADMIN,
  USER_FULL_NAME,
  GET_TEAM_BY_ID,
  GET_TENANT_BY_ID,
  GET_REGION_BY_ID,
  GET_REGION_FOR_TENANT,
  GET_REGION_NAME_FOR_TENANT,
  FAQS_KEYPAIRS,
  FAQS_SERVERS,
  FAQS_VOLUMES,
} from "./getter-types";

export const getters = {
  [DEFAULT_TEAM_ID](state) {
    return state.user.teamMemberships.find(
      (membership) => membership.id === state.user.profile.defaultTeamMembership
    )?.team;
  },

  [DEFAULT_TENANT](_state, getters) {
    return getters[TENANTS].find(
      (tenant) => tenant.region === getters[TEAM].defaultRegion
    );
  },

  [FAQS_KEYPAIRS](state) {
    return state.faqs.filter((faq) => faq.category === "KP");
  },

  [FAQS_SERVERS](state) {
    return state.faqs.filter((faq) => faq.category === "SV");
  },

  [FAQS_VOLUMES](state) {
    return state.faqs.filter((faq) => faq.category === "VL");
  },

  [FILTER_TENANT](state, getters) {
    return getters[TENANTS].find(
      (tenant) => tenant.id === state.filterTenantId
    );
  },

  [GET_TEAM_BY_ID](state) {
    return createFindByIdGetter(state.teams);
  },

  [GET_TENANT_BY_ID](_state, getters) {
    return createFindByIdGetter(getters[TENANTS]);
  },

  [GET_REGION_BY_ID](state) {
    return createFindByIdGetter(state.regions);
  },

  [GET_REGION_FOR_TENANT](_state, getters) {
    return (tenant) => getters[GET_REGION_BY_ID](tenant.region);
  },

  [GET_REGION_NAME_FOR_TENANT](_state, getters) {
    return (tenant) => {
      const region = getters[GET_REGION_FOR_TENANT](tenant);
      return region?.description?.replace("University of ", "");
    };
  },

  [LOADING](_state, getters) {
    return !getters[TEAM].initialized;
  },

  [TEAM](state) {
    return state.teams.find((team) => team.id === state.activeTeamId);
  },

  [TENANTS](state, getters) {
    return state.activeTeamId
      ? getters[TEAM].tenants
          .filter((tenant) => {
            const region = getters[GET_REGION_FOR_TENANT](tenant);
            return !region.disabled; // Exclude tenants at disabled regions
          })
          .map((tenant) => {
            const region = getters[GET_REGION_FOR_TENANT](tenant);
            tenant.newInstancesDisabled = region.newInstancesDisabled; // Convenience newInstancesDisabled property
            tenant.unshelvingDisabled = region.unshelvingDisabled;
            return tenant;
          })
      : [];
  },

  [USER_FULL_NAME](state) {
    return `${state.user.firstName} ${state.user.lastName}`;
  },

  [USER_IS_ADMIN](state, getters) {
    return getters[ADMIN_TEAM_MEMBERS].some(
      (member) => member.user.id === state.user.id
    );
  },
};

export default getters;
