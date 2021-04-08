<template>
  <base-modal-split @close-modal="closeModal">
    <template v-slot:left>
      <h4 class="title is-4">Create a New Volume</h4>
      <p>Create a new volume, which can be attached to your instances.</p>

      <base-form-validated
        :form="form"
        @fieldValidate="form.onFieldValidate"
        submitLabel="Create Volume"
        :submitted="submitted"
        @submit="submitForm"
      />
    </template>
    <template v-slot:right>
      <h4 class="title is-4">Help with Volumes</h4>
      <base-message color="danger"
        ><strong>Important!</strong><br />As per the user agreement, we cannot
        guarantee the integrity or availability of your data. It is essential
        that you backup your data elsewhere.</base-message
      >
      <div v-html="guidanceHTML"></div>
    </template>
  </base-modal-split>
</template>

<script>
import useFormValidation from "@/composables/formValidation";
import {
  isAlphaNumHyphensOnly,
  isRequired,
  ValidationError,
} from "@/composables/formValidation/validators";

import { formatBytes } from "@/utils";

import marked from "marked";
import DOMPurify from "dompurify";
import guidanceMarkdown from "@/content/volumes/newVolumeGuidance.md";

import { mapState, mapActions, mapGetters } from "vuex";
import { CREATE_VOLUME } from "@/store/action-types";
import {
  DEFAULT_TENANT,
  GET_MAX_VOLUME_SIZE_FOR_TENANT,
  GET_REGION_NAME_FOR_TENANT,
  GET_TENANT_BY_ID,
  GET_VOLUMES_FOR_TENANT,
  TENANTS,
} from "@/store/getter-types";

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
      guidanceHTML: DOMPurify.sanitize(marked(guidanceMarkdown)),
      form: useFormValidation({
        tenant: {
          label: "Region",
          element: "select",
          iconClasses: ["fas", "globe-europe"],
          validators: [isRequired],
        },
        size: {
          label: "Size",
          element: "select",
          value: "250",
          iconClasses: ["fas", "save"],
          validators: [isRequired],
        },
        name: {
          label: "Name",
          iconClasses: ["fas", "tag"],
          validators: [isRequired, isAlphaNumHyphensOnly, this.isUniqueName],
        },
      }),
      submitted: false,
    };
  },

  computed: {
    ...mapState({
      filterTenantId: (state) => state.filterTenantId,
    }),
    ...mapGetters({
      defaultTenant: DEFAULT_TENANT,
      getMaxVolumeSizeForTenant: GET_MAX_VOLUME_SIZE_FOR_TENANT,
      getRegionNameForTenant: GET_REGION_NAME_FOR_TENANT,
      getTenantById: GET_TENANT_BY_ID,
      getVolumesForTenant: GET_VOLUMES_FOR_TENANT,
      tenants: TENANTS,
    }),

    selectedTenant() {
      return this.form.fields.tenant.value
        ? this.getTenantById(this.form.fields.tenant.value)
        : null;
    },

    sizeOptions() {
      const allSizes = [250, 500, 1000, 2000, 5000, 10000, 20000];
      const maxForTenant = this.getMaxVolumeSizeForTenant(this.selectedTenant);
      const tenantSizes = allSizes.filter((size) => size <= maxForTenant);
      return tenantSizes.map((size) => {
        return {
          value: size,
          label: formatBytes(size * Math.pow(1000, 3)),
        };
      });
    },

    tenantOptions() {
      return this.tenants.map((tenant) => {
        return {
          value: tenant.id,
          label: `${this.getRegionNameForTenant(tenant)}${
            tenant === this.defaultTenant ? " (default)" : ""
          }`,
        };
      });
    },

    invalidNames() {
      return this.selectedTenant
        ? this.getVolumesForTenant(this.selectedTenant).map(
            (volume) => volume.name
          )
        : [];
    },
  },

  // Events
  watch: {
    selectedTenant: {
      handler() {
        if (this.selectedTenant != null) {
          this.form.fields.size.options = this.sizeOptions;
        }
      },
      immediate: true,
    },
  },

  mounted() {
    this.form.fields.tenant.options = this.tenantOptions;
    if (this.filterTenantId) {
      this.form.fields.tenant.value = this.filterTenantId;
    } else if (this.tenants.length === 1) {
      this.form.fields.tenant.value = this.tenants[0].id;
    } else if (this.defaultTenant) {
      this.form.fields.tenant.value = this.defaultTenant.id;
    }
  },

  // Non-reactive
  methods: {
    ...mapActions({
      createVolume: CREATE_VOLUME,
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
        const volume = await this.createVolume(this.form.values);
        this.toast.success(`New volume created: ${volume.name}`);
        this.closeModal();
      } catch (err) {
        if (err.response?.status === 400) {
          this.form.parseResponseError(err.response.data);
        } else {
          this.toast.error(
            `Failed to create volume: ${
              err.response?.data.detail ?? "unexpected error"
            }`
          );
        }
      } finally {
        this.submitted = false;
      }
    },

    isUniqueName(value) {
      if (!value || !this.invalidNames.includes(value)) {
        return true;
      }
      throw new ValidationError("A unique name is required");
    },
  },
};
</script>