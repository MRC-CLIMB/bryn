<template>
  <div>
    <div
      v-for="(teamMember, index) in allTeamMembers"
      :key="index"
      class="panel-block"
    >
      <span class="panel-icon">
        <font-awesome-icon :icon="['fas', 'user']" aria-hidden="true" />
      </span>
      <p class="is-flex-grow-1">
        <strong
          >{{ teamMember.user.firstName }}
          {{ teamMember.user.lastName }}</strong
        >
        -
        <span class="is-italic is-size-6">{{ teamMember.user.email }}</span>
      </p>
      <base-tag v-if="teamMember.isAdmin" class="ml-3" color="dark" rounded
        >Admin</base-tag
      >
      <base-button
        v-if="!teamMember.isAdmin && userIsAdmin"
        color="danger"
        size="small"
        rounded
        outlined
        @click="onDelete(teamMember)"
        >Remove</base-button
      >
    </div>

    <base-modal-delete
      v-if="confirmDeleteTeamMember"
      verb="Remove"
      type="Team
  Member"
      :name="fullName(confirmDeleteTeamMember)"
      :processing="deleteProcessing"
      @close-modal="onCancelDelete"
      @confirm-delete="onConfirmDelete"
    />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { DELETE_TEAM_MEMBER } from "@/store/action-types";
import { ALL_TEAM_MEMBERS, USER_IS_ADMIN } from "@/store/getter-types";

export default {
  // Composition
  inject: ["toast"],

  // Local state
  data() {
    return {
      confirmDeleteTeamMember: null,
      deleteProcessing: false,
    };
  },

  computed: {
    ...mapGetters({
      allTeamMembers: ALL_TEAM_MEMBERS,
      userIsAdmin: USER_IS_ADMIN,
    }),
  },

  // Non-reactive
  methods: {
    ...mapActions({
      deleteTeamMember: DELETE_TEAM_MEMBER,
    }),
    fullName(teamMember) {
      return `${teamMember.user.firstName} ${teamMember.user.lastName}`;
    },
    onDelete(teamMember) {
      this.confirmDeleteTeamMember = teamMember;
    },
    onCancelDelete() {
      this.confirmDeleteTeamMember = null;
    },
    async onConfirmDelete() {
      if (this.deleteProcessing) {
        return;
      }
      const teamMember = this.confirmDeleteTeamMember;
      this.deleteProcessing = true;
      try {
        await this.deleteTeamMember(teamMember);
        this.toast(`Removed team member: ${this.fullName(teamMember)}`);
      } catch (err) {
        this.toast.error(
          `Failed to remove team member: ${
            err.response?.data.detail ?? "unexpected error"
          }`
        );
      } finally {
        this.confirmDeleteTeamMember = null;
        this.deleteProcessing = false;
      }
    },
  },
};
</script>