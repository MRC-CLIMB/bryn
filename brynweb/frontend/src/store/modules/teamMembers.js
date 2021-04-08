import { axios, getAPIRoute } from "@/api";
import { collectionForTeamId } from "@/utils/store";
import { DELETE_TEAM_MEMBER, FETCH_TEAM_MEMBERS } from "@/store/action-types";
import {
  ADMIN_TEAM_MEMBERS,
  ALL_TEAM_MEMBERS,
  GET_TEAM_MEMBER_BY_ID,
  TEAM,
} from "@/store/getter-types";
import {
  REMOVE_TEAM_MEMBER_BY_ID,
  SET_TEAM_MEMBERS,
} from "@/store/mutation-types";
import { createFindByIdGetter, updateTeamCollection } from "@/utils/store";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [SET_TEAM_MEMBERS](state, { members, team }) {
    updateTeamCollection(state.all, members, team);
  },
  [REMOVE_TEAM_MEMBER_BY_ID](state, id) {
    state.all.splice(
      state.all.findIndex((obj) => obj.id === id),
      1
    );
  },
};

const getters = {
  [ALL_TEAM_MEMBERS](state, _getters, rootState) {
    return collectionForTeamId(state.all, rootState.activeTeamId);
  },
  [ADMIN_TEAM_MEMBERS](_state, getters) {
    return getters[ALL_TEAM_MEMBERS].filter((member) => member.isAdmin);
  },
  [GET_TEAM_MEMBER_BY_ID](state) {
    return createFindByIdGetter(state.all);
  },
};

const actions = {
  async [FETCH_TEAM_MEMBERS]({ commit, rootState, rootGetters }) {
    const url = getAPIRoute("teamMembers", rootState.activeTeamId);
    const team = rootGetters[TEAM];
    const response = await axios.get(url);
    const members = response.data;
    commit(SET_TEAM_MEMBERS, { members, team });
  },
  async [DELETE_TEAM_MEMBER]({ commit }, teamMember) {
    /* Delete a team member */
    const url = `${getAPIRoute("teamMembers", teamMember.team)}${
      teamMember.id
    }`;
    await axios.delete(url);
    commit(REMOVE_TEAM_MEMBER_BY_ID, teamMember.id);
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
