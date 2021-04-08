<template>
  <div>
    <template v-if="!serviceAnnouncements.length">
      <h3 class="is-size-3 mb-5">Welcome back, {{ user.firstName }}</h3>
      <hr />
    </template>

    <team-licence-panel hideValid />

    <service-announcement
      v-for="announcement in serviceAnnouncements"
      :key="announcement.id"
      :announcement="announcement"
    />

    <h4 class="is-size-4 mb-4">Team resources</h4>
    <dashboard-team-tiles />

    <h4 class="is-size-4 mb-4">Service status</h4>
    <dashboard-service-status />

    <hr />

    <div v-if="newsAnnouncements.length">
      <h4 class="is-size-3 mb-4">Latest news</h4>

      <news-announcement
        v-for="announcement in newsAnnouncements"
        :key="announcement.id"
        :announcement="announcement"
      />
    </div>
  </div>
</template>

<script>
import DashboardServiceStatus from "@/components/DashboardServiceStatus.vue";
import DashboardTeamTiles from "@/components/DashboardTeamTiles.vue";
import NewsAnnouncement from "@/components/NewsAnnouncement";
import ServiceAnnouncement from "@/components/ServiceAnnouncement";
import TeamLicencePanel from "@/components/TeamLicencePanel";

import { mapGetters, mapState } from "vuex";
import {
  NEWS_ANNOUNCEMENTS,
  SERVICE_ANNOUNCEMENTS,
} from "@/store/getter-types";

export default {
  components: {
    DashboardServiceStatus,
    DashboardTeamTiles,
    NewsAnnouncement,
    ServiceAnnouncement,
    TeamLicencePanel,
  },

  computed: {
    ...mapState({
      user: (state) => state.user,
    }),
    ...mapGetters({
      newsAnnouncements: NEWS_ANNOUNCEMENTS,
      serviceAnnouncements: SERVICE_ANNOUNCEMENTS,
    }),
  },
};
</script>

<style lang="scss" scoped>
.announcements-column {
  border-left: 1px solid hsl(0, 0%, 90%);
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
}
</style>