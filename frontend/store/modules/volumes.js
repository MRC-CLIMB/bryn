import { axios, apiRoutes } from "@/api";
import {
  updateTeamCollection,
  collectionForTeamId,
  createFilterByTenantGetter,
} from "@/utils";

const state = () => {
  return {
    all: [],
    pollingSymbol: null,
    pollingTargetStatus: [],
    loading: false,
  };
};

const mutations = {
  addVolume(state, volume) {
    state.all.push(volume);
  },
  setVolumes(state, { volumes, team, tenant }) {
    updateTeamCollection(state.all, volumes, team, tenant);
  },
  setLoading(state, loading) {
    state.loading = loading;
  },
  updateVolume(state, volume) {
    const target = state.all.find((target) => target.id === volume.id);
    if (volume) {
      Object.assign(target, volume);
    }
  },
};

const getters = {
  getVolumesForTenant(state) {
    return createFilterByTenantGetter(state.all);
  },
  volumesForActiveTeam(state, _getters, rootState) {
    return collectionForTeamId(state.all, rootState.activeTeamId);
  },
  volumesForFilterTenant(_state, getters, rootState, rootGetters) {
    return rootState.filterTenantId
      ? getters.getVolumesForTenant(rootGetters.filterTenant)
      : getters.volumesForActiveTeam;
  },
};

const actions = {
  async createVolume({ commit }, { tenant, volumeType, size, name }) {
    const payload = { tenant, volumeType, size, name };
    const response = await axios.post(apiRoutes.volumes, payload);
    const volume = response.data;
    commit("addVolume", volume);
    return volume;
  },
  async fetchVolume({ commit }, { volume }) {
    const uri = `${apiRoutes.volumes}${volume.tenant}/${volume.id}`;
    const response = await axios.get(uri);
    commit("updateVolume", response.data);
  },
  async getTeamVolumes({ commit, rootGetters }, { tenant } = {}) {
    commit("setLoading", true);
    const team = rootGetters.team;
    const response = await axios.get(apiRoutes.volumes, {
      params: { team: team.id, tenant: tenant?.id },
    });
    const volumes = response.data;
    commit("setVolumes", { volumes, team, tenant });
    commit("setLoading", false);
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
