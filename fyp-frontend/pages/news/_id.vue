<template>
  <div
    class="ma-n3 mb-n6"
    style="
      display: grid;
      grid-template-rows: 1fr auto;
      height: calc(100% - 56px);
      width: 100%;
      position: fixed;
    "
  >
    <div class="pa-3 pb-6" style="min-width: 0; overflow: auto">
      <client-only>
        <swiper class="ml-n3 mr-n3 mt-n3">
          <swiper-slide
            v-for="(photo, i) in photos"
            :key="i"
            style="max-width: 100%"
          >
            <v-img
              class="mx-n3 mt-n3"
              :aspect-ratio="16 / 10"
              width="calc(100% + 24px)"
              :src="photo"
            />
          </swiper-slide>
        </swiper>
      </client-only>
      <div class="mt-12 text-h6">
        News Summary
      </div>
      <div v-swiper:myDirectiveSwiper="swiperOptions" class="swiper">
        <div class="swiper-wrapper">
          <div v-for="(title, i) in news.titles" :key="i" class="swiper-slide">
            <div class="ma-4 text-justify">
              {{ title }}
            </div>
          </div>
        </div>
        <div slot="button-prev" class="swiper-button-prev primary--text" />
        <div slot="button-next" class="swiper-button-next primary--text" />
      </div>
      <div class="text-caption mt-2 mb-n3 d-flex align-center">
        Last Updated
        <div class="ml-1">
          {{ moment(news.updatedAt).format("YYYY/MM/DD") }}
        </div>
        <div class="d-flex align-center ml-5">
          <i class="material-icons-outlined" style="font-size: 14px">
            visibility
          </i>
          {{ news.views }}
        </div>
      </div>
      <div class="mt-12 text-h6">
          Unique Sentences Extracted from Each Source
      </div>
      <div v-for="(article, i) in news.articles" :key="i" class="mt-9">
        <div class="text-subtitle-2 d-flex">
          <div>{{ article.source }}</div>
          <div class="ml-6">
            {{ moment(article.date).format("YYYY/MM/DD") }}
          </div>
        </div>
        <div
          style="
            line-height: 155%;
            letter-spacing: 0.5px;
            text-align: justify;
            white-space: pre-line;
          "
        >
          {{ article.text }}
        </div>
        <div
          class="mt-3 d-flex align-center mx-auto clickable--text"
          style="width: fit-content"
        >
          <div class="d-flex flex-column align-center">
            <i class="material-icons-outlined green--text"> check_circle </i>
            <div class="mt-2" :style="voteStyle">
              {{ article.upvotes }}
            </div>
          </div>
          <div class="mx-12 d-flex flex-column align-center">
            <i class="material-icons red--text"> not_interested </i>
            <div class="mt-2" :style="voteStyle">
              {{ article.downvotes }}
            </div>
          </div>
          <div>
            <a
              :href="
                article.url +
                  '#:~:text=' +
                  article.text.split('\n')[0] +
                  '&text=' +
                  article.text.split('\n')[1]
              "
              target="_blank"
              rel="noopener"
            >
              <i class="material-icons"> launch </i>
            </a>
          </div>
        </div>
      </div>
      <template v-if="news.related && news.related.length">
        <div class="mt-12 text-h6">
          You might be interested in...
        </div>
        <news-list :news-list="news.related" />
      </template>
      <div class="text-h6 mt-9 mb-3">
        Comments
      </div>
      <div class="d-flex justify-space-between align-center mb-3">
        <div class="text-caption">
          {{ fetchedComments.length }} Comments
        </div>
        <div
          class="d-flex align-center"
          style="flex: 0 0 158px; margin-right: -6px"
        >
          <div class="text-caption mr-2" style="flex: 0 0 42px">
            Sort By
          </div>
          <v-select
            v-model="sortCommentsBy"
            dense
            solo
            :items="sortOptions"
            item-text="label"
            item-value="value"
            hide-details
            return-object
            single-line
          />
        </div>
      </div>
      <comment
        v-for="(cm, i) in fetchedComments"
        :key="'comment' + i"
        class="pt-3"
        :comment="cm"
      >
        <!-- <comment
          v-for="(reply, j) in cm.replies"
          :key="'reply' + j"
          :comment="reply"
          :is-replying-comment="true"
        /> -->
      </comment>
      <v-btn class="mx-auto mt-3" style="display: block;" @click="$nuxt.refresh()">
        <i class="material-icons">
          refresh
        </i>
      </v-btn>
    </div>
    <div v-if="$auth.user" style="">
      <!-- width: 100%; position: fixed; bottom: 56px; left: 0px; -->
      <v-textarea
        v-model="commentInput"
        solo
        :rows="1"
        auto-grow
        hide-details
        name="commentInput"
        label="Comment as ..."
        append-icon="send"
        @click:append="getNewestComments"
      >
        <template #prepend-inner>
          <i :class="['material-icons']" style="font-size: 28px">
            account_circle
          </i>
        </template>
      </v-textarea>
    </div>
  </div>
