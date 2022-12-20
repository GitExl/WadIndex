<script setup lang="ts">
import type { Entry } from '@/data/Entry';

const props = defineProps<{
  entries: Entry[],
}>()

const emit = defineEmits<{
  (e: 'select', entry: Entry): void
}>()

function selectEntry(entry: Entry) {
  emit('select', entry)
}
</script>

<template>
  <div class="entry-list">
    <ul>
      <li v-for="entry in entries" :key="entry.id" @click="selectEntry(entry)">
        <h3>{{ entry.title }}</h3>
        <p v-if="entry.authors.length" class="entry__authors">By {{ entry.authors?.join(', ') }}</p>
        <p v-if="entry.description" class="entry__description">{{ entry.description.slice(0, 200) + (200 < entry.description.length ? '&hellip;' : '') }}</p>
      </li>
    </ul>
  </div>
</template>

<style lang="scss">
.entry-list {
  width: 100%;
  height: 100%;
  overflow-y: auto;

  ul {
    padding: 0;
    list-style: none;
  }

  li {
    padding: 0.5rem;
    cursor: pointer;

    &:hover {
      background-color: #124;
    }
  }

  h3 {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.125rem;
  }

  .entry__authors {
    margin: 0;
    font-size: 0.85rem;
    font-style: italic;
  }

  .entry__description {
    margin: 0;
    font-size: 0.85rem;
  }
}
</style>
