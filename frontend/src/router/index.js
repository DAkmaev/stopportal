import Vue from 'vue'
import VueRouter from 'vue-router'
import paths from './paths'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

Vue.use(VueRouter)

const router = new VueRouter({
  base: '/',
  mode: 'hash',
  linkActiveClass: 'active',
  routes: paths
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
