<script setup lang="ts">
import { computed, ref } from '@vue/reactivity'
import * as JSSynth from 'js-synthesizer'
import { onBeforeUnmount, onMounted } from 'vue'
import * as midiParser from 'midi-parser-js'

let ac: AudioContext| undefined = undefined
let synth: JSSynth.AudioWorkletNodeSynthesizer | undefined = undefined
let midiData: any
let intervalId: number = 0

const isPlaying = ref(false)
const seekCurrent = ref(0)
const seekTotal = ref(0)
const timeCurrent = ref(0)
const timeTotal = ref(0)

const props = defineProps<{
  url: string,
}>()


async function loadBinary(url: string): Promise<ArrayBuffer> {
	const resp = await fetch(url)
	return await resp.arrayBuffer()
}

async function initSynth(): Promise<JSSynth.AudioWorkletNodeSynthesizer> {
  ac = new AudioContext({
    sampleRate: 48000
  })

  await JSSynth.Synthesizer.waitForWasmInitialized()
  await JSSynth.waitForReady()

  await ac.audioWorklet.addModule('/js-synthesizer/libfluidsynth-2.2.1.js')
  await ac.audioWorklet.addModule('/js-synthesizer/js-synthesizer.worklet.min.js')

  const synth = new JSSynth.AudioWorkletNodeSynthesizer()
  synth.init(ac.sampleRate, {
    chorusActive: false,
    chorusDepth: 8.0,
    chorusLevel: 2.0,
    chorusNr: 3,
    chorusSpeed: 0.3,
    midiChannelCount: 16,
    midiBankSelect: 'gm',
    minNoteLength: 10,
    overflowAge: 1000.0,
    overflowImportantValue: 5000.0,
    overflowImportantChannels: [],
    overflowPercussion: 4000.0,
    overflowReleased: -2000.0,
    overflowSustained: -1000.0,
    overflowVolume: 500.0,
    polyphony: 256,
    reverbActive: false,
    reverbDamp: 0.0,
    reverbLevel: 0.9,
    reverbRoomSize: 0.2,
    reverbWidth: 0.5,
  })

  const node = synth.createAudioNode(ac)
  node.connect(ac.destination)

  const soundFont = await loadBinary('/soundfont/gzdoom.sf2')
  await synth.loadSFont(soundFont)

  synth.setGain(0.2)
  synth.setInterpolation(7)

  return synth
}

async function play() {
  if (!synth) {
    synth = await initSynth()
  }

  if (!midiData) {
    await loadSong(props.url)
  }

  isPlaying.value = !synth.isPlayerPlaying();
  if (synth.isPlayerPlaying()) {
    synth.stopPlayer()
    await synth.waitForPlayerStopped()
  } else {
    await synth.playPlayer()
  }
}

async function loadSong(url: string) {
  if (!synth) {
    return
  }

  const data = await loadBinary(url)
  const dataArray = new Uint8Array(data)
  await synth.addSMFDataToPlayer(data)
  midiData = midiParser.parse(dataArray)
  await synth.playPlayer()
  synth.stopPlayer()

  updateSeekBar()
}

async function seek(event: Event) {
  if (!synth) {
    return
  }

  const target = event.target as HTMLInputElement
  if (!target) {
    return
  }

  synth.seekPlayer(parseInt(target.value, 10))
  if (!synth.isPlayerPlaying()) {
    await synth.playPlayer()
    isPlaying.value = true
  }
  updateSeekBar()
}

async function updateSeekBar() {
  if (!synth) {
    return
  }

  seekTotal.value = await synth.retrievePlayerTotalTicks()
  seekCurrent.value = await synth.retrievePlayerCurrentTick()

  if (midiData) {
    const bpm = await synth.retrievePlayerBpm()
    const msPerTick = 60000 / (midiData.timeDivision * bpm)
    timeTotal.value = (seekTotal.value * msPerTick) / 1000
    timeCurrent.value = (seekCurrent.value * msPerTick) / 1000
  } else {
    timeTotal.value = -1
    timeCurrent.value = -1
  }
}


onMounted(async () => {
  intervalId = setInterval(updateSeekBar, 1000)
})

onBeforeUnmount(() => {
  clearInterval(intervalId)

  if (synth) {
    synth.closePlayer()
    synth.close()
  }
})


const playText = computed(() => {
  return isPlaying.value ? '⏸' : '⏵'
})

const current = computed(() => {
  if (timeCurrent.value >= 0) {
    const minutes = Math.floor(timeCurrent.value / 60)
    const seconds = String(Math.floor(timeCurrent.value % 60)).padStart(2, '0')
    return minutes + ':' + seconds
  }

  return '???'
})
</script>

<template>
  <div class="player">
    <div class="player__controls">
      <button class="player__control player__control-previous">⏮</button>
      <button class="player__control player__control-play" @click="play">{{ playText }}</button>
      <button class="player__control player__control-next">⏭</button>
    </div>
    <div class="player__seek">
      <input class="player__seek-bar" type="range" min="0" :max="seekTotal" :value="seekCurrent" @change="seek">
      <div class="player__seek-time">{{ current }}</div>
    </div>
  </div>
</template>

<style lang="scss">
.player {
  width: 100%;
  max-width: 32rem;
  display: flex;
  flex-direction: column;
}

.player__controls {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.player__control {
  background-color: transparent;
  color: #aaa;
  border: none;
  width: 3rem;
  height: 3rem;
  line-height: 3rem;
  font-weight: 700;
  font-size: 2rem;
  cursor: pointer;
  transform: scale(1);

  &:hover {
    color: #fff;
    transform: scale(1.1);
  }
}

.player__seek {
  display: flex;
  flex-direction: row;
  padding: 0.5rem 0;
}

.player__seek-bar {
  width: 100%;
  cursor: pointer;
}

.player__seek-time {
  font-size: 0.85rem;
  padding-left: 1rem;
}
</style>
