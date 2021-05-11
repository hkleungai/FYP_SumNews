<template>
  <v-app light>
    <v-main class="pa-3 pb-6 mb-14">
      <nuxt keep-alive />
    </v-main>
    <v-bottom-navigation :value="activeBtn" grow app color="#000">
      <v-btn style="height: inherit; background-color: transparent" nuxt to="/">
        <i
          :class="
            $route.path === '/' ? 'material-icons' : 'material-icons-outlined'
          "
        >
          home
        </i>
      </v-btn>
      <v-btn
        style="height: inherit; background-color: transparent"
        nuxt
        to="/search"
      >
        <i
          :class="[
            $route.path === '/search' ? 'font-weight-black' : '',
            'material-icons',
          ]"
        >
          search
        </i>
      </v-btn>

      <v-btn
        style="height: inherit; background-color: transparent"
        @click="drawer = !drawer"
      >
        <i :class="['material-icons']">
          account_circle
        </i>
      </v-btn>
    </v-bottom-navigation>

    <v-navigation-drawer v-model="drawer" fixed temporary right app>
      <div v-if="$auth.loggedIn" class="pt-6 px-6">
        <i :class="['material-icons']" style="font-size: 48px">
          account_circle
        </i>
        <div class="text-h5 mt-1">
          {{ $auth.user.name || 'Anonymous' }}
        </div>
        <div class="text-subtitle-2 mt-1 mb-2 grey--text text--lighten-1">
          {{ $auth.user.email || 'Anonymous' }}
        </div>
      </div>
      <v-list dense>
        <v-list-item
          v-for="item in items"
          :key="item.title"
          class="px-6"
          nuxt
          :to="item.to"
          @click="item.click && item.click()"
        >
          <v-list-item-icon class="mr-3">
            <i class="material-icons clickable--text">
              {{ item.icon }}
            </i>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title
              class="text-button clickable--text"
              style="text-transform: capitalize !important"
            >
              {{ item.title }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </v-app>
</template>

<script>
export default {
  data () {
    return {
      drawer: null,
      activeBtn: 1
    }
  },

  computed: {
    items () {
      return this.$auth.loggedIn
        ? [
          { title: 'Saved News', icon: 'bookmark_border', to: '/saved' },
          { title: 'Logout', icon: 'logout', to: '/', click: this.logout }
        ]
        : [
          { title: 'Register', icon: 'account_box', to: '/register' },
          { title: 'Login', icon: 'login', to: '/login' }
        ]
    }
  },

  methods: {
    async logout () {
      try {
        const { _id: userId } = this.$auth.user
        userId && await this.$axios.post('users/logout', { userId })
        await this.$auth.logout()
      } catch (error) {
        console.error(error) // eslint-disable-line no-console
      }
    }
  }
}
</script>
