<template>
  <template v-if="to">
    <NuxtLink :to="to" class="info-block-row info-block-row--link" :class="{ 'info-block-row--header': props.header }">
      <slot></slot>
      <span class="info-block-row__chevron material-icons-outlined">chevron_right</span>
    </NuxtLink>
  </template>

  <template v-else>
    <div class="info-block-row" :class="{ 'info-block-row--header': props.header }">
      <slot></slot>
    </div>
  </template>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

export interface Props {
  to?: string
  header?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  header: false,
});
</script>

<style lang="scss">
.info-block-row {
  display: grid;
  grid-template-columns: 6.5rem 1fr;
  position: relative;

  > * {
    padding: 0.375rem 0.5rem 0.2rem 0.5rem;
  }

  > *:first-child {
    padding-right: 0.5rem;
  }

  &--header {
    background-color: $color-primary;
    color: #fff;
    font-weight: normal;
    padding-right: 2.25rem;

    &:hover {
      @include rect-solid;
    }
  }

  &--link {
    text-decoration: none;
  }

  &__chevron {
    position: absolute;
    right: 0;
    color: $color-primary-light;
    font-size: 1.25rem;
  }
}
</style>
