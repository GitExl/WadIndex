<template>
  <div class="entry-search">
    <input type="search" placeholder="Search all entries" v-model.trim="model" />
  </div>
</template>

<script setup lang="ts">
const model = defineModel();
</script>

<style lang="scss">
.entry-search {
  width: 100%;
  max-width: 26rem;
  display: flex;
  flex-direction: column;

  input {
    width: 100%;
  }
}
</style>
