<template>
  <span :aria-hidden="decorative" :class="containerClasses">
    <font-awesome-icon v-bind="$attrs" :size="faSize" />
  </span>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],
  props: {
    decorative: {
      type: Boolean,
      default: false,
    },
    left: {
      type: Boolean,
      required: false,
    },
    right: {
      type: Boolean,
      required: false,
    },
  },
  computed: {
    containerClasses() {
      return [
        "icon",
        this.sizeClass,
        this.textColorClass,
        {
          "is-left": this.left,
          "is-right": this.right,
        },
      ];
    },
    faSize() {
      const sizeMap = {
        "is-large": "lg",
      };
      return sizeMap[this.sizeClass];
    },
  },
};
</script>