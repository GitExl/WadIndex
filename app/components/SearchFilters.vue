<template>
  <div class="search-filters">
    <h4 class="search-filters__title">{{ title }}</h4>
    <ul class="search-filters__list">
      <slot></slot>
    </ul>
</div>

</template>

<script setup lang="ts">
export interface Props {
  title: string
}

const props = defineProps<Props>();
</script>

<style lang="scss">
.search-filters {
  width: 100%;
  margin-top: 2rem;

  &__title {
    margin: 0;
    font-family: 'DejaVu Sans Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 0.5rem;
  }

  &__list {
    list-style: none;
    padding: 0;
  }
}
</style>
