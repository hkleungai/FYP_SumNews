<template>
  <div>
    <v-text-field
      v-model="searchText"
      solo
      label="Search news"
      class="rounded-pill"
      hide-details
      :append-icon="'search'"
      :prepend-icon="'clear'"
      @click:append="onSearch"
      @click:prepend="clearSearchText"
    />
    <div v-if="!hasStartSearching">
      Results will be displayed here
    </div>
    <div v-else>
      <div v-if="$fetchState.pending">
        Loading...
      </div>
      <div v-else-if="$fetchState.error">
        Error while fetching. Please reload.
      </div>
      <div v-else>
        <div class="my-3 d-flex justify-space-between align-center">
          <div class="text-caption" style="height: 1.25rem">
            {{ searchedNews.length }} Search results
          </div>
          <v-icon class="clickable--text">
            filter_list
          </v-icon>
        </div>
        <div class="text-h6">
          News
        </div>
        <news-list :news-list="searchedNews" />
      </div>
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
      if (!this.searchText) {
        return
      }
      if (!this.hasStartSearching) {
        this.hasStartSearching = true
      }
      const { data: news } = await this.$axios.get(`search/${this.searchText}`)
      this.searchedNews = news.map(({
        summary: { top },
        articles: sources,
        update_datetime: updated,
        photos,
        _id
      }) => {
        const result = {
          _id,
          title: top[0],
          sources,
          updated
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
      hasStartSearching: false,
      searchText: '',
      searchedNews: [],
      users: [
        {
          img:
            'https://www.whitehouse.gov/wp-content/uploads/2021/01/45_donald_trump.jpg',
          following: true,
          name: 'RealDonaldTrump'
        },
        {
          img:
            'https://www.whitehouse.gov/wp-content/uploads/2021/01/45_donald_trump.jpg',
          following: false,
          name: 'FakeDonaldTrump'
        }
      ]
    }
  },
  activated () {},
  methods: {
    clearSearchText () {
      if (!this.searchText) {
        return
      }
      this.searchText = ''
    },

    async onSearch () {
      if (!this.searchText) {
        return
      }
      await this.$fetch()
    }
  }
}
</script>
