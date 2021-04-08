<template>
  <base-modal @close-modal="closeModal">
    <base-card class="content">
      <h4 class="title is-4 has-text-centered">
        Assign a user to server '{{ instance.name }}'
      </h4>
      <p>
        Assign a team member to be responsible for the lease of this server.
      </p>

      <p>
        Lease renewal notifications and reminders will be sent to the email
        address associated with this user.
      </p>

      <base-form-validated
        :form="form"
        @fieldValidate="form.onFieldValidate"
        submitLabel="Assign team member"
        :submitted="submitted"
        @submit="submitForm"
      />
    </base-card>
  </base-modal>
</template>

<script>
import useFormValidation from "@/composables/formValidation";
import { isRequired } from "@/composables/formValidation/validators";

import { mapActions, mapGetters } from "vuex";
import { UPDATE_INSTANCE_ASSIGNED_TEAM_MEMBER } from "@/store/action-types";
import { ALL_TEAM_MEMBERS, GET_TEAM_MEMBER_BY_ID } from "@/store/getter-types";

export default {
  // Composition
  inject: ["toast"],

  // Interface
  props: {
    instance: {
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
      form: useFormValidation({
        teamMember: {
          label: "Team Member",
          element: "select",
          validators: [isRequired],
          value: this.instance.leaseAssignedTeammember,
        },
      }),
      submitted: false,
    };
  },

  computed: {
    ...mapGetters({
      allTeamMembers: ALL_TEAM_MEMBERS,
      getTeamMemberById: GET_TEAM_MEMBER_BY_ID,
    }),
    teamMemberOptions() {
      return this.allTeamMembers.map((teamMember) => {
        return {
          value: teamMember.id,
          label: `${teamMember.user.firstName} ${teamMember.user.lastName}`,
        };
      });
    },
  },

  // Events
  mounted() {
    this.form.fields.teamMember.options = this.teamMemberOptions;
  },

  // Non-reactive
  methods: {
    ...mapActions({
      updateInstanceAssignedTeamMember: UPDATE_INSTANCE_ASSIGNED_TEAM_MEMBER,
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
        const teamMember = this.getTeamMemberById(this.form.values.teamMember);
        await this.updateInstanceAssignedTeamMember({
          instance: this.instance,
          teamMember,
        });
        this.toast.success(
          `${teamMember.user.firstName} ${teamMember.user.lastName} has been assigned to ${this.instance.name}`
        );
        this.closeModal();
      } catch (err) {
        console.log(err);
        if (err.response?.status === 400) {
          this.form.parseResponseError(err.response.data);
        } else {
          this.toast.error(
            `Failed to assign team member: ${
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