<template>
  <section
    class="hero is-primary is-primary-gradient is-fullheight-with-navbar"
  >
    <div class="hero-body">
      <div class="container">
        <div class="columns is-centered">
          <div
            class="column is-two-thirds-tablet is-half-desktop is-one-third-widescreen"
            :class="{ 'has-text-centered': centered }"
          >
            <slot></slot>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: {
    centered: {
      type: Boolean,
      default: false,
    },
  },
};
</script>