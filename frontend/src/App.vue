<template>
  <div id="app" class="app-container">
    <h1 class="app-title">Audio Splitter</h1>

    <div class="controls">
      <UploadForm
        @split-complete="handleSplit"
        @show-tracks="modalVisible = true"
        ref="uploadForm"
        :has-tracks="tracks.length > 0"
      />

      <!-- this button is now moved into the form itself -->
    </div>

    <TrackTableModal
      v-model:visible="modalVisible"
      :tracks="tracks"
      :album="album"
      :cover="cover"
      :backend="backend"
    />
  </div>
</template>

<script>
import UploadForm from './components/UploadForm.vue'
import TrackTableModal from './components/TrackTableModal.vue'

export default {
  components: { UploadForm, TrackTableModal },
  data() {
    return {
      tracks: [],
      album: '',
      session: '',
      cover: null,
      backend: 'http://localhost:8000',
      modalVisible: false
    }
  },
  methods: {
    handleSplit({ tracks, session, album, cover }) {
      this.tracks = tracks
      this.session = session
      this.album = album
      this.cover = cover
      this.modalVisible = true      // auto‐open on split
    }
  }
}
</script>
