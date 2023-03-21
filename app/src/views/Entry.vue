<template>
  <div class="entry">
    <Layout v-if="entry" type="one-column">
      <div class="entry__slider">

      </div>

      <div class="entry__header">
        <h1>{{ entry.title }}</h1>

        <div class="entry__meta">
          <Tag v-if="entry.isSingleplayer">SP</Tag>
          <Tag v-if="entry.isCooperative">COOP</Tag>
          <Tag v-if="entry.isDeathmatch">DM</Tag>
        </div>

        <AuthorList class="entry__meta-authors" :authors="entry.authors" :limit="10"></AuthorList>

        <p v-if="entry.description" class="entry__description">{{ entry.description }}</p>

        <table class="entry__table">
          <tr>
            <td>Engine</td><td>{{ entry.engine }}</td>
          </tr>
          <tr>
            <td>Game</td><td>{{ entry.game }}</td>
          </tr>
          <tr>
            <td>Release date</td><td>{{ entry.timestamp.toDateString() }}</td>
          </tr>
          <tr>
            <td>File</td>
            <td>
              <span class="entry__file">{{ entry.path }}</span><br>
              {{ entry.size }}
            </td>
          </tr>
          <tr>
            <td>Authors</td>
            <td>
              <ul class="entry__authors">
                <li v-for="author of entry.authors" :key="author.alias">
                  <template v-if="author.fullName">{{ author.fullName }}</template>
                  <template v-else>{{ author.name }}</template>
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
    </Layout>
  </div>
</template>

<script setup lang="ts">
import API from '@/api/API'
import AuthorList from '@/components/AuthorList.vue';
import Layout from '@/components/Layout.vue'
import Tag from '@/components/Tag.vue';
import type { EntryData } from '@/data/Entry'
import { onMounted, ref, type Ref } from 'vue'
import { useRoute } from 'vue-router';

const route = useRoute()

const entry: Ref<EntryData|undefined> = ref()

async function fetch() {
  const segments = route.params.path as string[]
  const collection = segments[0]
  const path = segments.slice(1).join('/')

  entry.value = await API.entries.get(collection, path)
}

onMounted(async () => {
  await fetch()
})
</script>

<style lang="scss">
@import '@/assets/scss/base.scss';

.entry {
  h1 {
    margin-left: 0;
    margin-right: 0;
    margin-bottom: 0;
  }

  &__authors {
    padding: 0;
    list-style: none;
    columns: 1;

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
    font-family: 'DejaVu Sans Mono', monospace;
  }

  &__meta-authors {
    display: block;
    font-size: 1.25rem;
    margin-bottom: 2rem;
  }

  &__description {
    margin-bottom: 2rem;
  }

  &__meta {
    margin-bottom: 0.5rem;
  }
}
</style>
