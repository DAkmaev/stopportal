<template>
  <router-view />
</template>

<script>
import store from '@/store'

const startRouteGuard = async(to, from, next) => {
  await store.dispatch('actionCheckLoggedIn')
  if (store.getters.isLoggedIn) {
    if (to.name === 'login' || to.name === 'root') {
      next('home')
    } else {
      next()
    }
  } else if (store.getters.isLoggedIn === false) {
    if (to.name === 'root' || to.path.toString().startsWith('/home')) {
      next('/login')
    } else {
      next()
    }
  }
}

import { mapActions, mapGetters } from 'vuex'
export default {
  name: 'Start',
  beforeRouteEnter(to, from, next) {
    startRouteGuard(to, from, next)
  },
  beforeRouteUpdate(to, from, next) {
    startRouteGuard(to, from, next)
  },
  computed: {
    ...mapGetters(['isLoggedIn'])
  },
  methods: {
    ...mapActions(['actionCheckLoggedIn'])
  }
}
</script>

<style scoped>

</style>
