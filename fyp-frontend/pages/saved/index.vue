<template>
  <div v-if="$fetchState.pending">
    Loading...
  </div>
  <div v-else-if="$fetchState.error">
    Error while fetching. Please reload.
  </div>
  <div v-else>
    <div class="text-h6">
      Saved News
    </div>
    <news-list :news-list="savedNews" />
  </div>
</template>

<script>
import NewsList from '~/components/NewsList'
import { NOT_FOUND_IMAGE_FOR_NEWS } from '~/constants'

export default {
  middleware: 'preventInvalidAccessToAuthenticatedPages',

  components: {
    NewsList
  },

  async fetch () {
    try {
      const { data: news } = await this.$axios.get(`users/${this.$auth.user._id}/saved-news`)
      this.savedNews = news.map(({
        summary: { top },
        articles: sources,
        update_datetime: updated,
        photos,
        view_count: views,
        _id
      }) => {
        const result = {
          _id,
          title: top[0],
          sources,
          updated,
          views
        }
        if (!photos.length) {
          return { ...result, img: NOT_FOUND_IMAGE_FOR_NEWS }
        }
        return { ...result, img: photos[Math.floor(Math.random() * photos.length)] }
      })
    } catch (error) {
      console.error(error) // eslint-disable-line no-console
    }
  },

  data () {
    return {
      savedNews: []
    }
  },

  activated () {
    this.$fetchState.timestamp <= Date.now() - 60000 && this.$fetch()
  }
}
</script>
