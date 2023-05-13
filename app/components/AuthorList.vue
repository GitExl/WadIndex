<template>
  <span v-if="props.authors.length" class="author-list">By {{ authors }}</span>
</template>

<script setup lang="ts">
import type { Author } from '@/data/Author';
import { computed } from 'vue';

interface Props {
  authors: Author[],
  limit?: number,
}

const props = withDefaults(defineProps<Props>(), {
  limit: 0
});

const authors = computed((): string => {
  if (props.limit > 0) {
    const listed = props.authors.slice(0, props.limit).map((item) => {
      return item.fullName ?? item.name;
    });
    if (props.authors.length > props.limit) {
      return listed.join(', ') + ' and others';
    }
  }

  const listed = props.authors.map((item) => {
    return item.fullName ?? item.name;
  });

  if (listed.length === 1) {
    return listed[0];
  }

  return listed.slice(0, -1).join(', ') + ' and ' + listed.slice(-1);
});
</script>

