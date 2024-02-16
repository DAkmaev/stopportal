<template>
  <v-app id="inspire">
    <router-view />
    <NotificationManager />
  </v-app>
</template>

<script>
import NotificationManager from '@/components/NotificationManager.vue'
export default {
  name: 'App',
  components: { NotificationManager }
}
</script>
