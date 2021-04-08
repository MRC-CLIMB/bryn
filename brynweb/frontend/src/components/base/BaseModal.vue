<template>
  <div class="modal is-active">
    <div class="modal-background" @click="closeModal"></div>
    <div class="modal-content" :class="{ 'is-modal-wide': wide }">
      <slot></slot>
    </div>
    <button
      class="modal-close is-large"
      aria-label="close"
      @click="closeModal"
    ></button>
  </div>
</template>

<script>
export default {
  props: {
    wide: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    "close-modal": null,
  },
  methods: {
    closeModal() {
      this.$emit("close-modal");
    },
  },
};
</script>

<style scoped>
@media screen and (min-width: 769px) {
  .is-modal-wide {
    width: 800px;
  }
}
</style>