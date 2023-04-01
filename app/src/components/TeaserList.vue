<template>
  <ul class="teaser-list" :class="{ ['teaser-list--layout-' + props.layout]: true }">
    <slot></slot>
  </ul>
</template>

<script setup lang="ts">
export interface Props {
  layout: string
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'normal',
})
</script>

<style lang="scss">
.teaser-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;

  &--layout-columns {
    flex-direction: row;

    > * {
      width: calc(50% - 1.25rem);
    }
  }

  &--layout-rows {
    flex-direction: column;

    > * {
      width: 100%;
    }
  }
}
</style>
