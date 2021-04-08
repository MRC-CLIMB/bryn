<template>
  <div>
    <template v-if="allInvitations.length">
      <div
        v-for="(invitation, index) in allInvitations"
        :key="index"
        class="panel-block"
      >
        <span class="panel-icon">
          <font-awesome-icon :icon="['fas', 'envelope']" aria-hidden="true" />
        </span>
        <p class="is-flex-grow-1">
          {{ invitation.email }}
        </p>
        <base-button
          v-if="userIsAdmin"
          color="danger"
          size="small"
          rounded
          outlined
          @click="onDelete(invitation)"
          >Delete</base-button
        >
      </div>
    </template>

    <template v-else>
      <div class="panel-block"><p>No invitations pending</p></div>
    </template>

    <base-modal-delete
      v-if="confirmDeleteInvitation"
      verb="Delete"
      type="Invitation"
      :name="confirmDeleteInvitation.email"
      :processing="deleteProcessing"
      @close-modal="onCancelDelete"
      @confirm-delete="onConfirmDelete"
    />
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import { DELETE_INVITATION } from "@/store/action-types";
import { ALL_INVITATIONS, USER_IS_ADMIN } from "@/store/getter-types";

export default {
  // Composition
  inject: ["toast"],

  // Local state
  data() {
    return {
      confirmDeleteInvitation: null,
      deleteProcessing: false,
    };
  },

  computed: {
    ...mapGetters({
      allInvitations: ALL_INVITATIONS,
      userIsAdmin: USER_IS_ADMIN,
    }),
  },

  // Non-reactive
  methods: {
    ...mapActions({
      deleteInvitation: DELETE_INVITATION,
    }),
    onDelete(invitation) {
      this.confirmDeleteInvitation = invitation;
    },
    onCancelDelete() {
      this.confirmDeleteInvitation = null;
    },
    async onConfirmDelete() {
      if (this.deleteProcessing) {
        return;
      }
      const invitation = this.confirmDeleteInvitation;
      this.deleteProcessing = true;
      try {
        await this.deleteInvitation(invitation);
        this.toast(`Cancelled invitation: ${invitation.email}`);
      } catch (err) {
        this.toast.error(
          `Failed to remove invitation: ${
            err.response?.data.detail ?? "unexpected error"
          }`
        );
      } finally {
        this.confirmDeleteInvitation = null;
        this.deleteProcessing = false;
      }
    },
  },
};
</script>