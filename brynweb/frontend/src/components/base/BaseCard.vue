<template>
  <div class="card">
    <header v-if="hasHeader" class="card-header">
      <slot name="header"></slot>
    </header>
    <div class="card-content">
      <slot></slot>
    </div>
    <footer v-if="hasFooter" class="card-footer">
      <slot name="footer"></slot>
    </footer>
  </div>
</template>

<script>
export default {
  computed: {
    hasHeader() {
      return this.$slots.header !== undefined;
    },
    hasFooter() {
      return this.$slots.footer !== undefined;
    },
  },
};
</script>