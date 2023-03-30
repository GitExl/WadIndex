<template>
  <section class="page-section">
    <h2>
      <span v-if="icon" class="material-icons-outlined">{{ icon }}</span>
      {{ title }}
    </h2>
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

  h2 {
    position: relative;
  }

  span {
    font-size: 2.125rem;
    position: absolute;
    left: -3.25rem;
    top: 0.6125rem;
  }
}
</style>
