<template>
  <base-form-input-select
    v-if="field.element === 'select'"
    :modelValue="field.value"
    v-bind="selectedAttrs"
    @change="$emit('change', $event)"
  />
  <base-form-input
    v-else
    :modelValue="field.value"
    v-bind="field.element === 'textarea' ? sharedAttrs : inputAttrs"
    :element="field.element"
    @input="$emit('input', $event)"
    @blur="$emit('blur', $event)"
  />
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    field: {
      type: Object,
      required: false,
    },
  },

  emits: ["input", "change", "blur"],

  computed: {
    sharedAttrs() {
      // Applicable to all elements (input, textarea & select)
      return {
        name: this.field.name,
        invalid: this.field.invalid,
      };
    },
    inputAttrs() {
      // Input attributes
      return {
        ...this.sharedAttrs,
        type: this.field.type,
      };
    },
    selectedAttrs() {
      // Select attributes
      return {
        ...this.sharedAttrs,
        options: this.field.options,
        "null-option-label": `Select a ${this.field.label}`,
        fullwidth: true,
      };
    },
  },
};
</script>