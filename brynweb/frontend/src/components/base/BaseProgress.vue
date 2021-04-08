<template>
  <progress v-if="indeterminate" :class="classList"></progress>
  <progress v-else :value="value" :max="max" :class="classList">
    {{ value }}%
  </progress>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],
  props: {
    value: {
      type: Number,
      default: 0,
    },
    max: {
      type: Number,
      default: 100,
    },
    indeterminate: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    classList() {
      return ["progress", this.colorClass, this.sizeClass];
    },
  },
};
</script>