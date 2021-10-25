<template>
  <div :class="divClass"><slot /></div>
</template>
<script lang="ts">
import { defineComponent, PropType } from 'vue'
export default defineComponent({
  name: 'Message',
  props: {
    variant: {
      type: String as PropType<MessageVariant>,
      default: 'info'
    },
  },
  computed: {
    divClass(): {[className: string]: boolean} {
      const out: {[className: string]: boolean} = {
        message: true,
      }
      if(this.variant == 'error') {
        out['message-error'] = true
      } else if(this.variant === 'warning') {
        out['message-warning'] = true
      } else if(this.variant === 'info') {
        out['message-info'] = true
      } else if(this.variant === 'success') {
        out['message-success'] = true
      }
      return out
    }
  }
})
</script>
<style scoped type="less">
.message {
  padding: 8px;
}
.message-error {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.message-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
}

.message-info {
  background-color: #d1ecf1;
  border: 1px solid #bee5eb;
}

.message-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
}



</style>