<template>
  <transition name="fade">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-card">
        <header class="modal-header">
          <h2>{{ album }} - Tracks</h2>
          <button class="close-btn" @click="close">✕</button>
        </header>

        <div class="modal-body">
          <TrackTable
            :tracks="tracks"
            :album="album"
            :cover="cover"
            :backend="backend"
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
    album: String,
    cover: String,     // ← new prop
    backend: {
      type: String,
      default: 'http://localhost:8000'
    }
  },
  emits: ['update:visible'],
  methods: {
    close() {
      this.$emit('update:visible', false)
    }
  }
}
</script>
