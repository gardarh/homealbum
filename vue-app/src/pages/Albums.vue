<template>
  <h1 class="text-center">Albums</h1>
  <LoadingAnimation v-if="!isLoaded" />
  <div v-else>
    <div v-for="albumYear in albumsListByYear" :key="albumYear.year">
      <h3>{{albumYear.year}}</h3>
      <ul class="list-unstyled">
        <li v-for="album in albumYear.albums" :key="album.id">
          <router-link :to="{
              name: 'Album',
              params: {albumId: album.id}
          }">{{ album.name }}</router-link>
          ({{ reprAlbumDateRange(album)}})
        </li>
      </ul>
    </div>
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
    albumsListByYear(): AlbumsForYear[] {
      if(this.albums === null) {
        return []
      }
      const yearMap: {[year: string]: {year: string, albums: AlbumSimple[]}} = {}
      for(const album of this.albums) {
        const albumYear = album.latest_date !== null ?
          String(DateTime.fromISO(album.latest_date).year) :
          'Unknown time'
        if(yearMap[albumYear] === undefined) {
          yearMap[albumYear] = {year: albumYear, albums: []}
        }
        yearMap[albumYear].albums.push(album)
      }
      const years = Array.from(Object.keys(yearMap))
      const parseYear = (year: string) => isNaN(parseInt(year)) ? 0 : parseInt(year)
      years.sort((a, b) => parseYear(b) - parseYear(a))
      return years.map(year => yearMap[year])
    }
  },
  methods: {
    reprAlbumDateRange(album: AlbumSimple) {
      const earliestDate = album.earliest_date !== null ?
        DateTime.fromISO(album.earliest_date) :
        null
      const latestDate = album.latest_date !== null ?
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
interface AlbumsForYear {
  year: string
  albums: AlbumSimple[]
}
</script>

<style scoped>
</style>
