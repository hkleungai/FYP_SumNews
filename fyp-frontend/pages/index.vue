<template>
  <div v-if="$fetchState.pending">
    Loading...
  </div>
  <div v-else-if="$fetchState.error">
    Error while fetching. Please reload.
  </div>
  <div v-else>
    <div class="text-h6 mb-3">
      Top News
    </div>
    <v-img
      class="mx-n3"
      max-width="calc(100% + 24px)"
      :aspect-ratio="16 / 10"
      :src="topNews.img"
    >
      <div
        style="
          position: absolute;
          height: 100%;
          width: 100%;
          background: linear-gradient(
            180deg,
            rgba(0, 0, 0, 0) 0%,
            rgba(0, 0, 0, 0.7) 100%
          );
        "
      />
      <div
        class="text-subtitle-2"
        style="color: white; position: absolute; bottom: 12px; left: 12px"
      >
        <v-row no-gutters>
          <v-col cols="9">
            {{ topNews.title }}
          </v-col>
        </v-row>
      </div>
      <div style="color: white; position: absolute; bottom: 12px; right: 12px">
        <i class="material-icons">more_vert</i>
      </div>
    </v-img>
    <div class="pt-9">
      <div class="text-h6">
        Latest News
      </div>
      <news-list :news-list="latestNews" />
    </div>
  </div>
</template>

<script>
import NewsList from '~/components/NewsList'
import { NOT_FOUND_IMAGE_FOR_NEWS } from '~/constants'

export default {
  components: {
    NewsList
  },
  async fetch () {
    try {
      const { data: news } = await this.$axios.get('news?should_get_req_info_for_frontend=true')
      this.latestNews = news.map(({
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
      this.topNews = this.latestNews.reduce((previous, current) => (
        previous.views >= current.views ? previous : current
      ))
    } catch (error) {
      console.error(error) // eslint-disable-line no-console
    }
  },
  data () {
    return {
      latestNews: [],
      topNews: {}
    }
  },
  activated () {
    this.$fetchState.timestamp <= Date.now() - 60000 && this.$fetch()
  }
}
</script>
