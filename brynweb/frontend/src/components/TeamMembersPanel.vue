<template>
  <nav class="panel is-primary">
    <p class="panel-heading">Membership</p>
    <p class="panel-tabs">
      <a
        v-for="tab in tabs"
        :key="tab.name"
        :class="{ 'is-active': tab == currentTab }"
        @click="currentTab = tab"
        >{{ tab.name }}</a
      >
    </p>
    <keep-alive>
      <component :is="currentTab.component" />
    </keep-alive>
  </nav>
</template>

<script>
import TeamMembersPanelMembers from "@/components/TeamMembersPanelMembers";
import TeamMembersPanelInvitations from "@/components/TeamMembersPanelInvitations";

export default {
  components: {
    TeamMembersPanelMembers,
    TeamMembersPanelInvitations,
  },
  data() {
    return {
      currentTab: null,
      tabs: [
        { name: "Members", component: "team-members-panel-members" },
        { name: "Invitations", component: "team-members-panel-invitations" },
      ],
    };
  },
  beforeMount() {
    this.currentTab = this.tabs[0];
  },
};
</script>