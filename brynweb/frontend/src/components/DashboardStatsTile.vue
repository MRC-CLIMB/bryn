<template>
  <div class="box has-text-centered">
    <base-icon
      color="info"
      size="large"
      :icon="iconClasses"
      :decorative="true"
    />
    <p class="is-size-6 has-text-grey">{{ description }}</p>
    <p class="is-size-4">{{ data }}</p>
  </div>
</template>

<script>
export default {
  props: {
    description: {
      type: String,
      required: true,
    },
    iconClasses: {
      type: Array,
      required: true,
    },
    data: {
      type: String,
      required: true,
    },
  },
};
</script>