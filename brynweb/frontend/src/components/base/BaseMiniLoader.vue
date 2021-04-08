<template>
  <base-level-item class="mini-loader">
    <base-progress v-if="loading" color="info" indeterminate />
  </base-level-item>
</template>

<script>
export default {
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<style scoped>
.mini-loader {
  padding-right: 25px;
  width: 150px;
}
</style>