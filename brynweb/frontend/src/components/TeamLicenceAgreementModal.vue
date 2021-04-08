<template>
  <base-modal wide @close-modal="onClose">
    <base-card>
      <div class="content is-size-5 has-text-centered">
        <h4 class="title is-4">Renew Licence Agreement</h4>
        <p>Please read the licence terms below and confirm your acceptance.</p>
        <hr />
        <div
          v-html="licenceTerms"
          class="box has-text-left"
          style="max-height: 300px; overflow-y: auto"
        ></div>
      </div>
      <base-button color="success" fullwidth @click="onSubmit"
        >Agree and Renew Licence</base-button
      >
    </base-card>
  </base-modal>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import { CREATE_LICENCE_ACCEPTANCE } from "@/store/action-types";
import { TEAM } from "@/store/getter-types";

export default {
  // Composition
  inject: ["toast"],

  // Interface
  emits: {
    "close-modal": null,
  },

  // Local state
  data() {
    return {
      submitted: false,
    };
  },

  computed: {
    ...mapGetters({
      team: TEAM,
    }),
    ...mapState({
      licenceTerms: (state) => state.licenceTerms,
    }),
  },

  // Non-reactive
  methods: {
    ...mapActions({
      createLicenceAcceptance: CREATE_LICENCE_ACCEPTANCE,
    }),
    onClose() {
      this.$emit("close-modal");
    },
    async onSubmit() {
      this.submitted = true;
      try {
        await this.createLicenceAcceptance();
        this.toast.success(`Licence renewed for ${this.team.name}`);
        this.onClose();
      } catch (err) {
        if (err.response?.status === 400) {
          this.form.parseResponseError(err.response.data);
        } else {
          this.toast.error(
            `Failed to renew licence: ${
              err.response?.data.detail ?? "unexpected error"
            }`
          );
        }
      } finally {
        this.submitted = false;
      }
    },
  },
};
</script>