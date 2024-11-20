<template>
  <div class="search-sort">
    <h4 class="search-sort__title">{{ title }}</h4>
    <select :name="name" v-model="model">
      <option v-for="(option, key) in options" :value="key">{{ option.title }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  name: string
  options: SearchSortOptions
}

export interface SearchSortOption {
  title: string
  field: string
  order: string
}

export type SearchSortOptions = Record<string, SearchSortOption>

const props = defineProps<Props>();
const model = defineModel();
</script>

<style lang="scss">
.search-sort {
  width: 100%;
  margin-top: 2rem;

  &__title {
    margin: 0;
    font-family: 'DejaVu Sans Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 0.5rem;
  }

  select {
    width: 100%;
    padding: 0.333rem;
    cursor: pointer;
  }
}
</style>
