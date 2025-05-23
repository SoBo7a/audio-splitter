<template>
  <div class="track-table">
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th class="select-cell">
              <input type="checkbox" v-model="allSelected" />
            </th>
            <th>Preview</th>
            <th>Track</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(t, i) in tracks" :key="i">
            <!-- 1) Select checkbox -->
            <td class="select-cell">
              <input type="checkbox" :value="i" v-model="selected" />
            </td>

            <!-- 2) Waveform preview -->
            <td class="waveform-cell">
              <!-- Use relative path: -->
              <WaveformPlayer :url="t.path" />
              <!-- Use below for development -->
              <!-- <WaveformPlayer :url="$backend + t.path" /> -->
            </td>

            <!-- 3) Track number + title -->
            <td class="title-cell">
              <span class="track-number">{{ i + 1 }}.</span>
              <span class="track-title">{{ t.title }}</span>
            </td>

            <!-- 4) Download link -->
            <td class="actions">
              <a
                :href="t.path"
                :download="filenameFromPath(t.path)"
                target="_blank"
              >
                Download
              </a>
              <!-- Use below for development -->
              <!--
              <a
                :href="$backend + t.path"
                :download="filenameFromPath(t.path)"
                target="_blank"
              >
                Download
              </a>
              -->
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <button
      class="download-selected"
      @click="downloadSelected"
      :disabled="!selected.length"
    >
      Download Selected ({{ selected.length }})
    </button>
  </div>
</template>

<script>
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import WaveformPlayer from './WaveformPlayer.vue'

export default {
  name: 'TrackTable',
  components: { WaveformPlayer },
  props: {
    artist: {
      type: String,
      default: ''
    },
    tracks: Array,
    album: String,
    cover: String, // e.g. "/api/download/<session>/cover.jpg"
  },
  data() {
    return {
      selected: []
    }
  },
  computed: {
    allSelected: {
      get() {
        return this.selected.length === this.tracks.length
      },
      set(val) {
        this.selected = val
          ? this.tracks.map((_, i) => i)
          : []
      }
    }
  },
  methods: {
    filenameFromPath(path) {
      // strip off everything before the last '/'
      return path.split('/').pop()
    },

    async downloadSelected() {
      if (!this.selected.length) return

      const zip = new JSZip()
      // Build the folder name as "Artist – Album" if artist given, else just album or "tracks"
      const folderName = this.artist
        ? `${this.artist} - ${this.album || 'tracks'}`
        : (this.album || 'tracks')
      const folder = zip.folder(folderName)

      // include cover first
      if (this.cover) {
        try {
          // use relative cover URL
          let coverUrl = this.cover
          // Use below for development
          // let coverUrl = this.$backend + this.cover

          const resp = await fetch(coverUrl)
          if (resp.ok) {
            const blob = await resp.blob()
            const coverName = this.filenameFromPath(this.cover)
            folder.file(coverName, blob)
          }
        } catch (e) {
          console.warn("Couldn't fetch cover:", e)
        }
      }

      // then the selected tracks, using relative URLs
      for (const idx of this.selected) {
        const t = this.tracks[idx]
        let url = t.path
        // Use below for development
        // let url = this.$backend + t.path

        const resp = await fetch(url)
        if (!resp.ok) {
          console.error('Fetch failed', url, resp.status)
          continue
        }
        const blob     = await resp.blob()
        const filename = this.filenameFromPath(t.path)
        folder.file(filename, blob)
      }

      const content = await zip.generateAsync({ type: 'blob' })
      saveAs(content, `${folderName}.zip`)
    }
  }
}
</script>

<style scoped>
.track-table {
  .select-cell {
    width: 2.5rem;
    text-align: center;
  }
  .waveform-cell {
    min-width: 200px;
  }
  .actions a {
    margin-right: 0.5rem;
  }
  .download-selected {
    margin-top: 1rem;
  }
}
</style>
