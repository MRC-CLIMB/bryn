<template>
  <tr class="is-size-6">
    <td>
      <span class="has-text-weight-semibold">{{ instance.name }}</span
      ><br />
      <span class="is-size-7">{{ regionName }}</span>
    </td>

    <td class="is-hidden-touch">
      <span class="has-text-weight-semibold">{{ flavorName }}</span
      ><br />
      <span v-if="flavor" class="is-size-7"
        >{{ flavor.vcpus }} vCPUs : {{ flavor.ram / 1024 }} GB RAM</span
      >
    </td>

    <td>
      <base-tag-control>
        <base-tag v-if="isNew" color="dark" rounded class="is-hidden-touch"
          >NEW</base-tag
        >
        <base-tag :color="statusColor" rounded light>
          {{ instance.status }}
          <base-icon
            v-if="isPolling"
            class="ml-1"
            :icon="['fas', 'spinner']"
            spin
            :decorative="true"
          />
        </base-tag>
      </base-tag-control>
      <span
        v-if="!isShelved"
        class="is-family-monospace is-size-7 is-hidden-mobile"
        >{{ instance.ip }}</span
      >
      <span
        v-else-if="tenant.unshelvingDisabled"
        class="is-size-7 has-text-danger is-hidden-mobile"
        >Unshelving temporarily disabled</span
      >
    </td>

    <td class="is-hidden-mobile">
      <template v-if="displayLease">
        <template v-if="leaseHasExpired">
          <base-tag color="danger has-text-weight-semibold">
            Lease expired</base-tag
          ><br />
        </template>

        <base-tag-control v-else-if="leaseExpiry">
          <base-tag color="dark" class="is-hidden-touch">Expires in</base-tag>
          <base-tag :color="leaseTagColor" class="has-text-weight-semibold">
            {{ timeUntilLeaseExpiry }}
          </base-tag>
        </base-tag-control>

        <template v-else>
          <base-tag color="success">Indefinite lease</base-tag><br />
        </template>

        <a v-if="leaseIsRenewable" class="is-size-7" @click="onRenewClick"
          >Renew lease</a
        >
        <span v-else class="is-size-7 is-hidden-mobile"
          >Assigned user:
          <a v-if="userIsAdmin" @click="$emit('assign-teammember', instance)">{{
            leaseTeamMemberName
          }}</a>
          <template v-else>{{ leaseTeamMemberName }}</template>
        </span>
      </template>
    </td>

    <td class="actions-cell">
      <base-dropdown-list
        v-if="!isPolling"
        @itemSelected="onActionClick"
        title="Actions"
        :items="stateTransitionActions"
        right
        size="small"
      >
        <template v-slot:title
          ><span class="is-hidden-mobile">Actions</span></template
        >
        <template v-slot:item="{ item: action }">
          <span :class="`has-text-weight-semibold has-text-${action.color}`">{{
            action.verb
          }}</span>
        </template>
      </base-dropdown-list>
    </td>

    <!-- Confirm action modal -->
    <base-modal-delete
      v-if="confirmAction"
      :verb="confirmAction.verb"
      type="server"
      :name="instance.name"
      :processing="actionProcessing"
      @close-modal="onCancelAction"
      @confirm-delete="onConfirmAction"
    />
  </tr>
</template>

<script>
import { minutesSince } from "@/utils";
import { formatDistanceToNow } from "date-fns";

import { mapActions, mapGetters } from "vuex";
import {
  DELETE_INSTANCE,
  RENEW_INSTANCE_LEASE,
  TRANSITION_INSTANCE,
} from "@/store/action-types";
import {
  GET_FLAVOR_BY_ID,
  GET_INSTANCE_IS_POLLING,
  GET_REGION_NAME_FOR_TENANT,
  GET_TEAM_MEMBER_BY_ID,
  GET_TENANT_BY_ID,
  USER_IS_ADMIN,
} from "@/store/getter-types";

const statusColorMap = {
  ACTIVE: "success",
  SHUTDOWN: "info",
};

/*
 * State transitions
 * Top level is current status, 1st level is target status
 */
const stateTransitions = {
  ACTIVE: [
    {
      targetStatus: "ACTIVE",
      verb: "Reboot",
      presentParticiple: "Rebooting",
      color: "primary",
      confirm: true,
    },
    {
      targetStatus: "SHUTOFF",
      verb: "Shutdown",
      presentParticiple: "Stopping",
      color: "primary",
      confirm: true,
    },
    {
      targetStatus: "SHELVED",
      verb: "Shelve",
      presentParticiple: "Shelving",
      color: "danger",
      confirm: true,
    },
  ],
  SHUTOFF: [
    {
      targetStatus: "ACTIVE",
      verb: "Start",
      presentParticiple: "Starting",
      color: "success",
      confirm: false,
    },
    {
      targetStatus: "SHELVED",
      verb: "Shelve",
      presentParticiple: "Shelving",
      color: "danger",
      confirm: true,
    },
  ],
  SHELVED: [
    {
      targetStatus: "ACTIVE",
      verb: "Unshelve",
      presentParticiple: "Unshelving",
      color: "success",
      confirm: false,
    },
  ],
  SHELVED_OFFLOADED: [
    {
      targetStatus: "ACTIVE",
      verb: "Unshelve",
      presentParticiple: "Unshelving",
      color: "success",
      confirm: false,
    },
    {
      targetStatus: "DELETED",
      verb: "Delete",
      presentParticiple: "Deleting",
      color: "danger",
      confirm: true,
    },
  ],
};

