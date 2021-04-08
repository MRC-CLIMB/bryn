<template>
  <tr>
    <td>
      <span>{{ region?.description?.replace("University of ", "") }}</span
      ><br />
      <span v-if="region.disabled" class="is-size-7 has-text-danger"
        >Offline</span
      >
      <span v-else class="is-size-7 has-text-success">Available</span>
    </td>
    <td class="is-hidden-mobile">
      <base-icon
        v-if="region.newInstancesDisabled"
        color="danger"
        size="large"
        :icon="['fas', 'times-circle']"
      />
      <base-icon
        v-else
        color="success"
        size="large"
        :icon="['fas', 'check-circle']"
      />
    </td>
    <td>{{ stats.runningVms }}</td>
    <td>
      <p class="is-size-7 has-text-centered is-hidden-touch">
        {{ stats.vcpusUsed }} / {{ stats.vcpus }}
      </p>
      <base-progress :value="vcpusPercent" :max="100" color="info" />
    </td>
    <td>
      <p class="is-size-7 has-text-centered is-hidden-touch">
        {{ MBtoTB(stats.memoryMbUsed) }} / {{ MBtoTB(stats.memoryMb) }} TB
      </p>
      <base-progress :value="memoryPercent" :max="100" color="info" />
    </td>
  </tr>
</template>

<script>
import { mapGetters } from "vuex";
import { GET_REGION_BY_ID } from "@/store/getter-types";

export default {
  props: {
    stats: {
      type: Object,
      required: true,
    },
  },

  computed: {
    ...mapGetters({
      getRegionById: GET_REGION_BY_ID,
    }),
    region() {
      return this.getRegionById(this.stats.region);
    },
    localGbPercent() {
      return Math.round((this.stats.localGbUsed / this.stats.localGb) * 100);
    },
    memoryPercent() {
      return Math.round((this.stats.memoryMbUsed / this.stats.memoryMb) * 100);
    },
    vcpusPercent() {
      return Math.round((this.stats.vcpusUsed / this.stats.vcpus) * 100);
    },
  },

  methods: {
    MBtoTB(mb) {
      return (mb / Math.pow(1000, 2)).toFixed(1);
    },
    GBtoPB(gb) {
      return (gb / Math.pow(1000, 2)).toFixed(1);
    },
  },
};
</script>

<style scoped>
td {
  vertical-align: middle;
}
</style>