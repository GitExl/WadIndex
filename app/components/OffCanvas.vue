<script setup lang="ts">
</script>

<template>
  <div class="off-canvas">
    <div class="off-canvas__off">
      <slot name="off"></slot>
    </div>

    <div class="off-canvas__on">
      <slot name="on"></slot>
    </div>
  </div>
</template>

<style lang="scss">
.off-canvas {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  min-height: 100vh;
}

.off-canvas__off {
  min-height: 100vh;
}

.off-canvas__on {
  flex-grow: 1;
  min-height: 100vh;
}
</style>
