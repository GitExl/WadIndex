<template>
  <section class="page-section">
    <h2 class="page-section__title">
      <span v-if="icon" class="material-icons-outlined page-section__icon">{{ icon }}</span>
      {{ title }}
    </h2>

    <slot></slot>
  </section>
</template>

<script setup lang="ts">
export interface Props {
  title: string,
  icon?: string,
}

const props = withDefaults(defineProps<Props>(), {
  icon: undefined,
});
</script>

<style lang="scss">
.page-section {
  margin-bottom: 3rem;

  &__title {
    position: relative;
  }

  &__icon {
    position: relative;
    top: 0.25rem;
    font-size: 2.125rem;

    @media (min-width: 80rem) {
      position: absolute;
      left: -3rem;
    }
  }
}
</style>
