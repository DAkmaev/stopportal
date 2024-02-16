<template>
  <v-main>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-card class="elevation-12">
            <v-toolbar dark color="primary">
              <v-toolbar-title>{{ appName }}</v-toolbar-title>
              <v-spacer />
            </v-toolbar>
            <v-card-text>
              <v-form @keyup.enter="submit">
                <v-text-field v-model="name" prepend-icon="mdi-account" name="login" label="Имя" type="text" @keyup.enter="submit" />
                <v-text-field id="password" v-model="password" prepend-icon="mdi-lock" name="password" label="Пароль" type="password" @keyup.enter="submit" />
              </v-form>
              <div v-if="logInError">
                <v-alert :value="logInError" transition="fade-transition" type="error">
                  Неверный логин или пароль
                </v-alert>
              </div>
              <!--  <v-flex class="caption text-xs-right"><router-link to="/recover-password">Забыли пароль?</router-link></v-flex>-->
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn @click.prevent="submit">Вход</v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-main>
</template>

<script>

import { mapActions, mapGetters } from 'vuex'

export default {
  data() {
    return {
      name: '',
      password: '',
      appName: process.env.VUE_APP_NAME || 'Stop Portal'
    }
  },
  computed: {
    ...mapGetters(['logInError'])
  },
  methods: {
    ...mapActions(['actionLogIn']),
    submit() {
      this.actionLogIn({ username: this.name, password: this.password })
    }
  }
}
</script>

<style>
</style>
