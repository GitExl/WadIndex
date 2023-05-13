<template>
  <div class="info-block">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="scss">
.info-block {
  width: 100%;
  border: 3px solid $color-primary;

  &:hover {
    @include rect;
  }
}
</style>
