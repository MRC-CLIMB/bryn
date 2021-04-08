<template>
  <div class="modal is-active">
    <div class="modal-background" @click="closeModal"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">
          <slot name="header"></slot>
        </p>
        <button @click="closeModal" class="delete" aria-label="close"></button>
      </header>
      <div class="modal-card-body">
        <slot></slot>
      </div>
      <footer class="modal-card-foot">
        <slot name="footer"></slot>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
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
