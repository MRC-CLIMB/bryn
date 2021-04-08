import { axios, getAPIRoute } from "@/api";
import {
  updateTeamCollection,
  createFindByIdGetter,
  createFilterByTenantGetter,
} from "@/utils/store";
import { FETCH_TENANT_FLAVORS } from "@/store/action-types";
import {
  GET_FLAVOR_BY_ID,
  GET_FLAVORS_FOR_TENANT,
  TEAM,
} from "@/store/getter-types";
import { SET_FLAVORS } from "@/store/mutation-types";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [SET_FLAVORS](state, { flavors, team, tenant }) {
    updateTeamCollection(state.all, flavors, team, tenant);
  },
};

const getters = {
  [GET_FLAVOR_BY_ID](state) {
    return createFindByIdGetter(state.all);
  },

  [GET_FLAVORS_FOR_TENANT](state) {
    return createFilterByTenantGetter(state.all);
  },
};

const actions = {
  async [FETCH_TENANT_FLAVORS]({ commit, rootGetters }, tenant) {
    const team = rootGetters[TEAM];
    const url = getAPIRoute("flavors", team.id, tenant.id);
    const response = await axios.get(url);
    const flavors = response.data;
    commit(SET_FLAVORS, { flavors, team, tenant });
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
