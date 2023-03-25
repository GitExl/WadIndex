<template>
  <div class="entry">

    <div v-if="entry" class="entry__slider">
      <div ref="container" class="keen-slider">
        <div v-for="image of imageList" :key="image.name" class="keen-slider__slide">
          <img :src="imageBaseUrl + '/' + image.href" :width="image.width" :height="image.height" loading="lazy">
        </div>
      </div>
    </div>

    <Layout v-if="entry" type="one-column">

      <div class="entry__section">
        <h1>{{ entry.title }}</h1>
        <AuthorList class="entry__meta-authors" :authors="entry.authors" :limit="10"></AuthorList>
        <div class="entry__meta">
          <Tag v-if="entry.isSingleplayer" type="large">SP</Tag>
          <Tag v-if="entry.isCooperative" type="large">COOP</Tag>
          <Tag v-if="entry.isDeathmatch" type="large">DM</Tag>
        </div>

        <p v-if="entry.description" class="entry__description">{{ entry.description }}</p>

        <table class="entry__table">
          <tr v-if="engineTitle">
            <td>Engine</td><td>{{ engineTitle }}</td>
          </tr>
          <tr v-if="gameTitle">
            <td>Game</td><td>{{ gameTitle }}</td>
          </tr>
          <tr>
            <td>Release date</td><td>{{ entry.timestamp.toDateString() }}</td>
          </tr>
          <tr>
            <td>File</td>
            <td>
              <span class="entry__file">{{ entry.path.split('/').pop() }}</span><br>
              <template v-if="readableFileSize">{{ readableFileSize }}</template>
            </td>
          </tr>
          <tr v-if="entry.authors.length">
            <td v-if="entry.authors.length > 1">Authors</td>
            <td v-else>Author</td>
            <td>
              <ul class="entry__authors" :class="authorListClasses">
                <li v-for="author of entry.authors" :key="author.alias">
                  <router-link :to="{ name: 'author', params: { alias: author.alias }}">
                    <template v-if="author.fullName">{{ author.fullName }}</template>
                    <template v-else>{{ author.name }}</template>
                  </router-link>
                </li>
              </ul>
            </td>
          </tr>
          <tr v-if="entry.toolsUsed">
            <td>Tools used</td><td>{{ entry.toolsUsed }}</td>
          </tr>
          <tr v-if="entry.knownBugs">
            <td>Known bugs</td><td>{{ entry.knownBugs }}</td>
          </tr>
          <tr v-if="entry.comments">
            <td>Comments</td><td>{{ entry.comments }}</td>
          </tr>
        </table>
      </div>

      <div v-if="entry.mirrorUrls" class="entry__section">
        <h2>Download</h2>

        <table class="entry__table">
          <tr v-for="mirror of entry.mirrorUrls" :key="mirror.url">
            <td>
              {{ mirror.title }}<br>
              <span class="entry__mirror-location">{{ mirror.location }}</span>
            </td>
            <td><a :href="mirror.url">{{ mirror.url }}</a></td>
          </tr>
        </table>
      </div>

      <div class="entry__section">
        <h2>Maps</h2>
      </div>

      <div class="entry__section">
        <h2>Music</h2>
      </div>

    </Layout>
  </div>
</template>

