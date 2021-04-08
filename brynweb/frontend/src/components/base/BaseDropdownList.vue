<template>
  <base-dropdown :hoverable="hoverable" :right="right" :up="up">
    <template v-slot:trigger="{ toggle: toggleDropdown }">
      <base-button
        @click="toggleDropdown"
        rounded
        dropdown
        outlined
        :color="color"
        :size="size"
      >
        <slot name="title"></slot>
      </base-button>
    </template>
    <template v-slot="{ toggle: toggleDropdown }">
      <a
        v-for="item in items"
        :key="item"
        @click="
          toggleDropdown();
          selectItem(item);
        "
        class="dropdown-item"
        :class="{
          'is-active': item == activeItem,
          'has-text-weight-bold': item == activeItem,
        }"
      >
        <slot name="item" :item="item"></slot>
      </a>
    </template>
  </base-dropdown>
</template>

<script>
import bulmaDropdownMixin from "@/mixins/bulmaDropdownMixin";

export default {
  mixins: [bulmaDropdownMixin],
  props: {
    items: {
      type: Array,
      required: true,
    },
    activeItem: {
      type: Object,
      required: false,
    },
    color: {
      type: String,
      required: false,
      default: "primary",
    },
    size: {
      type: String,
      required: false,
      default: "normal",
    },
  },
  methods: {
    selectItem(item) {
      this.$emit("itemSelected", item);
    },
  },
  emits: {
    itemSelected: null,
  },
};
</script>