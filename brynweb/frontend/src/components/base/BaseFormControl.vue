<template>
  <label v-if="label" class="label"
    >{{ label }}<span v-if="required" class="has-text-danger"> *</span></label
  >
  <div :class="controlClasses">
    <slot name="default"></slot>
    <slot name="iconLeft"></slot>
    <slot name="iconRight"></slot>
  </div>
  <p v-if="errors?.length" class="help is-danger">
    {{ errorMessage }}
  </p>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      required: false,
    },
    errors: {
      type: Array,
      required: false,
    },
    expanded: {
      type: Boolean,
      default: false,
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    errorMessage() {
      /* Derives a single error message from an expected array of ValidationError objects */
      return this.errors?.map((err) => err.message).join(", ");
    },
    controlClasses() {
      return [
        "control",
        {
          "is-expanded": this.expanded,
          "has-icons-left": this.$slots.iconLeft !== undefined,
          "has-icons-right": this.$slots.iconRight !== undefined,
        },
      ];
    },
  },
};
</script>