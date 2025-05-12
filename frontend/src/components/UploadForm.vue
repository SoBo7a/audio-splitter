<template>
  <div class="upload-form-wrapper">
    <Loading
      :active="isLoading"
      :can-cancel="false"
      :is-full-page="true"
      color="#4f46e5"
      loader="dots"
      :width="64"
      :height="64"
      background-color="rgba(255,255,255,0.7)"
    />

    <form class="upload-form" @submit.prevent="submit">
      <div class="form-header"><h2>Upload & Split</h2></div>

      <label>
        Artist (optional)
        <input v-model="artist" placeholder="Artist name" />
      </label>

      <label>
        Album (optional)
        <input v-model="album" placeholder="Album title" />
      </label>

      <label>
        Release Year (optional)
        <input
          v-model="year"
          type="number"
          min="1900"
          max="2100"
          placeholder="2025"
        />
      </label>

      <label>
        Album Cover (optional)
        <input type="file" @change="onCoverChange" accept="image/*" />
      </label>

      <label>
        Audio File <small>(.mp3 only)</small>
        <input
          class="file-input"
          type="file"
          @change="onFileChange"
          accept=".mp3,audio/mpeg"
          required
        />
      </label>

      <label>
        Tracklist
        <textarea
          v-model="tracklist"
          :placeholder="'00:00 Intro\n01:23 Next Track\n…'"
          rows="6"
          required
        ></textarea>
      </label>

      <div class="form-actions">
        <button v-if="!submitted" type="submit" :disabled="!canSubmit">
          Split
        </button>
        <template v-else>
          <button type="button" @click="resetForm">Clear</button>
          <button type="button" @click="$emit('show-tracks')">
            Show Tracks
          </button>
        </template>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
import Loading from 'vue-loading-overlay'
import { useToast } from 'vue-toastification'

export default {
  components: { Loading },
  data() {
    return {
      artist: '',
      album: '',
      year: '',
      coverFile: null,
      file: null,
      tracklist: '',
      submitted: false,
      isLoading: false
    }
  },
  computed: {
    canSubmit() {
      return this.file && this.tracklist
    }
  },
  methods: {
    onFileChange(e) {
      const toast = useToast()
      const selected = e.target.files[0]
      if (!selected) {
        this.file = null
        return
      }
      // enforce .mp3 extension
      const name = selected.name.toLowerCase()
      if (!name.endsWith('.mp3')) {
        toast.error('Please upload an MP3 file (.mp3)')
        e.target.value = ''
        this.file = null
        return
      }
      this.file = selected
    },
    onCoverChange(e) {
      this.coverFile = e.target.files[0] || null
    },
    resetForm() {
      this.artist = ''
      this.album = ''
      this.year = ''
      this.coverFile = null
      this.file = null
      this.tracklist = ''
      this.submitted = false
      // clear both file inputs
      this.$el.querySelectorAll('input[type=file]').forEach(i => i.value = '')
    },
    async submit() {
      const toast = useToast()
      toast.info('Submitted, please wait…')
      this.isLoading = true

      const form = new FormData()
      form.append('file', this.file)
      if (this.coverFile) form.append('cover', this.coverFile)
      if (this.artist)   form.append('artist', this.artist)
      if (this.album)    form.append('album', this.album)
      if (this.year)     form.append('year', this.year)
      form.append('tracklist', this.tracklist)

      try {
        const res = await axios.post(`${this.$backend}/api/split`, form)
        this.submitted = true
        this.$emit('split-complete', {
          tracks:  res.data.tracks,
          session: res.data.session,
          album:   res.data.album,
          cover:   res.data.cover,
          year:    res.data.year
        })
        toast.success('Split completed successfully!')
      } catch (err) {
        console.error(err)
        toast.error('Error during split. Please try again.')
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>
