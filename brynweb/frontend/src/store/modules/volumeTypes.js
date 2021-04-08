import { axios, getAPIRoute } from "@/api";
import {
  updateTeamCollection,
  createFilterByTenantGetter,
} from "@/utils/store";
import { FETCH_TENANT_VOLUME_TYPES } from "@/store/action-types";
import { GET_VOLUME_TYPES_FOR_TENANT, TEAM } from "@/store/getter-types";
import { SET_VOLUME_TYPES } from "@/store/mutation-types";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [SET_VOLUME_TYPES](state, { volumeTypes, team, tenant }) {
    updateTeamCollection(state.all, volumeTypes, team, tenant);
  },
};

const getters = {
  [GET_VOLUME_TYPES_FOR_TENANT](state) {
    return createFilterByTenantGetter(state.all);
  },
};

const actions = {
  async [FETCH_TENANT_VOLUME_TYPES]({ commit, rootGetters }, tenant) {
    const team = rootGetters[TEAM];
    const url = getAPIRoute("volumeTypes", team.id, tenant.id);
    const response = await axios.get(url);
    const volumeTypes = response.data;
    commit(SET_VOLUME_TYPES, { volumeTypes, team, tenant });
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
