<template>
  <base-tabs toggle rounded>
    <li :class="{ 'is-active': filterTenantId == null }">
      <a @click="onTabClick">{{ allDescription }}</a>
    </li>
    <li
      v-for="tenant in tenants"
      :key="tenant.id"
      :class="{ 'is-active': tenant.id === filterTenantId }"
    >
      <a @click="onTabClick(tenant)">{{ getRegionNameForTenant(tenant) }}</a>
    </li>
  </base-tabs>
</template>

<script>
import { mapGetters, mapActions, mapState } from "vuex";
import { SET_FILTER_TENANT } from "@/store/action-types";
import { GET_REGION_NAME_FOR_TENANT, TENANTS } from "@/store/getter-types";

export default {
  props: {
    entityName: {
      type: String,
      required: false,
    },
  },

  computed: {
    ...mapState({
      filterTenantId: (state) => state.filterTenantId,
    }),
    ...mapGetters({
      getRegionNameForTenant: GET_REGION_NAME_FOR_TENANT,
      tenants: TENANTS,
    }),

    allDescription() {
      return this.entityName == null ? "All" : "All " + this.entityName;
    },
  },

  methods: {
    ...mapActions({
      setFilterTenant: SET_FILTER_TENANT,
    }),
    onTabClick(tenant = null) {
      this.setFilterTenant(tenant);
    },
  },
};
</script>