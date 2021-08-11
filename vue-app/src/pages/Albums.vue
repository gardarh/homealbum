<template>
  <h1>Albums</h1>
  <LoadingAnimation v-if="!isLoaded" />
  <div v-else>
    <ul class="list-unstyled">
      <li v-for="album in albums" :key="album.id">
        <router-link :to="{
            name: 'Album',
            params: {albumId: album.id}
        }">{{ album.name }}</router-link>
        ({{ reprAlbumDateRange(album)}})
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { albumsListFetch } from '../utils/api'
import { DateTime } from 'luxon'
export default defineComponent({
  name: 'Albums',
  props: {
  },
  data() {
    return {
      isLoaded: false,
      albums: null as AlbumSimple[]|null,
    }
  },
  created() {
    albumsListFetch().then(albums => {
      this.albums = albums
      this.isLoaded = true
    })
  },
  computed: {
  },
  methods: {
    reprAlbumDateRange(album: AlbumSimple) {
      const earliestDate = album.earliest_date !== undefined ?
        DateTime.fromISO(album.earliest_date) :
        null
      const latestDate = album.latest_date !== undefined ?
        DateTime.fromISO(album.latest_date) :
        null
      if(earliestDate === null && latestDate === null) {
        return 'Unknown dates'
      }
      const earliestRepr = earliestDate !== null ?
        earliestDate.toLocaleString(DateTime.DATE_MED) :
        ''
      const latestRepr = latestDate !== null ?
        latestDate.toLocaleString(DateTime.DATE_MED) :
        ''
      return `${earliestRepr} - ${latestRepr}`

    }
  }
})
</script>

<style scoped>
</style>
