<template>
  <button @click="click" :class="classes" :disabled="disabled">
    <slot name="icon-before"></slot>

    <span v-if="hasText">
      <slot></slot>
    </span>

    <slot name="icon-after">
      <base-icon
        v-if="dropdown"
        size="small"
        :icon="['fas', 'angle-down']"
        :decorative="true"
      />
    </slot>
  </button>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],
  emits: {
    click: null,
  },
  props: {
    light: {
      type: Boolean,
      default: false,
    },
    rounded: {
      type: Boolean,
      default: false,
    },
    fullwidth: {
      type: Boolean,
      default: false,
    },
    outlined: {
      type: Boolean,
      default: false,
    },
    inverted: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    dropdown: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    classes() {
      return [
        "button",
        this.colorClass,
        this.sizeClass,
        {
          "is-light": this.light,
          "is-rounded": this.rounded,
          "is-fullwidth": this.fullwidth,
          "is-outlined": this.outlined,
          "is-inverted": this.inverted,
          "is-loading": this.loading,
        },
      ];
    },
    hasText() {
      return this.$slots.default !== undefined;
    },
  },
  methods: {
    click() {
      if (!this.disabled) {
        this.$emit("click");
      }
    },
  },
};
</script>
