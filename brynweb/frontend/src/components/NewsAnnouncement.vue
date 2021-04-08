<template>
  <base-message color="light">
    <h4 class="subtitle has-text-weight-semibold">{{ announcement.title }}</h4>
    <div class="content has-text-primary" v-html="announcement.content"></div>
    <span class="is-size-7 is-italic mt-1">{{ createdAt }}</span>
  </base-message>
</template>

<script>
import { formatRelative } from "date-fns";

export default {
  props: {
    announcement: {
      type: Object,
      required: true,
    },
  },

  computed: {
    createdAt() {
      return formatRelative(new Date(this.announcement.createdAt), new Date());
    },
  },
};
</script>