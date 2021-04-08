<template>
  <div class="level">
    <slot name="default"></slot>
    <div class="level-left">
      <slot name="left"></slot>
    </div>
    <div class="level-right">
      <slot name="right"></slot>
    </div>
  </div>
</template>