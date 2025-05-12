<template>
  <transition name="fade">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-card">
        <header class="modal-header">
          <h2>
            {{ artist ? `${artist} - ${album}` : `${album} - Tracks` }}
          </h2>
          <button class="close-btn" @click="close">✕</button>
        </header>

        <div class="modal-body">
          <TrackTable
            :tracks="tracks"
            :artist="artist"
            :album="album"
            :cover="cover"
          />
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import TrackTable from './TrackTable.vue'

export default {
  name: 'TrackTableModal',
  components: { TrackTable },
  props: {
    visible: Boolean,
    tracks: Array,
    artist: String,
    album: String,
    cover: String,
  },
  emits: ['update:visible'],
  methods: {
    close() {
      this.$emit('update:visible', false)
    }
  }
}
</script>
