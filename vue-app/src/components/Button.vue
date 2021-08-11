<template>
  <button :class="buttonClass"><slot /></button>
</template>
<script lang="ts">
import { defineComponent, PropType } from 'vue'
export default defineComponent({
  name: 'Button',
  props: {
    buttonStyle: {
      type: String as PropType<ButtonStyle>,
      default: 'default'
    },
  },
  computed: {
    buttonClass(): {[className: string]: boolean} {
      const out: {[className: string]: boolean} = {
        btn: true,
        'btn-sm': true,
      }
      if(this.buttonStyle == 'link') {
        out['btn-link'] = true
      } else if(this.buttonStyle === 'default') {
        out['btn-primary'] = true
      } else if(this.buttonStyle === 'outline') {
        out['btn-outline-dark'] = true
      }
      return out
    }
  }
})
</script>
<style scoped>
</style>