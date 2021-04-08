<template>
  <router-view v-slot="{ Component, route }">
    <transition name="fade" mode="out-in">
      <keep-alive>
        <component :is="Component" :class="'tab-' + route.name" />
      </keep-alive>
    </transition>
  </router-view>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>