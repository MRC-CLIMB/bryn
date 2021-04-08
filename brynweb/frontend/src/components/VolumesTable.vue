<template>
  <div class="table-container">
    <base-table fullwidth hoverable>
      <!-- Table header -->
      <template v-slot:head>
        <tr>
          <th>Name</th>
          <th class="is-hidden-touch">Type</th>
          <th class="is-hidden-mobile">Size</th>
          <th>Status</th>
          <th class="is-hidden-touch">Attached To</th>
          <th class="is-hidden-touch">Created</th>
          <th><!-- Action buttons --></th>
        </tr>
      </template>

      <!-- Table body -->
      <template v-slot:body>
        <tr v-for="(volume, index) in volumes" :key="index">
          <!-- Name & region -->
          <td>
            <span class="has-text-weight-semibold">{{ volume.name }}</span>
            <br />
            <span class="is-size-7">
              {{ getRegionNameForTenant(getTenantById(volume.tenant)) }}</span
            >
          </td>

          <!-- Type & Bootable -->
          <td class="is-hidden-touch">
            {{ volume.volumeType }}<br />
            <span v-if="volume.bootable" class="is-size-7">Bootable</span>
          </td>

          <td class="is-hidden-mobile">{{ formatSize(volume.size) }}</td>

          <!-- Status & polling spinner -->
          <td>
            <base-tag-control>
              <base-tag
                v-if="isNew(volume)"
                color="dark"
                rounded
                class="is-hidden-touch"
                >NEW</base-tag
              >
              <base-tag :color="statusColor(volume.status)" rounded light>
                {{ volume.status.toUpperCase() }}
                <base-icon
                  v-if="getVolumeIsPolling(volume)"
                  class="ml-1"
                  :icon="['fas', 'spinner']"
                  spin
                  :decorative="true"
                />
              </base-tag>
            </base-tag-control>
          </td>

          <!-- Attachments -->
          <td class="is-hidden-touch">
            <span
              v-for="attachment in formatAttachments(volume.attachments)"
              :key="attachment.id"
            >
              {{ attachment.attachedToName }}<br />
              <span class="is-family-monospace is-size-7">{{
                attachment.device
              }}</span>
            </span>
          </td>

          <!-- Created at -->
          <td class="is-size-6 is-hidden-touch">
            {{ timeSinceCreated(volume) }}
          </td>

          <td>
            <div class="buttons is-right">
              <!-- Attach button -->
              <base-button
                v-if="isAvailable(volume) && !volume.bootable"
                size="small"
                color="success"
                outlined
                rounded
                @click="$emit('attach-volume', volume)"
              >
                <template v-slot:default>Attach</template>
                <template v-slot:icon-before>
                  <base-icon :icon="['fas', 'link']" :decorative="true" />
                </template>
              </base-button>

              <!-- Detach button -->
              <base-button
                v-if="isInUse(volume) && !volume.bootable"
                size="small"
                outlined
                rounded
                @click="$emit('detach-volume', volume)"
              >
                <template v-slot:default>Detach</template>
                <template v-slot:icon-before>
                  <base-icon :icon="['fas', 'unlink']" :decorative="true" />
                </template>
              </base-button>

              <!-- Delete button -->
              <base-button-delete
                v-if="isAvailable(volume)"
                size="small"
                @click="$emit('delete-volume', volume)"
              />
            </div>
          </td>
        </tr>
      </template>
    </base-table>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import {
  GET_INSTANCE_BY_ID,
  GET_REGION_NAME_FOR_TENANT,
  GET_TENANT_BY_ID,
  GET_VOLUME_IS_POLLING,
} from "@/store/getter-types";

import { formatBytes, minutesSince } from "@/utils";
import { formatDistanceToNow } from "date-fns";

const volumePayloadValidator = ({ id, name }) => {
  if (id && name) {
    return true;
  }
  console.warn("Invalid event payload");
  return false;
};

export default {
  props: {
    volumes: {
      type: Array,
      required: true,
    },
  },

  emits: {
    "attach-volume": volumePayloadValidator,
    "delete-volume": volumePayloadValidator,
    "detach-volume": volumePayloadValidator,
  },

  computed: {
    ...mapGetters({
      getInstanceById: GET_INSTANCE_BY_ID,
      getRegionNameForTenant: GET_REGION_NAME_FOR_TENANT,
      getTenantById: GET_TENANT_BY_ID,
      getVolumeIsPolling: GET_VOLUME_IS_POLLING,
    }),
  },

  methods: {
    isNew(volume) {
      return minutesSince(volume.createdAt) < 3 && !this.isDeleting(volume);
    },
    isAvailable(volume) {
      return volume.status === "available";
    },
    isInUse(volume) {
      return volume.status === "in-use";
    },
    isDeleting(volume) {
      return volume.status === "deleting";
    },
    timeSinceCreated(volume) {
      return formatDistanceToNow(new Date(volume.createdAt)) + " ago";
    },
    formatAttachments(attachments) {
      return attachments.map((attachment) => {
        return {
          attachedToName: this.getInstanceById(attachment.serverId)?.name,
          device: attachment.device,
        };
      });
    },
    formatSize(size) {
      return formatBytes(size * Math.pow(1000, 3));
    },
    statusColor(status) {
      const colors = {
        "in-use": "success",
        available: "info",
      };
      const color = colors[status];
      return color;
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