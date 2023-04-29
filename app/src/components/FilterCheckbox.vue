<template>
  <li class="filter-checkbox">
    <input :id="name" type="checkbox"> <label :for="name">{{ title }}</label>
  </li>
</template>

<script setup lang="ts">
export interface Props {
  name: string
  title: string
}

const props = defineProps<Props>();
</script>

<style lang="scss">
.filter-checkbox {
  margin: 0.25rem 0;

  label {
    color: $color-primary-light;
    margin-left: 0.5rem;
    cursor: pointer;
  }

  input {
    cursor: pointer;
  }
}
</style>
