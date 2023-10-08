<template>
  <v-app id="inspire">
    <v-navigation-drawer
      v-model="drawer"
      :clipped="$vuetify.breakpoint.lgAndUp"
      app
      fixed
    >
      <v-list dense>
        <template v-for="item in menu">
          <v-row v-if="item.heading" :key="item.heading" align="center">
            <v-col cols="6">
              <v-subheader v-if="item.heading">
                {{ item.heading }}
              </v-subheader>
            </v-col>
          </v-row>
          <v-list-group
              v-else-if="item.children"
              :key="item.title"
              v-model="item.model"
              :prepend-icon="item.model ? item.icon : item['icon-alt']"
              append-icon="mdi-menu-down"
          >
            <template v-slot:activator>
              <v-list-item-content>
                <v-list-item-title>
                  {{ item.title }}
                </v-list-item-title>
              </v-list-item-content>
            </template>
            <v-list-item
                v-for="(child, i) in item.children"
                :key="i"
                link
                :to="child.name ? { name: child.name } : null"
                :href="child.name"
                style="padding-left: 4.5em"
            >
              <v-list-item-action v-if="child.icon">
                <v-icon>{{ child.icon }}</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title>
                  {{ child.title }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-group>
          <v-list-item
              v-else
              :key="item.title"
              link
              :to="item.name ? { name: item.name } : null"
              :href="item.name"
          >
            <v-list-item-action>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                {{ item.title }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar
      :clipped-left="$vuetify.breakpoint.lgAndUp"
      app
      color="blue darken-3"
      dark
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title style="width: 300px" class="ml-0 pl-4">
        <span class="hidden-sm-and-down">InvMos</span>
      </v-toolbar-title>
      <v-text-field
        flat
        solo-inverted
        hide-details
        prepend-inner-icon="mdi-magnify"
        label="Поиск"
        class="hidden-sm-and-down"
      />
      <v-spacer />
      <v-btn icon>
        <v-icon>mdi-apps</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-bell</v-icon>
      </v-btn>
      <v-btn icon large>
        <v-avatar size="32px" item>
          <v-img
              src="https://cdn.vuetifyjs.com/images/logos/logo.svg"
              alt="Vuetify"
          /></v-avatar>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="grey lighten-5">
        <v-row class="align-center px-5 pt-4 app--page-header">
          <div class="page-header-left">
            <h3 class="pr-3">{{ title }}</h3>
          </div>
          <v-breadcrumbs divider="-" :items="breadcrumbs" />
          <v-spacer />
          <!--<div class="page-header-right">
            <v-btn class="mx-2" fab outlined color="primary">
              <v-icon dark>mdi-refresh</v-icon>
            </v-btn>
          </div>-->
        </v-row>
      </v-container>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import menu from '@/api/menu'
export default {
  name: 'App',
  components: {},
  props: {
    source: {
      type: String,
      default: undefined
    }
  },
  data: () => ({
    title: '',
    dialog: false,
    drawer: null,
    menu: menu
  }),
  computed: {
    breadcrumbs: function() {
      const breadcrumbs = []
      menu.forEach(item => {
        if (item.children) {
          const child = item.children.find(i => {
            return i.name === this.$route.name
          })
          if (child) {
            breadcrumbs.push(item.title)
            breadcrumbs.push(child.title)
            this.title = child.title
          }
        } else {
          if (item.name === this.$route.name) {
            this.title = item.title
            breadcrumbs.push(item.title)
          }
        }
      })
      return breadcrumbs
    }
  }
}
</script>
