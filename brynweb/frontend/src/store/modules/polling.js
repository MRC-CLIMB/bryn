import { CREATE_POLLING_TARGET, FETCH_POLLING_TARGETS } from "../action-types";
import { GET_ITEM_IS_POLLING } from "../getter-types";
import {
  SET_POLLING_SYMBOL,
  CLEAR_POLLING_SYMBOL,
  UPDATE_OR_CREATE_POLLING_TARGET,
  REMOVE_POLLING_TARGET,
} from "../mutation-types";

const state = () => {
  return {
    pollingSymbol: null, // Identifier for polling from setInterval()
    pollingTargets: [], // [{collection[], itemId, fetchAction, ["targetStatus", "alternativeStatus"]}]
  };
};

const getters = {
  [GET_ITEM_IS_POLLING](state) {
    return (collection, item) => {
      return state.pollingTargets.some(
        (target) =>
          target.collection === collection && target.itemId === item.id
      );
    };
  },
};

const mutations = {
  [SET_POLLING_SYMBOL](state, symbol) {
    state.pollingSymbol = symbol;
  },

  [CLEAR_POLLING_SYMBOL](state) {
    state.pollingSymbol = null;
  },

  [UPDATE_OR_CREATE_POLLING_TARGET](
    state,
    { collection, item, fetchAction, targetStatuses = [] }
  ) {
    /*
     * Update or create a polling target
     */
    const targets = state.pollingTargets;
    const existingTarget = targets.find(
      (target) => target.collection === collection && target.itemId == item.id
    );
    if (existingTarget) {
      /* Don't add duplicate targets; update status only */
      existingTarget.targetStatuses = targetStatuses;
    } else {
      targets.push({
        collection,
        itemId: item.id,
        fetchAction,
        targetStatuses,
      });
    }
  },

  [REMOVE_POLLING_TARGET](state, index) {
    state.pollingTargets.splice(index, 1);
  },
};

const actions = {
  async [CREATE_POLLING_TARGET](
    { state, commit, dispatch },
    { collection, item, fetchAction, targetStatuses = [] }
  ) {
    commit(UPDATE_OR_CREATE_POLLING_TARGET, {
      collection,
      item,
      fetchAction,
      targetStatuses,
    });
    dispatch(FETCH_POLLING_TARGETS); // First/immediate update
    if (!state.pollingSymbol) {
      /* Start polling */
      const pollingSymbol = setInterval(() => {
        dispatch(FETCH_POLLING_TARGETS);
      }, 5000);
      commit(SET_POLLING_SYMBOL, pollingSymbol);
    }
  },

  async [FETCH_POLLING_TARGETS]({ commit, dispatch, state }) {
    /* Fetch & update all polling targets */
    const results = await Promise.allSettled(
      state.pollingTargets.map((target) => {
        const item = target.collection.find(
          (item) => item.id === target.itemId
        );
        return dispatch(target.fetchAction, item);
      })
    );

    /* Handle results */
    results.forEach((result, index) => {
      if (result.status == "fulfilled") {
        /* Fulfilled case: check status against target */
        const target = state.pollingTargets[index];
        const newStatus = result.value.status;
        if (target.targetStatuses?.includes(newStatus)) {
          commit(REMOVE_POLLING_TARGET, index);
        }
      } else if (
        result.status == "rejected" &&
        result.reason.response?.status === 404
      ) {
        /* 404 case (e.g., item deleted) */
        commit(REMOVE_POLLING_TARGET, index);
      }
    });

    if (state.pollingTargets.length === 0) {
      /* Stop polling */
      clearInterval(state.pollingSymbol);
      commit(CLEAR_POLLING_SYMBOL);
    }
  },
};

export default {
  namespaced: false,
  state,
  getters,
  actions,
  mutations,
};
