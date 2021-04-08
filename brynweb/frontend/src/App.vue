<template>
  <router-view />
</template>

<script>
import { useToast, TYPE } from "vue-toastification";
import { axios, apiRoutes } from "@/api";
import { mapActions } from "vuex";
import { INIT_STORE } from "@/store/action-types";

export default {
  // Composition
  provide() {
    return {
      toast: this.toast, // Global toast interface
    };
  },

  // Composition API
  setup() {
    const toast = useToast();
    return { toast };
  },

  // Local state
  computed: mapActions({
    initStore: INIT_STORE,
  }),

  // Events
  async beforeMount() {
    try {
      await this.initStore(); // Initialises global & user data (non-team sepecifc)
    } catch (err) {
      this.toast.error(
        `Failed to initialise team admin console: ${
          err.response?.data.detail ?? err
        }`
      );
    }
  },

  async mounted() {
    /* Creat toasts for any Django messages */
    const levelTagMap = {
      "is-danger": TYPE.ERROR,
      "is-success": TYPE.SUCCESS,
      "is-warning": TYPE.WARNING,
      "is-info": TYPE.INFO,
    };
    const response = await axios.get(apiRoutes.messages);
    const messages = response.data;
    if (messages.length) {
      messages.forEach((message) => {
        this.toast(message.message, { type: levelTagMap[message.levelTag] });
      });
    }
  },
};
</script>

<style>
.navbar.is-fixed-top {
  border-bottom: 1px solid #457b9dff;
}
</style>