<script setup lang="ts">
import API from '@/api/API';
import AuthorList from '@/components/AuthorList.vue';
import Layout from '@/components/Layout.vue';
import Tag from '@/components/Tag.vue';
import type { EntryData } from '@/data/Entry'
import { humanFileSize } from '@/utils/FileSize';
import { ref, type Ref, computed, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { useKeenSlider, type KeenSliderInstance } from 'keen-slider/vue.es';
import type { IndexImage } from '@/data/IndexImage';

const route = useRoute();

const entry: Ref<EntryData|undefined> = ref();
let container: Ref<HTMLElement|undefined> = ref();
let slider: Ref<KeenSliderInstance|undefined> = ref();

const imageBaseUrl = import.meta.env.VITE_STORAGE_BASE_URL;


const segments = route.params.path as string[];
const collection = segments[0];
const path = segments.slice(1).join('/');

entry.value = await API.entries.get(collection, path);

[container, slider] = useKeenSlider({
  loop: true,
  mode: 'snap',

  slides: {
    origin: 'center',
    perView: 1.25,
    spacing: 8,
  },

  breakpoints: {
    '(min-width: 35rem)': {
      slides: {
        origin: 'center',
        perView: 2.25,
        spacing: 16,
      },
    },
    '(min-width: 60rem)': {
      slides: {
        origin: 'center',
        perView: 3.25,
        spacing: 32,
      },
    },
  },
}, []);


onBeforeUnmount(() => {
  slider.value?.destroy();
});

const readableFileSize = computed((): string|undefined => {
  if (!entry.value) {
    return undefined;
  }

  return humanFileSize(entry.value?.size);
});

const authorListClasses = computed((): Record<string, boolean> => {
  const authorCount = entry.value?.authors.length;
  if (!authorCount) {
    return {}
  }

  return {
    'entry__authors--one-column': authorCount < 4,
    'entry__authors--two-column': authorCount >= 4 && authorCount < 9,
    'entry__authors--three-column': authorCount >= 9,
  }
});

const imageList = computed((): IndexImage[] => {
  if (!entry.value) {
    return [];
  }
  if (entry.value.images.length < 4) {
    return entry.value.images.concat(entry.value.images);
  }

  return entry.value.images;
});

const gameTitle = computed((): string|undefined => {
  if (!entry.value?.game) {
    return undefined;
  }

  switch (entry.value?.game) {
    case 'doom': return 'Doom';
    case 'doom2': return 'Doom 2';
    case 'heretic': return 'Heretic';
    case 'hexen': return 'Hexen';
    case 'strife': return 'Strife';
    case 'tnt': return 'TNT: Evilution';
    case 'plutonia': return 'The Plutonia Experiment';
    case 'chex': return 'Chex Quest';
  }

  return entry.value.game;
});

const engineTitle = computed((): string|undefined => {
  if (!entry.value?.engine) {
    return undefined;
  }

  switch (entry.value?.engine) {
    case 'unknown': return 'Unknown';
    case 'doom': return 'Doom';
    case 'heretic': return 'Heretic';
    case 'hexen': return 'Hexen';
    case 'strife': return 'Strife';
    case 'no_limits': return 'Limit removing';
    case 'boom': return 'Boom compatible';
    case 'mbf': return 'Marine\'s Best Friend';
    case 'zdoom': return 'ZDoom';
    case 'gzdoom': return 'GZDoom';
    case 'legacy': return 'Doom Legacy';
    case 'skulltag': return 'Skulltag';
    case 'zdaemon': return 'Zdaemon';
    case 'doomsday': return 'Doomsday';
    case 'edge': return 'EDGE';
    case 'eternity': return 'Eternity';
    case 'doom_retro': return 'Doom Retro';
    case 'zandronum': return 'Zandronum';
    case 'odamex': return 'ODamex';
  }

  return entry.value.engine;
});

</script>

<style lang="scss">
@import '@/assets/scss/base.scss';
@import url('keen-slider/keen-slider.css');

.entry {
  h1 {
    margin-bottom: 0;
    font-size: 2.75rem;
  }

  &__slider {
    width: 100vw;
    background-color: rgba($color-primary-dark, 0.33);
    cursor: pointer;
    margin-bottom: 2rem;

    img {
      width: 100%;
      height: auto;
    }
  }

  &__authors {
    padding: 0;
    list-style: none;
    columns: 1;
  }

  &__authors--two-column {
    @media(min-width: 35rem) {
      columns: 2;
    }
  }

  &__authors--three-column {
    @media(min-width: 35rem) {
      columns: 2;
    }

    @media(min-width: 60rem) {
      columns: 3;
    }
  }

  &__table {
    tr {
      td:first-child {
        font-weight: normal;
        color: $color-accent;
        min-width: 9rem;
      }
    }

    td {
      vertical-align: top;
      padding: 0.5rem 2rem 0.5rem 0;
    }
  }

  &__file {
    font-size: 0.9375rem;
    font-family: 'DejaVu Sans Mono', monospace;
  }

  &__meta-authors {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
  }

  &__description {
    margin-bottom: 2rem;
  }

  &__meta {
    margin-bottom: 2.5rem;
  }

  &__section {
    margin-bottom: 3rem;
  }

  &__mirror-location {
    color: $color-text;
    font-size: 0.75rem;
  }
}
</style>
