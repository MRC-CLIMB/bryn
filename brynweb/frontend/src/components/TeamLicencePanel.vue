<template>
  <base-notification
    v-if="team.licenceIsValid && (!hideValid || isRenewable)"
    :color="isRenewable ? 'warning' : 'success'"
    class="has-text-centered"
  >
    <p>
      <strong
        >Your team licence is valid until {{ licenceExpiryFormatted }}</strong
      >
    </p>

    <template v-if="isRenewable">
      <base-button
        v-if="userIsAdmin"
        class="mt-5"
        color="white"
        rounded
        outlined
        @click="showLicenceAgreementModal = true"
        >Renew Licence</base-button
      >
      <p v-else>
        To retain access to compute resources, please ask your team's primary
        user to renew before this date.
      </p>
    </template>
  </base-notification>

  <base-notification
    v-if="!team.licenceIsValid"
    color="danger"
    class="has-text-centered"
  >
    <p><strong>Your team licence has expired.</strong></p>

    <template v-if="userIsAdmin">
      <p>Please renew your licence to regain access to compute resources.</p>

      <base-button
        class="mt-5"
        color="white"
        rounded
        outlined
        @click="showLicenceAgreementModal = true"
        >Renew Licence</base-button
      >
    </template>

    <template v-else>
      <p>
        To regain access to compute resources, please ask your team's primary
        user to renew your licence.
      </p>
    </template>
  </base-notification>

  <team-licence-agreement-modal
    v-if="showLicenceAgreementModal"
    @close-modal="showLicenceAgreementModal = false"
  />
</template>

<script>
import { mapGetters } from "vuex";
import { TEAM, USER_IS_ADMIN } from "@/store/getter-types";

import TeamLicenceAgreementModal from "@/components/TeamLicenceAgreementModal";

export default {
  components: {
    TeamLicenceAgreementModal,
  },

  props: {
    hideValid: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      showLicenceAgreementModal: false,
    };
  },

  computed: {
    ...mapGetters({
      team: TEAM,
      userIsAdmin: USER_IS_ADMIN,
    }),
    expiryDate() {
      return new Date(this.team.licenceExpiry);
    },
    isRenewable() {
      const earliestRenewalDate = new Date(this.expiryDate).setDate(
        this.expiryDate.getDate() - 30
      );
      return Date.now() >= earliestRenewalDate;
    },
    licenceExpiryFormatted() {
      return this.expiryDate.toUTCString();
    },
  },
};
</script>