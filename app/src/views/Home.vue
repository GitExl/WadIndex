<script setup lang="ts">
import Player from '../components/Player.vue'
import EntrySearch from '../components/EntrySearch.vue'
import TrackInfo from '../components/TrackInfo.vue'
import { ref } from 'vue';

</script>

<template>
  <div class="home">
    <div class="home__top">
      <div class="home__left">
        <EntrySearch />
      </div>
      <div class="home__right">
        <!-- <PlayList /> -->
        <!-- <Entry /> -->
      </div>
    </div>
    <div class="home__bottom">
      <TrackInfo title="Hangar 7" author="Jimmy"></TrackInfo>
      <Player url="/midi/hangar7.mid"></Player>
    </div>
  </div>
</template>

<style lang="scss">
.home {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.home__top {
  display: flex;
  flex-direction: row;
  flex: 1;
  height: 80%;
}

.home__left {
  display: flex;
  flex-direction: column;
  width: 30%;
  height: 100%;
}

.home__right {
  width: 70%;
  height: 100%;
  background-color: #111;
}

.home__bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  background-color: #222;
  padding: 1rem;
  height: 7rem;
}
</style>
