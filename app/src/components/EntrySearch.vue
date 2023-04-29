<template>
  <div class="entry-search">
    <input type="search" placeholder="Search all entries" />
  </div>
</template>

<script setup lang="ts">
import { ref, type Ref } from "vue";

const searchTerms: Ref<string> = ref('')

function input(event: Event) {
  const target = event.target as HTMLInputElement
  searchTerms.value = target.value
}
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
