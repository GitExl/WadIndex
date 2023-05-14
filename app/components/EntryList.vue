<script setup lang="ts">
import type { EntryTeaserData } from '@/data/EntryTeaser';
import EntryTeaser from './EntryTeaser.vue';

const props = defineProps<{
  entries: EntryTeaserData[] | null,
}>()

const emit = defineEmits<{
  (e: 'select', entry: EntryTeaserData): void
}>()

function selectEntry(entry: EntryTeaserData) {
  emit('select', entry)
}
</script>

<template>
  <div class="entry-list">
    <ul v-if="entries">
      <EntryTeaser v-for="entry in entries" :key="entry.collection + entry.path" :entry="entry" @click="selectEntry(entry)" />
    </ul>
  </div>
</template>

<style lang="scss">
.entry-list {
  margin-bottom: 3rem;

  ul {
    padding: 0;
    margin: 0;
    list-style: none;
  }
}
</style>
