<template>
  <div>
    <v-snackbar :bind="show" :bind:color="currentNotificationColor">
      <v-progress-circular v-if="showProgress" class="ma-2" :bind:indeterminate="showProgress" />
      {{ currentNotificationContent }}
      <v-btn @click.native="close">Закрыть</v-btn>
    </v-snackbar>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data() {
    return {
      show: false,
      text: '',
      showProgress: false,
      currentNotification: false
    }
  },
  computed: {
    ...mapGetters(['firstNotification']),
    currentNotificationContent() {
      return this.currentNotification && this.currentNotification.content || ''
    },
    currentNotificationColor() {
      return this.currentNotification && this.currentNotification.color || 'info'
    }
  },
  watch: {
    firstNotification: {
      handler(newNotification, oldNotification) {
        if (newNotification !== this.currentNotification) {
          this.setNotification(newNotification)
          if (newNotification) {
            this.$store.dispatch('removeNotification', { notification: newNotification, timeout: 6500 })
          }
        }
      },
      immediate: true
    }
  },
  methods: {
    async hide() {
      this.show = false
      await new Promise((resolve, reject) => setTimeout(() => resolve(), 500))
    },
    async close() {
      await this.hide()
      await this.removeCurrentNotification()
    },
    async removeCurrentNotification() {
      if (this.currentNotification) {
        this.$store.commit('commitRemoveNotification', this.currentNotification)
      }
    },
    async setNotification(notification) {
      if (this.show) {
        await this.hide()
      }
      if (notification) {
        this.currentNotification = notification
        this.showProgress = notification.showProgress || false
        this.show = true
      } else {
        this.currentNotification = false
      }
    }
  }
}
</script>
