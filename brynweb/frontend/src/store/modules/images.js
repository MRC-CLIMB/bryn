import { axios, getAPIRoute } from "@/api";
import {
  updateTeamCollection,
  createFindByIdGetter,
  createFilterByTenantGetter,
} from "@/utils/store";
import { FETCH_TENANT_IMAGES } from "@/store/action-types";
import {
  GET_IMAGE_BY_ID,
  GET_IMAGES_FOR_TENANT,
  TEAM,
} from "@/store/getter-types";
import { SET_IMAGES } from "@/store/mutation-types";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [SET_IMAGES](state, { images, team, tenant }) {
    updateTeamCollection(state.all, images, team, tenant);
  },
};

const getters = {
  [GET_IMAGE_BY_ID](state) {
    return createFindByIdGetter(state.all);
  },

  [GET_IMAGES_FOR_TENANT](state) {
    return createFilterByTenantGetter(state.all);
  },
};

const actions = {
  async [FETCH_TENANT_IMAGES]({ commit, rootGetters }, tenant) {
    const team = rootGetters[TEAM];
    const url = getAPIRoute("images", team.id, tenant.id);
    const response = await axios.get(url);
    const images = response.data;
    commit(SET_IMAGES, { images, team, tenant });
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
