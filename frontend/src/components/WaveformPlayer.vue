<template>
  <div class="waveform-player">
    <!-- 1) Waveform canvas -->
    <div ref="containerRef" class="waveform-container"></div>

    <!-- 2) Controls row: play button left, time right -->
    <div class="controls-row">
      <button class="play-btn" @click="togglePlay">
        {{ isPlaying ? 'Pause' : 'Play' }}
      </button>
      <div class="time-display">
        {{ currentTimeFormatted }} / {{ totalDurationFormatted }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useWaveSurfer } from '@meersagor/wavesurfer-vue'

// props
const props = defineProps({
  url: {
    type: String,
    required: true
  }
})

// HTML container ref
const containerRef = ref(null)

// Destructure the composable’s returns
const {
  waveSurfer,
  isPlaying,
  currentTime,     // this is a number of seconds
  totalDuration    // this is a number of seconds
} = useWaveSurfer({
  containerRef,
  options: {
    url: props.url,
    barGap: 2,
    barWidth: 2,
    height: 60,
    waveColor: '#ddd',
    progressColor: '#4f46e5',
    cursorColor: '#4f46e5',
    responsive: false
  }
})

// Clean up on unmount
onBeforeUnmount(() => {
  waveSurfer.value.destroy()
})

// format helper
function formatTime(sec = 0) {
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
}

// computed refs for MM:SS strings
const currentTimeFormatted   = computed(() => formatTime(currentTime.value))
const totalDurationFormatted = computed(() => formatTime(totalDuration.value))

// control playback
function togglePlay() {
  waveSurfer.value?.playPause()
}
</script>

<style scoped>
.waveform-player {
  display: flex;
  flex-direction: column;
}

.waveform-container {
  width: 200px;   /* fixed width so it initializes correctly */
  margin-bottom: 0.5rem;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.play-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.time-display {
  font-size: 0.75rem;
  color: #4b5563;
}
</style>
