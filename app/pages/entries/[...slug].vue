<template>
  <div class="entry" :class="{'entry--has-slides': slides.length}">

    <template v-if="entry">

      <WideSlider v-if="slides.length" :slides="slides"></WideSlider>

      <Layout type="one-column" class="entry__main">

        <template v-slot:start>
          <PageSidebar>

            <LocalNav>
              <LocalNavLink href="#general">General</LocalNavLink>
              <LocalNavLink v-if="entry.mirrorUrls" href="#download" icon="cloud_download">Download</LocalNavLink>
              <LocalNavLink href="#maps" icon="near_me" :counter="entry.levels.length">Maps</LocalNavLink>
              <LocalNavLink href="#music" icon="music_note" :counter="entry.music.length">Music</LocalNavLink>
              <LocalNavLink href="#" icon="description">Text file</LocalNavLink>
            </LocalNav>

          </PageSidebar>
        </template>

        <div id="general" class="entry__head">
          <h1>{{ entry.title }}</h1>
          <AuthorList class="entry__meta-authors" :authors="entry.authors" :limit="10"></AuthorList>
          <div class="entry__meta">
            <Tag v-if="entry.isSingleplayer" type="large">Singleplayer</Tag>
            <Tag v-if="entry.isCooperative" type="large">Cooperative</Tag>
            <Tag v-if="entry.isDeathmatch" type="large">Deathmatch</Tag>
          </div>

          <p v-if="entry.description" class="entry__description">{{ entry.description }}</p>

          <table class="entry__table">
            <tbody>
              <tr v-if="engineTitle">
                <td>Engine</td><td>{{ engineTitle }}</td>
              </tr>
              <tr v-if="gameTitle">
                <td>Game</td><td>{{ gameTitle }}</td>
              </tr>
              <tr>
                <td>Release date</td><td><ClientOnly>{{ entry.timestamp.toLocaleDateString() }}</ClientOnly></td>
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
                      <NuxtLink :to="'/authors/' + author.alias">
                        <template v-if="author.fullName">{{ author.fullName }}</template>
                        <template v-else>{{ author.name }}</template>
                      </NuxtLink>
                    </li>
                  </ul>
                </td>
              </tr>
              <tr v-if="entry.toolsUsed">
                <td>Tools used</td><td class="entry__tools">{{ entry.toolsUsed }}</td>
              </tr>
              <tr v-if="entry.knownBugs">
                <td>Known bugs</td><td>{{ entry.knownBugs }}</td>
              </tr>
              <tr v-if="entry.comments">
                <td>Comments</td><td class="entry__comments">{{ entry.comments }}</td>
              </tr>
              <tr v-if="entry.credits">
                <td>Additional credits</td><td class="entry__credits">{{ entry.credits }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <PageSection v-if="entry.mirrorUrls" id="download" title="Download" icon="cloud_download">
          <table class="entry__table">
            <tbody>
              <tr v-for="mirror of entry.mirrorUrls" :key="mirror.url">
                <td>
                  <span v-if="mirror.isHttpOnly" class="material-icons-outlined">http</span>
                  {{ mirror.title }}<br>
                  <span class="entry__mirror-location">{{ mirror.location }}</span>
                </td>
                <td><a :href="mirror.url">{{ mirror.url }}</a></td>
              </tr>
            </tbody>
          </table>
        </PageSection>

        <PageSection v-if="entry.levels.length" id="maps" title="Maps" icon="near_me">
          <TeaserList layout="columns">
            <LevelTeaser v-for="level of entry.levels" :level="level" :key="level.name"></LevelTeaser>
          </TeaserList>
        </PageSection>

        <PageSection v-if="entry.music.length" id="music" title="Music" icon="music_note">
          <TeaserList layout="columns">
            <MusicTeaser v-for="music of entry.music" :music="music" :key="music.name"></MusicTeaser>
          </TeaserList>
        </PageSection>
      </Layout>

    </template>

  </div>
</template>

<script setup lang="ts">
import { humanFileSize } from '@/utils/FileSize';
import { WideSliderSlide } from '~/components/WideSlider.vue';

const route = useRoute();
const api = useApi();
const runtimeConfig = useRuntimeConfig();

const slug = route.params.slug as string[];
const collection = slug[0];
const path = slug.slice(1, -1).join('/');
const { data: entry } = useAsyncData(() => api.entries.get(collection, path));

useSeoMeta({
  title: entry.value?.title,
});

const readableFileSize = computed((): string|undefined => {
  if (!entry.value) {
    return undefined;
  }

  return humanFileSize(entry.value.size);
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

const slides = computed((): WideSliderSlide[] => {
  if (!entry.value) {
    return [];
  }

  const slides = [];
  for (const image of entry.value.images) {
    slides.push({
      key: image.name,
      imageUrl: runtimeConfig.public.otherUrl + '/' + image.href,
      imageWidth: image.width,
      imageHeight: image.height,
      aspectRatio: image.aspectRatio
    });
  }

  return slides;
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
    case 'doom64': return 'Doom 64';
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
    case 'odamex': return 'Odamex';
    case 'doom64': return 'Doom 64';
    case 'doom64ex': return 'Doom 64 EX';
  }

  return entry.value.engine;
});
</script>

<style lang="scss">
.entry {
  height: 100%;

  &__head {
    margin-bottom: 3rem;

    h1 {
      margin-bottom: 0.625rem;
      margin-top: -0.5rem;
      font-size: 2.75rem;
    }
  }

  &--has-slides {
    .entry__main {
      position: relative;

      &:before {
        content: '';
        display: block;
        width: 100%;
        height: 100%;
        max-height: 40rem;
        background: linear-gradient(0deg, rgba($color-primary-dark, 0) 0%, rgba($color-primary-dark, 0.33) 96%);
        position: absolute;
        top: 0;
        z-index: -10;
      }
    }
  }

  &__main {
    padding-top: 3rem;
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

    .material-icons-outlined {
      font-size: 1.25rem;
      vertical-align: middle;
      margin-right: 0.25rem;
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

  &__description,
  &__tools,
  &__comments,
  &__credits {
    white-space: pre-wrap;
  }

  &__meta {
    margin-bottom: 2.5rem;
  }

  &__mirror-location {
    color: $color-text;
    font-size: 0.75rem;
  }
}
</style>
