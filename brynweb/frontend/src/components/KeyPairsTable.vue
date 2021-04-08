<template>
  <base-table fullwidth hoverable>
    <template v-slot:head>
      <tr>
        <th>Name</th>
        <th class="is-hidden-touch">Fingerprint</th>
        <th><!-- Action buttons --></th>
      </tr>
    </template>
    <template v-slot:body>
      <tr v-for="(keyPair, index) in keyPairs" :key="index">
        <td>
          <span class="has-text-weight-semibold">{{ keyPair.name }}</span>
          <base-tag
            v-if="getKeyPairIsDefault(keyPair)"
            class="ml-3"
            color="info"
            rounded
            >Default</base-tag
          >
        </td>
        <td class="is-family-monospace is-hidden-touch">
          {{ keyPair.fingerprint }}
        </td>
        <td>
          <div class="buttons is-right">
            <base-button
              v-if="!getKeyPairIsDefault(keyPair)"
              color="info"
              outlined
              rounded
              size="small"
              @click="$emit('set-default-keypair', keyPair)"
            >
              Set default
            </base-button>
            <base-button
              rounded
              size="small"
              class="has-tooltip-left has-tooltip-multiline has-tooltip-text-left is-hidden-touch"
              :data-tooltip="keyPair.publicKey"
            >
              View Public Key
            </base-button>
            <base-button-delete
              size="small"
              @click="$emit('delete-keypair', keyPair)"
            />
          </div>
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script>
import { mapGetters } from "vuex";
import { GET_KEY_PAIR_IS_DEFAULT } from "@/store/getter-types";

export default {
  // Interface
  props: {
    keyPairs: {
      type: Array,
      required: true,
    },
  },

  emits: {
    "delete-keypair": ({ id, name }) => {
      if (id && name) {
        return true;
      }
      console.warn("Invalid delete-keypair event payload");
      return false;
    },
    "set-default-keypair": ({ id, name }) => {
      if (id && name) {
        return true;
      }
      console.warn("Invalid set-default-keypair event payload");
      return false;
    },
  },

  // Local state
  computed: mapGetters({
    getKeyPairIsDefault: GET_KEY_PAIR_IS_DEFAULT,
  }),
};
</script>

<style scoped>
[data-tooltip]:not(.is-loading).has-tooltip-multiline::before,
[data-tooltip]:not(.is-disabled).has-tooltip-multiline::before,
[data-tooltip]:not([disabled]).has-tooltip-multiline::before {
  overflow-wrap: anywhere;
  width: 25em;
  max-width: 25em;
}

td {
  vertical-align: middle;
}
</style>