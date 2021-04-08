<template>
  <section class="hero is-primary the-header">
    <div class="hero-body">
      <header class="container">
        <base-level>
          <template v-slot:left>
            <base-level-item>
              <h1 class="is-size-3">
                {{ team.name }}
              </h1>
            </base-level-item>
          </template>
          <template v-if="teams.length > 1" v-slot:right>
            <base-level-item>
              <base-dropdown-list
                @itemSelected="onTeamSelect"
                title="Select team"
                :items="teams"
                :activeItem="team"
                hoverable
                right
                color="white"
              >
                <template v-slot:title>Switch team</template>
                <template v-slot:item="{ item: team }">
                  {{ team.name }}
                </template>
              </base-dropdown-list>
            </base-level-item>
          </template>
        </base-level>
      </header>
    </div>

    <the-header-tabs class="is-hidden-desktop" />
  </section>
</template>

<script>
import { mapGetters, mapState } from "vuex";
import { TEAM, USER_FULL_NAME } from "@/store/getter-types";

import TheHeaderTabs from "@/components/TheHeaderTabs";

export default {
  components: {
    TheHeaderTabs,
  },

  computed: {
    ...mapState({
      teams: (state) => state.teams,
    }),
    ...mapGetters({
      team: TEAM,
      userFullName: USER_FULL_NAME,
    }),
  },

  methods: {
    onTeamSelect(team) {
      this.$router.push({
        name: this.$route.name,
        params: { teamId: team.id },
      });
    },
  },
};
</script>

<style scoped>
.the-header {
  background: rgb(32, 60, 71);
  background: linear-gradient(
    0deg,
    rgba(32, 60, 71, 1) 0%,
    rgba(38, 70, 83, 1) 100%
  );
}

.the-header > .hero-body {
  -webkit-box-shadow: 0px 3px 5px 0px rgba(50, 50, 50, 0.17);
  -moz-box-shadow: 0px 3px 5px 0px rgba(50, 50, 50, 0.17);
  box-shadow: 0px 3px 5px 0px rgba(50, 50, 50, 0.17);
}
</style>