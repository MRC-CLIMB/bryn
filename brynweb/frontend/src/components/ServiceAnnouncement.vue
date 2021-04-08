<template>
  <base-message :color="color" light>
    <div class="content">
      <strong>{{ announcement.title }}</strong>
      <div class="mt-2" v-html="announcement.content"></div>
      <span class="is-size-7 is-italic mt-1"
        >Last update: {{ lastUpdated }}</span
      >
    </div>
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
    color() {
      const categoryColorMap = {
        SE: "danger",
        SR: "success",
        SI: "info",
      };
      return categoryColorMap[this.announcement.category];
    },

    lastUpdated() {
      return formatRelative(new Date(this.announcement.updatedAt), new Date());
    },
  },
};
</script>