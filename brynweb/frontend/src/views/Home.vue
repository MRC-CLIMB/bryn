<template>
  <base-hero-full v-if="teams.length" centered>
    <h2 class="subtitle">Initializing team admin console...</h2>
    <base-progress indeterminate color="success" />
  </base-hero-full>
  <no-teams v-else />
</template>

<script>
import { mapGetters, mapState } from "vuex";
import { DEFAULT_TEAM_ID } from "@/store/getter-types";

import NoTeams from "@/components/NoTeams";

export default {
  components: {
    NoTeams,
  },

  computed: {
    ...mapState({
      teams: (state) => state.teams,
    }),
    ...mapGetters({
      defaultTeamId: DEFAULT_TEAM_ID,
    }),
  },

  mounted() {
    if (this.teams.length) {
      this.$router.push({
        name: "teamHome",
        params: { teamId: this.defaultTeamId ?? this.teams[0].id },
      });
    }
  },
};
</script>