<template>
  <article :class="classes">
    <div v-if="headed" class="message-header">
      <p>
        <slot name="header"></slot>
      </p>
      <button
        v-if="dismissable"
        @click="dismiss"
        class="delete"
        aria-label="delete"
      ></button>
    </div>
    <div class="message-body">
      <slot></slot>
    </div>
  </article>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],
  emits: {
    dismissed: null,
  },
  props: {
    dismissable: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    classes() {
      return ["message", this.colorClass, this.sizeClass];
    },
    headed() {
      return this.$slots.header !== undefined;
    },
  },
  methods: {
    dismiss() {
      this.$emit("dismissed");
    },
  },
};
</script>
