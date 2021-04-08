<template>
  <div :class="classes">
    <ul>
      <slot></slot>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    toggle: {
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
        "tabs",
        {
          "is-toggle": this.toggle,
          "is-toggle-rounded": this.toggle && this.rounded,
        },
      ];
    },
  },
};
</script>