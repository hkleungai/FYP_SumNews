<template>
  <div>
    <div v-if="newsList.length === 0">
      No news available in this page currently. Please come back later
    </div>
    <v-row v-for="news in newsList" v-else :key="news._id" no-gutters class="py-3 align-center">
      <v-col cols="5" class="pr-1">
        <nuxt-link :to="`/news/${news._id}`">
          <v-img :aspect-ratio="16/9" :src="news.img" />
        </nuxt-link>
      </v-col>
      <v-col cols="7" class="pl-1" style="position: relative;">
        <nuxt-link :to="`/news/${news._id}`" class="subtitle-2 clickable--text" style="cursor: pointer; text-decoration: none; display: block;">
          {{ news.title }}
        </nuxt-link>
        <div class="text-caption mt-3 grey--text pr-6">
          {{ news.sources.length }} News Sources
        </div>
        <div class="text-caption grey--text pr-6">
          Updated: {{ moment(news.updated).format('YYYY/MM/DD-HH:mm') }}
        </div>
        <v-btn
          v-if="$route.path !== '/saved' && $auth.loggedIn"
          style="position: absolute; bottom: 0px; right: 0px;"
          @click="saveNews(news._id)"
        >
          <i class="material-icons clickable--text">bookmark_border</i>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import moment from 'moment'

export default {
  props: {
    newsList: {
      type: Array,
      required: true
    }
  },

  data () {
    return {
      moment
    }
  },

  methods: {
    async saveNews (newsId) {
      await this.$axios.post(
        '/users/saved-news',
        { newsId, userId: this.$auth.user._id }
      )
    }
  }
}
</script>
