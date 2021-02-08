<template>
  <div>
    <div class="block mb-3">
      <base-level>
        <template v-slot:left>
          <base-level-item>
            <tenant-filter-tabs
              entity-name="Servers"
              v-if="tenants.length > 1"
            />
            <h2 v-else class="title">Servers</h2>
          </base-level-item>
        </template>
        <template v-slot:right>
          <base-mini-loader :loading="loading" />
          <base-level-item v-if="hasShelved">
            <base-button rounded @click="showShelved = !showShelved"
              ><template v-slot:icon-before>
                <base-icon
                  :icon="['fas', showShelved ? 'eye-slash' : 'eye']"
                  :decorative="true"
                />
              </template>
              <template v-slot:default>{{
                showShelved ? "Hide shelved" : "Show shelved"
              }}</template>
            </base-button>
          </base-level-item>
          <base-level-item>
            <base-button-create @click="onNewServerClick">
              New server
            </base-button-create>
          </base-level-item>
        </template>
      </base-level>
    </div>

    <instances-table :instances="filteredInstances" />

    <div
      v-if="!(loading || instancesForFilterTenant.length)"
      class="content has-text-centered"
    >
      <h4 class="subtitle">{{ noItemsMessage }}</h4>
    </div>

    <instances-new-instance-modal
      v-if="showInstancesNewInstanceModal"
      @close-modal="showInstancesNewInstanceModal = false"
    />

    <key-pairs-new-key-pair-modal
      v-if="showKeyPairsNewKeyPairModal"
      submit-button-text="Add Key and Continue"
      @close-modal="onKeyPairModalClose"
    />
  </div>
</template>

<script>
import { mapGetters, mapState } from "vuex";

import InstancesNewInstanceModal from "@/components/InstancesNewInstanceModal";
import InstancesTable from "@/components/InstancesTable";
import KeyPairsNewKeyPairModal from "@/components/KeyPairsNewKeyPairModal";
import TenantFilterTabs from "@/components/TenantFilterTabs";

export default {
  // Template dependencies
  components: {
    InstancesTable,
    InstancesNewInstanceModal,
    KeyPairsNewKeyPairModal,
    TenantFilterTabs,
  },

  // Composition
  inject: ["toast"],

  // Local state
  data() {
    return {
      showShelved: false,
      showKeyPairsNewKeyPairModal: false,
      showInstancesNewInstanceModal: false,
    };
  },

  computed: {
    ...mapState({
      loading: (state) => state.instances.loading,
      keyPairs: (state) => state.keyPairs.all,
    }),
    ...mapGetters(["filterTenant", "getRegionNameForTenant", "tenants"]),
    ...mapGetters("instances", [
      "instancesForFilterTenant",
      "notShelvedForFilterTenant",
    ]),
    filteredInstances() {
      return this.showShelved
        ? this.instancesForFilterTenant
        : this.notShelvedForFilterTenant;
    },
    hasShelved() {
      return (
        this.instancesForFilterTenant.length !==
        this.notShelvedForFilterTenant.length
      );
    },
    noItemsMessage() {
      if (this.filterTenant != null) {
        return `You haven't created any servers at ${this.getRegionNameForTenant(
          this.filterTenant
        )} yet`;
      } else {
        return "You haven't created any servers yet";
      }
    },
  },

  // Events
  // Note, this wont work as a mixin due https://github.com/vuejs/vue-router-next/issues/454
  beforeRouteEnter(to, _from, next) {
    next((vm) => {
      const hasTenants = vm.$store.getters.tenants.length;
      const hasLicense = true; // TODO: after licensing
      if (!(hasTenants && hasLicense)) {
        // No tenants or no license, redirect to team admin view
        vm.$router.push({ name: "team", params: { teamId: to.params.teamId } });
      }
    });
  },

  // Non-reactive
  methods: {
    onNewServerClick() {
      // Handle no-keys for user
      if (this.keyPairs.length) {
        this.showInstancesNewInstanceModal = true;
      } else {
        this.showKeyPairsNewKeyPairModal = true;
      }
    },
    onKeyPairModalClose() {
      this.showKeyPairsNewKeyPairModal = false;
      if (this.keyPairs.length) {
        // User created a keypair, continue to server modal
        this.showInstancesNewInstanceModal = true;
      }
    },
  },
};
</script>