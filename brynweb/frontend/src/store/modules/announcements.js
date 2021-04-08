import { axios, getAPIRoute } from "@/api";
import { FETCH_ANNOUNCEMENTS } from "@/store/action-types";
import {
  NEWS_ANNOUNCEMENTS,
  SERVICE_ANNOUNCEMENTS,
} from "@/store/getter-types";
import { SET_ANNOUNCEMENTS } from "@/store/mutation-types";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [SET_ANNOUNCEMENTS](state, announcements) {
    state.all = announcements;
  },
};

const getters = {
  [NEWS_ANNOUNCEMENTS](state) {
    return state.all.filter((announcement) => announcement.category === "NS");
  },
  [SERVICE_ANNOUNCEMENTS](state) {
    return state.all.filter(
      (announcement) => announcement.category.charAt(0) === "S"
    );
  },
};

const actions = {
  async [FETCH_ANNOUNCEMENTS]({ commit }) {
    const url = getAPIRoute("announcements");
    const response = await axios.get(url);
    const announcements = response.data;
    commit(SET_ANNOUNCEMENTS, announcements);
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
