<template>
  <base-form-validated
    :form="form"
    @fieldValidate="form.onFieldValidate"
    submitLabel="Update"
    @submit="onSubmit"
    :submitted="submitted"
    :disabled="!userIsAdmin"
    requireInput
  />
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { UPDATE_TEAM } from "@/store/action-types";
import { TEAM, USER_IS_ADMIN } from "@/store/getter-types";

import useFormValidation from "@/composables/formValidation";
import { isRequired } from "@/composables/formValidation/validators";

export default {
  // Composition
  inject: ["toast"],

  // Local state
  data() {
    return {
      form: useFormValidation({
        institution: {
          iconClasses: ["fas", "university"],
          validators: [isRequired],
        },
        department: {
          iconClasses: ["fas", "building"],
          validators: [isRequired],
        },
        phoneNumber: {
          label: "Phone",
          type: "tel",
          iconClasses: ["fas", "phone"],
          validators: [isRequired], // Rely on server side phone num validation
        },
      }),
      submitted: false,
    };
  },

  computed: {
    ...mapGetters({
      team: TEAM,
      userIsAdmin: USER_IS_ADMIN,
    }),
  },

  // Events
  watch: {
    team: {
      handler() {
        this.form.fields.institution.value = this.team.institution;
        this.form.fields.department.value = this.team.department;
        this.form.fields.phoneNumber.value = this.team.phoneNumber;
      },
      immediate: true,
    },
  },

  // Non-reactive
  methods: {
    ...mapActions({
      updateTeam: UPDATE_TEAM,
    }),
    async onSubmit() {
      this.form.validate();
      if (this.submitted || !this.form.valid) {
        return;
      }
      this.submitted = true;
      try {
        await this.updateTeam(this.form.values);
        this.toast.success("Team profile saved");
        this.form.resetValidation();
      } catch (err) {
        if (err.response?.status === 400) {
          this.form.parseResponseError(err.response.data);
        } else {
          this.toast.error(
            `Failed to update team: ${
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