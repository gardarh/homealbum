<template>
  <LoadingAnimation v-if="!isLoaded || album === null" />
  <div v-else>
    <div class="container">
      <div class="row">
        <div class="col-10">
          <h4>Album: {{ album.name }}</h4>
        </div>
        <div class="col-2">
          <router-link v-if="albumItemId === null" :to="{name: 'Albums'}">
            Albums list
          </router-link>
        </div>
      </div>
    </div>
    <div v-if="albumItemId !== null && album !== null">
      <LoadingAnimation v-if="albumItem === null" />
      <AlbumItem
        v-else
        :albumItem="albumItem"
        :album="album"
        :item-index="itemIndex"
        @go-to-prev="goToPrev"
        @go-to-next="goToNext"
        @exit-item-view="exitItemView"
      />
    </div>
    <ul v-show="albumItemId === null" class="thumb-grid list-unstyled">
      <li v-for="item in album.album_items" :key="item.id" :ref="setThumbRef">
        <Button
          button-style="link"
          @click="(evt) => albumItemClicked(evt, item)"
          >
          <img
            :src="`/thumbs/${item.media_file.substring(0, 2)}/${item.media_file}-${SMALL_THUMB_SIZE}.jpg`"
            class="img-thumbnail"
          />
        </Button>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { albumFetch, albumItemFetch } from '../utils/api'
import { Swipe } from '../utils/swipe'
import AlbumItem from '../components/AlbumItem.vue'
export default defineComponent({
  name: 'Album',
  components: {
    AlbumItem,
  },
  data() {
    return {
      isLoaded: false,
      album: null as Album|null,
      albumItem: null as AlbumItem|null,
      albumItemId: null as number|null,
      thumbRefs: [] as HTMLElement[],
      pendingScrollIndex: -1,
    }
  },
  created() {
    this.loadPage().then(() => {
      this.isLoaded = true
    })
  },
  mounted() {
    this.attachSwipe()
    this.attachKeyNavigation()
  },
  computed: {
    SMALL_THUMB_SIZE(): number {
      return 250
    },
    albumId(): number {
      const albumId = this.$route.params.albumId
      if(typeof albumId === 'string') {
        return parseInt(albumId)
      }
      throw `albumId from route invalid: ${albumId}`
    },
    /**
     * Get the index of the current albumItem within the album.
     */
    itemIndex(): number {
      if(this.albumItem === null || this.album === null) {
        return -1
      }
      return this.getAlbumIndexForId(this.albumItem.id)
    },
  },
  watch: {
      $route(){
        const albumItemId = typeof this.$route.params.albumItemId === 'string' ?
          parseInt(this.$route.params.albumItemId) :
          null

        if(albumItemId !== this.albumItemId) {
          this.isLoaded = false
          this.loadPage().then(() => {
            this.isLoaded = true
          })
        }
      }
  },
  methods: {
    loadPage(): Promise<void> {
      return albumFetch(this.albumId).then(album => {
        this.album = album
        const albumItemId = typeof this.$route.params.albumItemId === 'string' ?
          parseInt(this.$route.params.albumItemId) :
          null
        if(this.albumItemId !== null && albumItemId === null) {
          // Coming from "back" navigation. Dispatch exitItemView to scroll
          // to the item the user was viewing.
          this.exitItemView()
        } else {
          this.albumItemId = albumItemId
          this.loadAlbumItem()
        }
      })
    },
    attachSwipe(): void {
      const swiper = new Swipe(document.body);
      swiper.setOnLeft(() => {
        this.goToNext()
      })
      swiper.setOnRight(() => {
        this.goToPrev()
      })
    },
    attachKeyNavigation(): void {
      document.onkeydown = (e) => {
        e = e || window.event;
        switch(e.which || e.keyCode) {
          case 37: // left
            e.preventDefault(); // prevent the default action (scroll / move caret)
            this.goToPrev()
          break;

          case 39: // right
            e.preventDefault(); // prevent the default action (scroll / move caret)
            this.goToNext()
          break;
          default: return; // exit this handler for other keys
        }
      };
    },
    setThumbRef(el?: HTMLElement) {
      if (el) {
        this.thumbRefs.push(el)
      }
    },
    getAlbumIndexForId(itemId: number): number {
      return this.album !== null ?
        this.album.album_items.findIndex(albumItem => albumItem.id === itemId) :
        -1
    },
    goToAlbumItem(albumItemId: number|null): Promise<void> {
      this.albumItemId = albumItemId

      return this.loadAlbumItem().then(() => {
        if(albumItemId !== null) {
          this.$router.push({
            name: 'AlbumItem',
            params: {albumId: this.albumId, albumItemId: albumItemId}
          })
        } else {
          this.$router.push({
            name: 'Album',
            params: {albumId: this.albumId}
          })
        }
      })
    },
    albumItemClicked(event: PointerEvent, albumItem: AlbumItemSimple): void {
      event.preventDefault()
      this.goToAlbumItem(albumItem.id)
    },
    loadAlbumItem(): Promise<void> {
      this.albumItem = null
      if(this.albumItemId === null) {
        return Promise.resolve()
      }
      return albumItemFetch(this.albumId, this.albumItemId).then(albumItem => {
        this.albumItem = albumItem
      })
    },
    goToNext(): void {
      if(this.album === null || this.itemIndex === this.album.album_items.length - 1) {
        return
      }
      this.goToAlbumItem(this.album.album_items[this.itemIndex+1].id)
    },
    goToPrev(): void {
      if(this.album === null || this.itemIndex === 0) {
        return
      }
      this.goToAlbumItem(this.album.album_items[this.itemIndex-1].id)
    },
    exitItemView(): void {
      this.pendingScrollIndex = this.itemIndex
      this.goToAlbumItem(null)
    }
  },
  beforeUpdate() {
    this.thumbRefs = []
  },
  updated() {
    const thumbRef = this.thumbRefs[this.pendingScrollIndex]
    if(thumbRef) {
      thumbRef.scrollIntoView()
    }
    this.pendingScrollIndex = -1
  }
})
</script>

<style scoped>
.thumb-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 10px;
}
</style>