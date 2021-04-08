<template>
  <form @submit.prevent="$emit('submit')" novalidate>
    <base-form-field
      v-for="[name, field] in Object.entries(form.fields)"
      :key="name"
    >
      <base-form-validated-control
        :field="field"
        :name="name"
        :disabled="disabled"
        @input="onFieldEvent($event)"
        @blur="onFieldEvent($event)"
        @change="onFieldEvent($event)"
      />
    </base-form-field>

    <div v-if="form.nonFieldErrors?.length" class="content">
      <ul class="has-text-danger">
        <li v-for="err in form.nonFieldErrors" :key="err">{{ err.message }}</li>
      </ul>
    </div>

    <slot name="buttons"
      ><base-button-confirm
        type="submit"
        :disabled="disableSubmit"
        :loading="submitted"
        >{{ submitLabel }}</base-button-confirm
      ></slot
    >
  </form>
</template>

<script>
export default {
  props: {
    form: {
      type: Object,
      required: true,
    },
    requireInput: {
      type: Boolean,
      default: false,
    },
    submitLabel: {
      type: String,
      default: "Submit",
    },
    submitted: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },

  emits: ["submit", "fieldValidate"],

  computed: {
    disableSubmit() {
      if (this.disabled) return true;
      if (this.requireInput) return !this.form.enableSubmit || !this.form.dirty;
      return !this.form.enableSubmit;
    },
  },

  methods: {
    onFieldEvent($event) {
      this.$emit("fieldValidate", $event);
    },
  },
};
</script>