<template>
  <base-modal-split @close-modal="closeModal">
    <template v-slot:left>
      <h4 class="title is-4">Attach {{ volume.name }}</h4>
      <p>
        Attach
        <span class="has-text-weight-semibold is-family-monospace">{{
          volume.name
        }}</span>
        to an instance.
      </p>

      <base-form-validated
        :form="form"
        @fieldValidate="form.onFieldValidate"
        submitLabel="Attach Volume"
        :submitted="submitted"
        @submit="submitForm"
      />
    </template>

    <template v-slot:right>
      <h4 class="title is-4">Help with attachments</h4>
      <div v-html="guidanceHTML"></div>
    </template>
  </base-modal-split>
</template>

<script>
import useFormValidation from "@/composables/formValidation";
import { mapToFormOptions } from "@/composables/formValidation/utils";
import { isRequired } from "@/composables/formValidation/validators";

import marked from "marked";
import DOMPurify from "dompurify";
import guidanceMarkdown from "@/content/volumes/newVolumeGuidance.md";

import { mapActions, mapGetters } from "vuex";
import { ATTACH_VOLUME } from "@/store/action-types";
import {
  GET_INSTANCE_BY_ID,
  GET_INSTANCES_FOR_TENANT,
  GET_TENANT_BY_ID,
} from "@/store/getter-types";

export default {
  // Composition
  inject: ["toast"],

  // Interface
  props: {
    volume: {
      type: Object,
      required: true,
    },
  },

  emits: {
    "close-modal": null,
  },

  // Local state
  data() {
    return {
      guidanceHTML: DOMPurify.sanitize(marked(guidanceMarkdown)),
      form: useFormValidation({
        server: {
          label: "Server",
          element: "select",
          validators: [isRequired],
        },
      }),
      submitted: false,
    };
  },

  computed: {
    ...mapGetters({
      getInstanceById: GET_INSTANCE_BY_ID,
      getInstancesForTenant: GET_INSTANCES_FOR_TENANT,
      getTenantById: GET_TENANT_BY_ID,
    }),
    serverOptions() {
      /* Instances for tenant (not shelves) */
      const tenant = this.getTenantById(this.volume.tenant);
      const instances = this.getInstancesForTenant(tenant).filter(
        (instance) =>
          !["SHELVED", "SHELVED_OFFLOADED"].includes(instance.status)
      );
      return mapToFormOptions(instances);
    },
  },

  // Events
  mounted() {
    this.form.fields.server.options = this.serverOptions;
  },

  // Non-reactive
  methods: {
    ...mapActions({
      attachVolume: ATTACH_VOLUME,
    }),
    closeModal() {
      this.$emit("close-modal");
    },
    async submitForm() {
      this.form.validate();
      if (this.submitted || !this.form.valid) {
        return;
      }
      this.submitted = true;
      try {
        const server = this.getInstanceById(this.form.values.server);
        const volume = this.volume;
        await this.attachVolume({ volume, server });
        this.toast.success(
          `Volume '${volume.name}' attached to '${server.name}'`
        );
        this.closeModal();
      } catch (err) {
        if (err.response?.status === 400) {
          this.form.parseResponseError(err.response.data);
        } else {
          this.toast.error(
            `Failed to attach volume: ${
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