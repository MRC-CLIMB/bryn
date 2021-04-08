<template>
  <footer class="footer">
    <div class="columns">
      <div class="column is-3 is-offset-1">
        <p class="is-size-7">
          COPYRIGHT © {{ new Date().getFullYear() }} -
          <a href="https://www.climb.ac.uk/" class="has-text-white"
            >CLIMB-BIG-DATA</a
          >.<br />ALL RIGHTS RESERVED.
        </p>

        <p class="is-size-7 mt-2">
          <a
            href="http://www.climb.ac.uk/terms-conditions/"
            class="has-text-white"
            >TERMS &amp; CONDITIONS</a
          >
          |
          <a
            href="http://www.climb.ac.uk/privacy-cookie-policy/"
            class="has-text-white"
            >PRIVACY POLICY</a
          >
        </p>
      </div>
      <div class="column is-7 is-hidden-touch">
        <base-level>
          <base-level-item
            ><img
              class="footer-logo-image"
              src="@/assets/images/footer-su-logo.png"
              alt="Swansea University logo"
          /></base-level-item>
          <base-level-item
            ><img
              class="footer-logo-image"
              src="@/assets/images/footer-warwick-logo.png"
              alt="University of Warwick logo"
          /></base-level-item>
          <base-level-item
            ><img
              class="footer-logo-image"
              src="@/assets/images/footer-cardiff-logo.png"
              alt="Cardiff University logo"
          /></base-level-item>
          <base-level-item
            ><img
              class="footer-logo-image"
              src="@/assets/images/footer-quadram-logo.png"
              alt="Quadram Institute logo"
          /></base-level-item>
          <base-level-item
            ><img
              class="footer-logo-image"
              src="@/assets/images/footer-birmingham-logo.png"
              alt="University of Birmingham logo"
          /></base-level-item>
        </base-level>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer-logo-image {
  max-width: 150px;
  max-height: 60px;
}
</style>