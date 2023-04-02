<template>
  <div class="app">
    <OffCanvas>
      <template v-slot:off>
        <NavMenu></NavMenu>
      </template>

      <template v-slot:on>
        <Suspense>
          <router-view></router-view>
        </Suspense>

        <!-- <div class="home__bottom">
          <TrackInfo title="Hangar 7" author="Jimmy"></TrackInfo>
          <Player url="/midi/hangar7.mid"></Player>
        </div> -->

        <PageFooter></PageFooter>
      </template>
    </OffCanvas>
  </div>
</template>

<script setup lang="ts">
import NavMenu from './components/NavMenu.vue';
import OffCanvas from './components/OffCanvas.vue';
import PageFooter from './components/PageFooter.vue';
</script>

<style lang="scss">
.app {
  width: 100vw;
  min-height: 100vh;
}
</style>
