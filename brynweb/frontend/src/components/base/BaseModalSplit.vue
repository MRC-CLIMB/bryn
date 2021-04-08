<template>
  <base-modal wide>
    <base-card>
      <div class="columns is-variable is-5">
        <div class="column is-6 content">
          <slot name="left"></slot>
        </div>
        <div class="column is-6 content modal-right-col is-hidden-touch">
          <slot name="right"></slot>
        </div>
      </div>
    </base-card>
  </base-modal>
</template>

<style scoped>
.card {
  min-height: min(50vh, 500px);
}
.modal-right-col {
  border-left: 1px solid hsl(0, 0%, 96%);
  overflow-y: auto;
  position: absolute;
  top: 10px;
  bottom: 10px;
  right: 10px;
}
</style>