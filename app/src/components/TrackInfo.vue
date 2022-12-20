<script setup lang="ts">

const props = defineProps<{
  title: string,
  author: string
}>()
</script>

<template>
  <div class="track-info">
    <h3>{{ title }}</h3>
    <p>{{ author }}</p>
  </div>
</template>

<style lang="scss">
.track-info {
  display: flex;
  flex-direction: column;
  justify-content: center;

  h3 {
    font-size: 1rem;
    font-weight: 700;
  }

  p {
    font-size: 0.85rem;
    margin: 0;
  }
}
</style>