</template>

<style scoped>
.swiper {
  width: 100%;
  padding-top: 12px;
  padding-bottom: 12px;
}

.swiper-wrapper {
  align-items: stretch;
}

.swiper-slide {
  width: 55%;
  max-width: 300px;
  height: initial;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: rgba(0, 0, 0, 0.16) 0px 3px 6px, rgba(0, 0, 0, 0.23) 0px 3px 6px;
  border-radius: 12px;
}

#__layout .v-select >>> .v-input__slot,
#__layout .v-select {
  height: 20px;
  min-height: 20px;
  box-shadow: initial;
  padding: 0;
}
#__layout .v-select >>> .v-select__selections {
  font-size: 16px;
  color: #666;
}
#__layout .v-select >>> .v-select__selection--comma {
  margin-top: 2px;
  color: #666;
}
#__layout .v-textarea >>> textarea {
  margin-bottom: 10px;
  padding-left: 12px;
  max-height: 5.25rem;
  overflow: auto;
}
#__layout .v-text-field >>> .v-text-field__slot label {
  left: 12px !important;
}
</style>

<script>
import moment from 'moment'
import NewsList from '~/components/NewsList'
import Comment from '~/components/Comment'
import { NOT_FOUND_IMAGE_FOR_NEWS } from '~/constants'

export default {
  components: {
    NewsList,
    Comment
  },
  async asyncData ({ params: { id }, redirect, app }) {
    try {
      const {
        data: {
          articles,
          summary,
          update_datetime: updatedAt,
          related_news_groups: related,
          view_count: views
        }
      } = await app.$axios.get(`news/${id}/populated`)
      const { data: comments } = await app.$axios.get(`comments/${id}`)
      return {
        news: {
          titles: summary.top,
          updatedAt,
          views,
          related: related.map(({
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
              updated,
              photos
            }
            if (!photos.length) {
              return { ...result, img: NOT_FOUND_IMAGE_FOR_NEWS }
            }
            return { ...result, img: photos[Math.floor(Math.random() * photos.length)] }
          }),
          articles: articles.map(
            ({
              source,
              upvotes,
              downvotes,
              url,
              date_added: date,
              photos_url: photos,
              _id
            }) => ({
              source,
              date,
              text: (summary.originals[_id] || []).join('\n'),
              upvotes,
              downvotes,
              url,
              photo: photos.length ? photos[Math.floor(Math.random() * photos.length)] : NOT_FOUND_IMAGE_FOR_NEWS
            })
          )
        },
        fetchedComments: comments || []
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error({ error })
      return redirect('/')
    }
  },
  data () {
    return {
      sortCommentsBy: 'date',
      sortOptions: [
        { label: 'Popularity', value: 'popularity' },
        { label: 'Date', value: 'date' }
      ],
      voteStyle: 'font-size: 12px; font-weight: bold;',
      moment,
      commentInput: '',
      fetchedComments: [],
      news: {},
      swiperOptions: {
        slidesPerView: 'auto',
        centeredSlides: true,
        spaceBetween: 24,
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev'
        }
      }
    }
  },
  computed: {
    photos () {
      if (!this.news.articles.length) {
        return []
      }
      return this.news.articles.map(({ photo }) => photo)
    }
  },
  methods: {
    async getNewestComments () {
      try {
        if (!this.commentInput) {
          return
        }
        const newsId = this.$route.params.id
        const authorId = this.$auth.user._id
        await this.$axios.post(`comments/${newsId}`, { authorId, comment: this.commentInput })
        const { data: newComments } = await this.$axios.get(`comments/${this.$route.params.id}`)
        this.fetchedComments = newComments || []
        this.commentInput = ''
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error)
      }
    }
  }
}
</script>
