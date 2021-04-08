<template>
  <span :class="classes">
    <slot></slot>
  </span>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],
  props: {
    light: {
      type: Boolean,
      default: false,
    },
    rounded: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    classes() {
      return [
        "tag",
        this.colorClass,
        this.sizeClass,
        {
          "is-light": this.light,
          "is-rounded": this.rounded,
        },
      ];
    },
  },
};
</script>