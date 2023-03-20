<script setup lang="ts">
</script>

<template>
  <span class="tag">
    <slot></slot>
  </span>
</template>

<style lang="scss">
@import '@/assets/scss/base.scss';

.tag {
  font-family: 'DejaVu Sans Condensed', sans-serif;
  display: inline-block;
  background-color: $color-accent;
  color: #000;
  padding: 0.1rem 0.45rem;
  border-radius: 0.5rem;
  line-height: 1;
  font-size: 0.75rem;
  font-weight: 700;
  margin-right: 0.25rem;
  vertical-align: text-top;
}
</style>
