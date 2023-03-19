<script setup lang="ts">
import type { EntryTeaserData } from '@/data/EntryTeaser';
import { computed } from 'vue';

const props = defineProps<{
  entry: EntryTeaserData
}>()

const thumbnailUrl = computed(() => {
  if (props.entry.image) {
    return import.meta.env.VITE_STORAGE_BASE_URL + '/' + props.entry.image?.hrefThumbnail;
  }

  return undefined;
});

const description = computed(() => {
  if (props.entry.description) {
    if (props.entry.description.length < 350) {
      return props.entry.description;
    }

    return props.entry.description.slice(0, 350) + '…';
  }

  return undefined;
});

const authors = computed(() => {
  const listed = props.entry.authors.slice(0, 5).map((item) => {
    return item.fullName ?? item.name;
  });
  if (props.entry.authors.length > 5) {
    return listed.join(', ') + ' and others';
  }

  return listed.join(', ');
});
</script>

<template>
  <div class="entry-teaser">
    <div class="entry-teaser__info">
      <h2>{{ entry.title }}</h2>
      <p v-if="entry.authors.length" class="entry-teaser__subtitle">By {{ authors }}</p>
      <p v-if="entry.description" class="entry-teaser__description">{{ description }}</p>
    </div>
    <div class="entry-teaser__tags">

    </div>
    <div class="entry-teaser__image">
      <img v-if="thumbnailUrl" :src="thumbnailUrl" loading="lazy">
      <div v-else class="entry-teaser__placeholder"></div>
    </div>
  </div>
</template>

<style lang="scss">
@import '@/assets/scss/base.scss';

.entry-teaser {
  @include rect;

  padding: 1rem;
  display: flex;
  flex-direction: row;
  cursor: pointer;
  width: 100%;

  h2 {
    font-size: 1.25rem;
    font-family: 'DejaVu Sans Condensed', sans-serif;
    font-weight: normal;
    margin-bottom: 0;
  }

  &__subtitle {
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 0.5rem;
  }

  &__description {
    font-weight: 300;
    color: rgba($color-text, 0.66);
  }

  &__info {
    flex-grow: 1;
  }

  &__image {
    padding-left: 1rem;

    img {
      width: 13rem;
      height: auto;
      image-rendering: pixelated;
      display: block;
    }
  }

  &__placeholder {
    width: 13rem;
    // height: 9.75rem;
  }
}
</style>
