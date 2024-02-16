import Vue from 'vue'
import Vuex from 'vuex'
import router from '@/router'
import { getLocalToken, removeLocalToken, saveLocalToken } from '@/utils/localStorage'
import { endpoints, getData, sendFormData } from '@/api/invmos-back'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: '',
    isLoggedIn: null,
    logInError: false,
    userProfile: {
      is_superuser: false,
      is_active: false,
      id: null,
      name: null,
      password: null
    },
    notifications: []
  },
  getters: {
    userProfile: state => state.userProfile,
    token: state => state.token,
    isLoggedIn: state => state.isLoggedIn,
    logInError: state => state.logInError,
    hasAdminAccess: state => {
      return (
        state.userProfile &&
        state.userProfile.is_superuser && state.userProfile.is_active)
    },
    firstNotification: state => state.notifications.length > 0 && state.notifications[0]
  },
  mutations: {
    setToken(state, payload) {
      state.token = payload
    },
    setLoggedIn(state, payload) {
      state.isLoggedIn = payload
    },
    setLogInError(state, payload) {
      state.logInError = payload
    },
    setUserProfile(state, payload) {
      state.userProfile = payload
    },
    addNotification(state, payload) {
      state.notifications.push(payload)
    },
    removeNotification(state, payload) {
      state.notifications = state.notifications.filter((notification) => notification !== payload)
    }
  },
  actions: {
    async actionLogIn(context, { username, password }) {
      try {
        const response = await sendFormData(endpoints.LOGIN, { username, password })
        const token = response.access_token
        // const token = 'token'
        if (token) {
          saveLocalToken(token)
          context.commit('setToken', token)
          context.commit('setLoggedIn', true)
          context.commit('setLogInError', false)
          await context.dispatch('actionRouteLoggedIn')
          await context.dispatch('actionGetUserProfile')
          context.commit('addNotification', { content: 'Logged in', color: 'success' })
        } else {
          await context.dispatch('actionLogOut')
        }
      } catch (err) {
        context.commit('setLogInError', true)
        await context.dispatch('actionLogOut')
      }
    },
    async actionGetUserProfile(context) {
      try {
        const response = await getData(endpoints.ME, null, context.state.token)
        // const response = {
        //   data: {
        //     name: 'username',
        //     full_name: 'full name',
        //     id: 1,
        //     password: 'username@data.com',
        //     is_active: true,
        //     is_superuser: true
        //   }
        // }
        if (response) {
          context.commit('setUserProfile', response)
        }
      } catch (error) {
        await context.dispatch('actionCheckApiError', error)
      }
    },
    async actionLogOut(context) {
      await context.dispatch('actionRemoveLogIn')
      await context.dispatch('actionRouteLogOut')
      context.commit('addNotification', { content: 'Logged out', color: 'success' })
    },
    async actionCheckLoggedIn(context) {
      if (!context.state.isLoggedIn) {
        let token = context.state.token
        if (!token) {
          const localToken = getLocalToken()
          if (localToken) {
            context.commit('setToken', localToken)
            token = localToken
          }
        }
        if (token) {
          try {
            const response = await getData(endpoints.ME, null, context.state.token)
            // const response = {
            //   data: {
            //     name: 'username',
            //     full_name: 'full name',
            //     id: 1,
            //     email: 'username@data.com',
            //     is_active: true,
            //     is_superuser: true
            //   }
            // }
            context.commit('setLoggedIn', true)
            context.commit('setUserProfile', response)
          } catch (error) {
            await context.dispatch('actionRemoveLogIn')
          }
        } else {
          await context.dispatch('actionRemoveLogIn')
        }
      }
    },
    async actionRemoveLogIn({ commit }) {
      removeLocalToken()
      commit('setToken', '')
      commit('setLoggedIn', false)
    },
    async actionCheckApiError(context, payload) {
      // if (payload.response!.status === 401) {
      //   await dispatchLogOut(context);
      // }
      await context.dispatch('actionLogOut')
    },
    async actionRouteLoggedIn(context) {
      if (router.currentRoute.name === 'login' || router.currentRoute.name === 'root') {
        router.push('/home')
      }
    },
    async actionRouteLogOut(context) {
      if (router.currentRoute.name !== 'login') {
        router.push('/login')
      }
    },
    async removeNotification(context, payload) {
      return new Promise((resolve) => {
        setTimeout(() => {
          context.commit('removeNotification', payload.notification)
          resolve(true)
        }, payload.timeout)
      })
    }
  },
  modules: {}
})
