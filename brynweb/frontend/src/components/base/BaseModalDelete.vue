<template>
  <base-modal @close-modal="closeModal">
    <base-card class="content is-size-5 has-text-centered">
      <p>
        Are you sure you want to {{ verb.toLowerCase() }} this {{ type }}:<br />
        <span class="has-text-weight-semibold">{{ name }}</span
        >?
      </p>
      <base-buttons>
        <base-button fullwidth @click="closeModal" :disabled="processing"
          >Cancel</base-button
        >
        <base-button
          color="danger"
          fullwidth
          :loading="processing"
          @click="confirmDelete"
          >{{ verb }}</base-button
        >
      </base-buttons>
    </base-card>
  </base-modal>
</template>

<script>
export default {
  emits: {
    "confirm-delete": null,
    "close-modal": null,
  },
  props: {
    verb: {
      required: false,
      type: String,
      default: "remove",
    },
    type: {
      required: true,
      type: String,
      default: "record",
    },
    name: {
      required: false,
      type: String,
      default: "item",
    },
    processing: {
      required: false,
      type: Boolean,
      default: false,
    },
  },
  methods: {
    confirmDelete() {
      this.$emit("confirm-delete");
    },
    closeModal() {
      this.$emit("close-modal");
    },
  },
};
</script>