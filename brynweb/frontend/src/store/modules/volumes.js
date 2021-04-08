import { axios, getAPIRoute } from "@/api";
import {
  updateTeamCollection,
  collectionForTeamId,
  createFindByIdGetter,
  createFilterByTenantGetter,
} from "@/utils/store";
import {
  ATTACH_VOLUME,
  CREATE_POLLING_TARGET,
  CREATE_VOLUME,
  DELETE_VOLUME,
  DETACH_VOLUME,
  FETCH_TENANT_VOLUMES,
  FETCH_VOLUME,
} from "../action-types";
import {
  ALL_VOLUMES,
  FILTER_TENANT,
  GET_ITEM_IS_POLLING,
  GET_MAX_VOLUME_SIZE_FOR_TENANT,
  GET_REGION_FOR_TENANT,
  GET_VOLUMES_FOR_TENANT,
  GET_VOLUME_BY_ID,
  GET_VOLUME_IS_POLLING,
  TEAM,
  TOTAL_TEAM_VOLUMES,
  TOTAL_TEAM_CAPACITY_GB,
  VOLUMES_FOR_FILTER_TENANT,
} from "../getter-types";
import {
  ADD_VOLUME,
  MODIFY_VOLUME,
  SET_VOLUMES,
  SET_VOLUMES_LOADING,
  REMOVE_VOLUME_BY_ID,
} from "../mutation-types";

const state = () => {
  return {
    all: [],
    loading: false,
  };
};

const mutations = {
  [ADD_VOLUME](state, volume) {
    state.all.unshift(volume);
  },
  [SET_VOLUMES](state, { volumes, team, tenant }) {
    /* Update all volumes for a team (fetch [and replace]) */
    updateTeamCollection(state.all, volumes, team, tenant);
  },
  [SET_VOLUMES_LOADING](state, loading) {
    state.loading = loading;
  },
  [MODIFY_VOLUME](state, volume) {
    /* Update an existing volume, maintaining the ref */
    const target = state.all.find((target) => target.id === volume.id);
    if (target) {
      Object.assign(target, volume);
    }
  },
  [REMOVE_VOLUME_BY_ID](state, id) {
    const index = state.all.findIndex((volume) => volume.id === id);
    if (index >= 0) {
      state.all.splice(index, 1);
    }
  },
};

const getters = {
  [ALL_VOLUMES](state, _getters, rootState) {
    return collectionForTeamId(state.all, rootState.activeTeamId);
  },
  [GET_MAX_VOLUME_SIZE_FOR_TENANT](_state, _getters, _rootState, rootGetters) {
    return (tenant) => {
      return rootGetters[GET_REGION_FOR_TENANT](tenant).settings
        .maxVolumeSizeGb;
    };
  },
  [GET_VOLUME_BY_ID](state) {
    return createFindByIdGetter(state.all);
  },
  [GET_VOLUME_IS_POLLING](state, _getters, _rootState, rootGetters) {
    return (volume) => rootGetters[GET_ITEM_IS_POLLING](state.all, volume);
  },
  [GET_VOLUMES_FOR_TENANT](state) {
    return createFilterByTenantGetter(state.all);
  },
  [TOTAL_TEAM_CAPACITY_GB](_state, getters) {
    const reducer = (acc, volume) => {
      if (volume.bootable) return acc;
      return acc + volume.size;
    };
    return getters[ALL_VOLUMES].filter((volume) => !volume.bootable).reduce(
      reducer,
      0
    );
  },
  [TOTAL_TEAM_VOLUMES](_state, getters) {
    return getters[ALL_VOLUMES].filter((volume) => !volume.bootable).length;
  },
  [VOLUMES_FOR_FILTER_TENANT](_state, getters, rootState, rootGetters) {
    return rootState.filterTenantId
      ? getters[GET_VOLUMES_FOR_TENANT](rootGetters[FILTER_TENANT])
      : getters[ALL_VOLUMES];
  },
};

const actions = {
  async [FETCH_VOLUME]({ commit }, volume) {
    /* Fetch and update an individual volume */
    const url = getAPIRoute("volumes", volume.team, volume.tenant) + volume.id;
    try {
      const response = await axios.get(url);
      volume = response.data;
      commit(MODIFY_VOLUME, volume);
      return volume;
    } catch (err) {
      if (err.response?.status === 404) {
        // Volume is gone; remove from local state
        commit(REMOVE_VOLUME_BY_ID, volume.id);
      }
      throw err;
    }
  },

  async [CREATE_VOLUME](
    { commit, dispatch, rootState, state },
    { tenant, volumeType, size, name }
  ) {
    const payload = { tenant, volumeType, size, name };
    const url = getAPIRoute("volumes", rootState.activeTeamId, tenant);
    const response = await axios.post(url, payload);
    const volume = response.data;
    commit(ADD_VOLUME, volume);
    dispatch(CREATE_POLLING_TARGET, {
      collection: state.all,
      item: volume,
      fetchAction: FETCH_VOLUME,
      targetStatuses: ["available", "in-use", "error"],
    });
    return volume;
  },

  async [DELETE_VOLUME]({ dispatch, state }, volume) {
    /* Delete a volume */
    const url = getAPIRoute("volumes", volume.team, volume.tenant) + volume.id;
    await axios.delete(url);
    dispatch(CREATE_POLLING_TARGET, {
      collection: state.all,
      item: volume,
      fetchAction: FETCH_VOLUME,
      targetStatuses: [], // gone,
    });
    // /* Takes a while to delete, but better user experience to just remove rather than show polling */
    // commit(REMOVE_VOLUME_BY_ID, volume.id);
  },

  async [ATTACH_VOLUME]({ dispatch, state }, { volume, server }) {
    const payload = { attachments: [{ serverId: server.id }] };
    const url = getAPIRoute("volumes", volume.team, volume.tenant) + volume.id;
    await axios.patch(url, payload);
    dispatch(CREATE_POLLING_TARGET, {
      collection: state.all,
      item: volume,
      fetchAction: FETCH_VOLUME,
      targetStatuses: ["in-use"],
    });
  },

  async [DETACH_VOLUME]({ dispatch, state }, volume) {
    const payload = { attachments: [] }; // Empty array
    const url = getAPIRoute("volumes", volume.team, volume.tenant) + volume.id;
    await axios.patch(url, payload);
    dispatch(CREATE_POLLING_TARGET, {
      collection: state.all,
      item: volume,
      fetchAction: FETCH_VOLUME,
      targetStatuses: ["available"],
    });
  },

  async [FETCH_TENANT_VOLUMES]({ commit, rootGetters }, tenant) {
    /* Fetch [and replace] all volumes for the active team */
    commit(SET_VOLUMES_LOADING, true);
    const team = rootGetters[TEAM];
    const url = getAPIRoute("volumes", team.id, tenant.id);
    const response = await axios.get(url);
    const volumes = response.data;
    commit(SET_VOLUMES, { volumes, team, tenant });
    commit(SET_VOLUMES_LOADING, false);
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
