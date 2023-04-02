<template>
  <div class="info-block">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
// const props = defineProps<{
// }>()
</script>

<style lang="scss">
.info-block {
  width: 100%;
  border: 3px solid $color-primary;
  background-color: $color-background;

  &:hover {
    @include rect;
  }
}
</style>
