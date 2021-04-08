<template>
  <div :class="classes">
    <slot></slot>
  </div>
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
  },
  computed: {
    classes() {
      return [
        "notification",
        this.colorClass,
        this.sizeClass,
        {
          "is-light": this.light,
        },
      ];
    },
  },
};
</script>