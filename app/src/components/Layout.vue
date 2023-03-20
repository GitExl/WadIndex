<script setup lang="ts">
export interface Props {
  type?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'one-column',
});
</script>

<template>
  <div class="layout" :class="{['layout--' + props.type]: true}">
    <slot></slot>
  </div>
</template>

<style lang="scss">
@import '@/assets/scss/base.scss';
.layout {
  margin: 0 auto;
  padding: 0 1rem;
  gap: 0.5rem;

  @media(min-width: 60rem) {
    padding: 0 2rem;
    gap: 1rem;
  }

  &--one-column {
    max-width: 60rem;
  }

  &--two-column {
    max-width: 60rem;

    @media(min-width: 100rem) {
      max-width: 100rem;
      display: flex;
      flex-direction: row;

      > * {
        width: 50%;
      }
    }
  }
}
</style>
