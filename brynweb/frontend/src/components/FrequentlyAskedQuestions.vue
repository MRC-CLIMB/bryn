<template>
  <base-message v-for="faq in faqs" :key="faq.title" color="light">
    <h4 class="subtitle has-text-weight-semibold">{{ faq.title }}</h4>
    <div class="content has-text-primary" v-html="faq.content"></div>
  </base-message>
</template>

<script>
export default {
  props: {
    faqs: {
      type: Array,
      required: true,
    },
  },
};
</script>
