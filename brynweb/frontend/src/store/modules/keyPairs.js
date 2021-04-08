import { axios, getAPIRoute } from "@/api";
import { createFindByIdGetter } from "@/utils/store";
import {
  CREATE_KEY_PAIR,
  DELETE_KEY_PAIR,
  FETCH_KEY_PAIRS,
  FETCH_USER,
  SET_DEFAULT_KEY_PAIR,
  UPDATE_USER,
} from "@/store/action-types";
import {
  DEFAULT_KEY_PAIR,
  GET_KEY_PAIR_BY_ID,
  GET_KEY_PAIR_IS_DEFAULT,
} from "@/store/getter-types";
import {
  ADD_KEY_PAIR,
  SET_KEY_PAIRS,
  REMOVE_KEY_PAIR_BY_ID,
} from "@/store/mutation-types";

const state = () => {
  return {
    all: [],
  };
};

const mutations = {
  [ADD_KEY_PAIR](state, keyPair) {
    state.all.unshift(keyPair);
  },

  [REMOVE_KEY_PAIR_BY_ID](state, id) {
    state.all.splice(
      state.all.findIndex((obj) => obj.id === id),
      1
    );
  },

  [SET_KEY_PAIRS](state, keyPairs) {
    state.all = keyPairs;
  },
};

const getters = {
  [GET_KEY_PAIR_BY_ID](state) {
    return createFindByIdGetter(state.all);
  },

  [GET_KEY_PAIR_IS_DEFAULT](_state, _getters, rootState) {
    return ({ id }) => id === rootState.user.profile.defaultKeypair;
  },

  [DEFAULT_KEY_PAIR](_state, getters, rootState) {
    const defaultKeyPairId = rootState.user.profile.defaultKeypair;
    if (defaultKeyPairId == null) {
      return null;
    } else {
      return getters[GET_KEY_PAIR_BY_ID](defaultKeyPairId);
    }
  },
};

const actions = {
  async [FETCH_KEY_PAIRS]({ commit }) {
    const url = getAPIRoute("keyPairs");
    const response = await axios.get(url);
    const keyPairs = response.data;
    commit(SET_KEY_PAIRS, keyPairs);
  },

  async [CREATE_KEY_PAIR]({ commit, dispatch, state }, { name, publicKey }) {
    const payload = { name, publicKey };
    const url = getAPIRoute("keyPairs");
    const response = await axios.post(url, payload);
    const keypair = response.data;
    commit(ADD_KEY_PAIR, keypair);
    if (state.all.length == 1) {
      // First is auto-set to default, update user data on frontend
      dispatch(FETCH_USER, null, { root: true });
    }
    return keypair;
  },

  async [DELETE_KEY_PAIR]({ commit, dispatch, getters }, keyPair) {
    const url = `${getAPIRoute("keyPairs")}${keyPair.id}`;
    const wasDefault = getters[GET_KEY_PAIR_IS_DEFAULT](keyPair);
    await axios.delete(url);
    commit(REMOVE_KEY_PAIR_BY_ID, keyPair.id);
    if (wasDefault) {
      // User default will have changed
      dispatch(FETCH_USER, null, { root: true });
    }
  },

  async [SET_DEFAULT_KEY_PAIR]({ dispatch }, { id }) {
    const userData = { profile: { default_keypair: id } };
    await dispatch(UPDATE_USER, userData, { root: true });
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
