<template>
  <div :class="wrapperClasses">
    <select
      :name="name"
      :value="modelValue"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ nullOptionLabel }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<script>
import bulmaColorMixin from "@/mixins/bulmaColorMixin";
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaColorMixin, bulmaSizeMixin],

  props: {
    modelValue: {
      type: undefined,
      required: false,
    },
    options: {
      type: Array,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    nullOptionLabel: {
      type: String,
      default: "Select an option",
    },
    invalid: {
      type: Boolean,
      default: false,
    },
    loading: {
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
  },

  emits: ["update:modelValue"],

  computed: {
    disabled() {
      return this.options.length === 0;
    },
    wrapperClasses() {
      return [
        "select",
        this.invalid ? "is-danger" : this.colorClass,
        this.sizeClass,
        {
          "is-rounded": this.rounded,
          "is-fullwidth": this.fullwidth,
          "is-loading": this.loading,
        },
      ];
    },
  },
};
</script>  