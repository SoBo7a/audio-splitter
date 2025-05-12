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
    </div>

    <TrackTableModal
      v-model:visible="modalVisible"
      :tracks="tracks"
      :artist="artist"
      :album="album"
      :cover="cover"
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
      artist: '',
      tracks: [],
      album: '',
      session: '',
      cover: null,
      modalVisible: false
    }
  },
  methods: {
    handleSplit({ tracks, session, album, cover, artist }) {
      this.tracks = tracks
      this.session = session
      this.artist = artist
      this.album = album
      this.cover = cover
      this.modalVisible = true      // auto‐open on split
    }
  }
}
</script>
