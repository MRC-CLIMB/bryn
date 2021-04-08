<template>
  <base-table fullwidth hoverable>
    <template v-slot:head>
      <tr>
        <th>Name</th>
        <th class="is-hidden-touch">Flavor</th>
        <th>Status</th>
        <th class="is-hidden-mobile">Lease</th>
        <th><!-- Action buttons --></th>
      </tr>
    </template>
    <template v-slot:body>
      <instances-table-row
        v-for="instance in instances"
        :key="instance.uuid"
        :instance="instance"
        @assign-teammember="onAssignTeamMember"
      />
    </template>
  </base-table>

  <instances-assign-team-member-modal
    v-if="assignTeamMemberInstance"
    :instance="assignTeamMemberInstance"
    @close-modal="assignTeamMemberInstance = null"
  />
</template>

<script>
import InstancesTableRow from "@/components/InstancesTableRow";
import InstancesAssignTeamMemberModal from "@/components/InstancesAssignTeamMemberModal";

export default {
  components: {
    InstancesTableRow,
    InstancesAssignTeamMemberModal,
  },

  props: {
    instances: {
      type: Array,
      required: true,
    },
  },

  data() {
    return {
      assignTeamMemberInstance: false,
    };
  },

  methods: {
    onAssignTeamMember(instance) {
      this.assignTeamMemberInstance = instance;
    },
  },
};
</script>