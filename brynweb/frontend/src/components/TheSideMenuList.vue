<template>
  <p class="menu-label">{{ label }}</p>
  <ul class="menu-list">
    <router-link
      v-for="route in routes"
      :key="route.path"
      :to="route.path"
      custom
      v-slot="{ href, navigate, isExactActive }"
    >
      <li>
        <a
          :class="{ 'is-active': isExactActive }"
          :href="href"
          @click="navigate"
          >{{ route.meta.displayName }}</a
        >
      </li>
    </router-link>
  </ul>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      required: true,
    },
    routes: {
      type: Array,
      required: true,
    },
  },
  computed: {
    currentRoute() {
      return this.$route;
    },
  },
};
</script>