<template>
  <base-button rounded color="danger" :size="size" outlined
    ><template v-slot:icon-before>
      <base-icon :size="size" :icon="['fas', 'trash-alt']" :decorative="true" />
    </template>
    <template v-slot:default><slot>Delete</slot></template>
  </base-button>
</template>

<script>
import bulmaSizeMixin from "@/mixins/bulmaSizeMixin";

export default {
  mixins: [bulmaSizeMixin],
};
</script>