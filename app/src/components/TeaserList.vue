<template>
  <div class="teaser-list" :class="{ ['teaser-list--layout-' + props.layout]: true }">
    <slot></slot>
  </div>
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
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;

  &--layout-columns {
    flex-direction: row;

    > * {
      width: calc(50% - 0.75rem);
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
