<template>
  <div>
    <div class="container mb-1">
      <div class="row">
        <div class="col-4 d-flex justify-content-left">
          <Button
            v-if="allowPrevNavigation"
            @click="goToPrev"
            button-style="outline"
          >Prev</Button>
        </div>
        <div class="col-4 d-flex justify-content-center">
          <Button @click="exitItemView" button-style="outline">Back to album</Button>
        </div>
        <div class="col-4 d-flex justify-content-end">
          <Button
            v-if="allowNextNavigation"
            @click="goToNext"
            button-style="outline"
          >Next</Button>
        </div>
      </div>
    </div>
    <div class="mb-1">
        <div class="px-0">
          <img
            :src="`/thumbs/${mediaFile.substring(0, 2)}/${mediaFile}-${LARGE_THUMB_SIZE}.jpg`"
            class="img-fluid"
          />
        </div>
    </div>
    <div class="mb-2">
      <small>
        Shot on: {{ albumItemDateRepr }}
      </small>
    </div>
    <Button
      @click="() => displayExifData = !displayExifData"
      button-style="outline"
      class="mx-2"
    >
      <span v-if="displayExifData">Hide details</span>
      <span v-else>Show details</span>
    </Button>
    <a :href="srcUrl" class="mx-2 btn btn-sm btn-outline-dark">Original</a>
    <a v-if="albumItem.raw_url" :href="albumItem.raw_url" class="mx-2 btn btn-sm btn-outline-dark">Raw</a>
    <transition name="fade">
      <div v-if="displayExifData" class="mx-2">
        <table class="table">
          <thead>
            <tr>
              <th scope="col">Attribute</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="exif.f_number">
              <td>
                Aperture
              </td>
              <td>
                {{ exif.f_number }}
              </td>
            </tr>
            <tr v-if="exif.exposure_time">
              <td>
                Exposure time
              </td>
              <td>
                {{ exif.exposure_time }}
              </td>
            </tr>
            <tr v-if="exif.iso && exif.iso">
              <td>
                ISO
              </td>
              <td>
                {{ exif.iso }}
              </td>
            </tr>
            <tr v-if="exif.make && exif.model">
              <td>
                Make/Model
              </td>
              <td>
                {{ exif.make }} {{ exif.model }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </transition>
  </div>
</template>
<script lang="ts">
import { defineComponent, PropType } from 'vue'
import { DateTime } from 'luxon'
const ORIGINALS_URL = '/originals'
export default defineComponent({
  name: 'AlbumItem',
  props: {
    albumItem: {
      type: Object as PropType<AlbumItem>,
      required: true,
    },
    album: {
      type: Object as PropType<Album>,
      required: true,
    },
    /**
     * itemIndex indicates where within the album this albumItem is.
     */
    itemIndex: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      displayExifData: false,
    }
  },
  methods: {
    goToPrev(evt: Event): void {
      evt.preventDefault()
      this.$emit('go-to-prev')
    },
    goToNext(evt: Event): void {
      evt.preventDefault()
      this.$emit('go-to-next')
    },
    exitItemView(evt: Event): void {
      evt.preventDefault()
      this.$emit('exit-item-view')
    },
  },
  computed: {
    LARGE_THUMB_SIZE(): number {
      return 1200
    },
    srcUrl(): string {
      return `${ORIGINALS_URL}/${this.albumItem.file_location}`
    },
    mediaFile(): string {
      return this.albumItem.media_file
    },
    allowPrevNavigation(): boolean {
      return this.itemIndex > 0
    },
    allowNextNavigation(): boolean {
      return this.itemIndex < this.album.album_items.length - 1
    },
    exif(): ExifData|null {
      return this.albumItem.media_file_item.exif_data
    },
    albumItemDateRepr(): string|null {
      if(this.exif === null || this.exif.date === null) {
        return null
      }
      const date = DateTime.fromISO(this.exif.date)
      return date.toLocaleString(DateTime.DATETIME_MED);
    }
  }
})
</script>
<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>