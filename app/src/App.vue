<template>
  <div class="app">
    <OffCanvas>
      <template v-slot:off>
        <NavMenu></NavMenu>
      </template>

      <template v-slot:on>

        <router-view v-slot="{ Component }">
          <Suspense timeout="2000">
            <template #default>
              <component :is="Component" :key="$route.path"></component>
            </template>

            <template #fallback>
              <Layout type="one-column" class="app__loader">
                <img src="@/assets/images/skull.gif" width="150" height=150 />
              </Layout>
            </template>
          </Suspense>
        </router-view>

        <PageFooter></PageFooter>
      </template>
    </OffCanvas>
  </div>
</template>

<script setup lang="ts">
import { Suspense } from 'vue';
import Layout from './components/Layout.vue';
import NavMenu from './components/NavMenu.vue';
import OffCanvas from './components/OffCanvas.vue';
import PageFooter from './components/PageFooter.vue';
</script>

<style lang="scss">
.app {
  width: 100vw;
  min-height: 100vh;

  &__loader {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }
}
</style>
