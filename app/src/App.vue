<script setup lang="ts">
import NavMenu from './components/NavMenu.vue';
import OffCanvas from './components/OffCanvas.vue';

</script>

<template>
  <div class="app__background" :class="{ 'app__background--visible': $route.name === 'home' }">
    <div class="app__background-row app__background-row--1">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/btsx_e1_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/biowar_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/dcv_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/abyss24a_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/longtrek_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/projectunity_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/rlmchaos_titlepic_thumb.webp">
    </div>
    <div class="app__background-row app__background-row--2">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/tmmc2_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/toon2b_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/v64_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/world_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/techwars_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/dot_titlepic_thumb.webp">
      <img src="http://storage.idgames.local/graphics/levels/doom2/megawads/requiem_titlepic_thumb.webp">
    </div>
  </div>

  <div class="app">
    <OffCanvas>
      <template v-slot:off>
        <NavMenu></NavMenu>
      </template>

      <template v-slot:on>
        <Header></Header>
        <router-view></router-view>

        <!-- <div class="home__bottom">
          <TrackInfo title="Hangar 7" author="Jimmy"></TrackInfo>
          <Player url="/midi/hangar7.mid"></Player>
        </div> -->
      </template>
    </OffCanvas>
  </div>
</template>

<style lang="scss">
@import '@/assets/scss/base.scss';

.app {
  width: 100vw;
  min-height: 100vh;
}

.app__background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  overflow-x: hidden;
  padding: 0.25rem;
  opacity: 0;
  transition: opacity 0.33s ease-out;

  &--visible {
    opacity: 0.25;
  }
}

.app__background-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  width: 150%;

  img {
    width: auto;
    height: 14rem;
    margin: 0.5rem;
    display: block;
    image-rendering: pixelated;
  }

  &--2 {
    left: -25%;
  }
}
</style>
