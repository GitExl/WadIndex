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
    font-size: 2.125rem;
    position: absolute;
    left: -3.25rem;
    top: 0.6125rem;
  }
}
</style>
