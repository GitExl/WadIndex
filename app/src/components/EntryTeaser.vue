<template>
  <div class="entry-teaser">
    <div class="entry-teaser__info">
      <h2><router-link :to="href">{{ entry.title }}</router-link></h2>

      <p class="entry-teaser__subtitle">
        <AuthorList class="entry-teaser__authors" :authors="entry.authors" :limit="5"></AuthorList>
        <Tag v-if="entry.isSingleplayer">SP</Tag>
        <Tag v-if="entry.isCooperative">COOP</Tag>
        <Tag v-if="entry.isDeathmatch">DM</Tag>
      </p>

      <p v-if="entry.description" class="entry-teaser__description">{{ description }}</p>
    </div>

    <div v-if="thumbnailUrl" class="entry-teaser__image">
      <img :src="thumbnailUrl" :width="entry.image?.width" :height="entry.image?.height" loading="lazy" :style="{ 'aspect-ratio': entry.image?.aspectRatio }">
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EntryTeaserData } from '@/data/EntryTeaser';
import Tag from '@/components/Tag.vue';
import { computed } from 'vue';
import AuthorList from './AuthorList.vue';

const props = defineProps<{
  entry: EntryTeaserData
}>()

const thumbnailUrl = computed(() => {
  if (props.entry.image) {
    return import.meta.env.VITE_STORAGE_BASE_URL + '/' + props.entry.image.hrefThumbnail;
  }

  return undefined;
});

const description = computed((): string|undefined => {
  const maxLength = props.entry.image ? 200 : 350

  if (props.entry.description) {
    if (props.entry.description.length < maxLength) {
      return props.entry.description;
    }

    return props.entry.description.slice(0, maxLength) + '…';
  }

  return undefined;
});

const href = computed((): string => {
  return '/entries/' + props.entry.collection + '/' + props.entry.path + '/';
});
</script>

<style lang="scss">
.entry-teaser {
  @include rect;

  position: relative;
  padding: 1rem;
  display: flex;
  flex-direction: row;
  cursor: pointer;
  width: 100%;

  h2 {
    margin-bottom: 0;

    a {
      display: block;
      color: $color-accent;
      font-size: 1.25rem;
      font-family: 'DejaVu Sans Condensed', sans-serif;
      font-weight: normal;
      text-decoration: none;

      &:after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
      }
    }
  }

  &__subtitle {
    margin-bottom: 0.5rem;
  }

  &__description {
    color: rgba($color-text, 0.66);
  }

  &__info {
    flex-grow: 1;
  }

  &__authors {
    font-size: 1rem;
    margin-right: 0.5rem;
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
}
</style>
