<template>
  <base-hero-full centered>
    <h2 class="subtitle">Sorry about this...</h2>
    <p>You don't seem to be a member of any team yet.</p>
    <p>
      Please contact:
      <a href="mailto:{{ adminEmail }}" class="has-text-white">{{
        adminEmail
      }}</a>
    </p>
  </base-hero-full>
</template>

<script>
import { mapState } from "vuex";

export default {
  computed: mapState({
    adminEmail: (state) => state.adminEmail,
  }),
};
</script>

<style scoped>
a {
  text-decoration: underline;
}
</style>