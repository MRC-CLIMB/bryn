<template>
  <div>
    <div class="columns">
      <div class="column is-12">
        <base-level>
          <template v-slot:left>
            <h2 class="title">Team Profile</h2>
          </template>
          <template v-slot:right>
            <base-level-item v-if="userIsAdmin">
              <base-button-create @click="showNewInvitationModal = true">
                New Invitation
              </base-button-create>
            </base-level-item>
          </template>
        </base-level>
      </div>
    </div>
    <div class="columns">
      <div class="column">
        <div class="box">
          <team-profile />
        </div>
      </div>
      <div class="column">
        <!-- Team members panel -->
        <team-members-panel :teamMembers="allTeamMembers" />

        <!-- Licencing -->
        <team-licence-panel />
      </div>
    </div>

    <team-new-invitation-modal
      v-if="showNewInvitationModal"
      @closeModal="showNewInvitationModal = false"
    />
  </div>
</template>

<script>
import TeamLicencePanel from "@/components/TeamLicencePanel";
import TeamMembersPanel from "@/components/TeamMembersPanel";
import TeamNewInvitationModal from "@/components/TeamNewInvitationModal";
import TeamProfile from "@/components/TeamProfile";

import { mapGetters } from "vuex";
import { ALL_TEAM_MEMBERS, TEAM, USER_IS_ADMIN } from "@/store/getter-types";

export default {
  components: {
    TeamLicencePanel,
    TeamMembersPanel,
    TeamNewInvitationModal,
    TeamProfile,
  },

  data() {
    return {
      showNewInvitationModal: false,
    };
  },

  computed: {
    ...mapGetters({
      allTeamMembers: ALL_TEAM_MEMBERS,
      team: TEAM,
      userIsAdmin: USER_IS_ADMIN,
    }),
  },
};
</script>