export default {
  // Composition
  inject: ["toast"],

  // Interface
  props: {
    instance: {
      type: Object,
      required: true,
    },
  },

  emits: {
    "assign-teammember": ({ id, leaseAssignedTeammember }) => {
      if (id && leaseAssignedTeammember) {
        return true;
      }
      console.warn("Invalid assign-teammember event payload");
      return false;
    },
  },

  // Local state
  data() {
    return {
      confirmAction: null,
      actionProcessing: false,
    };
  },

  computed: {
    ...mapGetters({
      getFlavorById: GET_FLAVOR_BY_ID,
      getInstanceIsPolling: GET_INSTANCE_IS_POLLING,
      getRegionNameForTenant: GET_REGION_NAME_FOR_TENANT,
      getTeamMemberById: GET_TEAM_MEMBER_BY_ID,
      getTenantById: GET_TENANT_BY_ID,
      userIsAdmin: USER_IS_ADMIN,
    }),

    isNew() {
      return minutesSince(this.instance.created) < 3;
    },

    isShelved() {
      return this.instance.status.includes("SHELVED");
    },

    isPolling() {
      return this.getInstanceIsPolling(this.instance);
    },

    tenant() {
      return this.getTenantById(this.instance.tenant);
    },

    regionName() {
      return this.getRegionNameForTenant(this.tenant);
    },

    flavor() {
      return this.getFlavorById(this.instance.flavor);
    },

    flavorName() {
      return this.flavor ? this.flavor.name : "[legacy flavor]";
    },

    timeUntilLeaseExpiry() {
      return formatDistanceToNow(new Date(this.instance.leaseExpiry));
    },

    displayLease() {
      return !["SHELVED", "SHELVED_OFFLOADED"].includes(this.instance.status);
    },

    leaseExpiry() {
      if (this.instance.leaseExpiry == null) {
        return null;
      } else {
        return new Date(this.instance.leaseExpiry);
      }
    },

    leaseIsRenewable() {
      if (
        this.leaseExpiry == null ||
        ["SHELVED", "SHELVED_OFFLOADED"].includes(this.instance.status)
      )
        return false;

      const earliestRenewalDate = new Date(this.leaseExpiry).setDate(
        this.leaseExpiry.getDate() - 7
      );
      return Date.now() >= earliestRenewalDate;
    },

    leaseHasExpired() {
      return this.leaseExpiry != null && Date.now() >= this.leaseExpiry;
    },

    leaseTagColor() {
      if (this.leaseIsRenewable) {
        return "warning";
      } else {
        return "success";
      }
    },

    leaseTeamMember() {
      return this.getTeamMemberById(this.instance.leaseAssignedTeammember);
    },

    leaseTeamMemberName() {
      return `${this.leaseTeamMember.user.firstName} ${this.leaseTeamMember.user.lastName}`;
    },

    statusColor() {
      if (this.isPolling) return "warning";
      return statusColorMap[this.instance.status] ?? "light";
    },

    stateTransitionActions() {
      const transitions = stateTransitions[this.instance.status];
      if (this.isShelved && this.tenant.unshelvingDisabled) {
        return transitions.filter((transition) => {
          return transition.verb.toLowerCase() !== "unshelve";
        });
      } else {
        return transitions;
      }
    },
  },

  // Non-reactive
  methods: {
    ...mapActions({
      deleteInstance: DELETE_INSTANCE,
      renewInstanceLease: RENEW_INSTANCE_LEASE,
      transitionInstance: TRANSITION_INSTANCE,
    }),

    async onRenewClick() {
      try {
        await this.renewInstanceLease(this.instance);
        this.toast.success(
          `The lease for server '${this.instance.name}' has been renewed`
        );
      } catch (err) {
        this.toast.error(
          `Failed to renew lease for '${this.instance.name}': ${
            err.response?.data.detail ?? "unexpected error"
          }`
        );
      } finally {
        this.actionProcessing = false;
      }
    },

    async onActionClick(action) {
      if (action.confirm) {
        this.confirmAction = action;
      } else {
        this.performAction(action);
      }
    },

    onCancelAction() {
      this.confirmAction = null;
    },

    async onConfirmAction() {
      await this.performAction(this.confirmAction);
      this.confirmAction = null;
    },

    async performAction(action) {
      if (this.actionProcessing) {
        return;
      }
      this.actionProcessing = true;
      try {
        if (action.targetStatus === "DELETED") {
          await this.deleteInstance(this.instance);
        } else {
          await this.transitionInstance({
            instance: this.instance,
            status: action.targetStatus,
          });
        }
        const toastMsg = `${action.presentParticiple} ${this.instance.name}`;
        this.toast(toastMsg);
      } catch (err) {
        this.toast.error(
          `Failed to ${action.verb} ${this.instance.name}: ${
            err.response?.data.detail ?? "unexpected error"
          }`
        );
      } finally {
        this.actionProcessing = false;
      }
    },
  },
};
</script>

<style scoped>
td {
  vertical-align: middle;
}

.actions-cell {
  text-align: right;
}
</style>