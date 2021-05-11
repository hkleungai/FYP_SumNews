<template>
  <div>
    <v-row align="center">
      <v-col cols="6">
        <v-subheader>
          Select News
        </v-subheader>
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="news"
          return-object
          item-text="_id"
          item-value="_id"
          :items="newsList"
          hide-details
          single-line
        />
      </v-col>
    </v-row>

    <v-row align="center">
      <v-col cols="6">
        <v-subheader>
          Select Articles
        </v-subheader>
      </v-col>
      <v-col cols="6">
        <v-select
          v-model="article"
          return-object
          item-text="_id"
          item-value="_id"
          :items="articles"
          hide-details
          single-line
        />
      </v-col>
    </v-row>
    <div class="d-flex align-center justify-center">
      <v-btn v-if="article" :href="article.url" rel="noopener noreferrer" target="_blank">
        link to article
      </v-btn>
    </div>
    <v-simple-table>
      <thead>
        <tr>
          <th class="text-center">
            Sentence
          </th>
          <th class="text-center">
            Common
          </th>
          <th class="text-center">
            Unique
          </th>
          <th class="text-center">
            Noise
          </th>
          <th class="text-center">
            None
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-if="sentences">
          <tr
            v-for="(sentence, n) in sentences"
            :key="sentence._id"
          >
            <td class="pa-4">
              {{ sentence.text }}
            </td>
            <td
              v-for="(responseType, i) in responseTypes"
              :key="`${sentence._id}-${i}`"
            >
              <v-radio-group v-model="sentences[n].label">
                <v-radio
                  :value="responseType"
                />
              </v-radio-group>
            </td>
          </tr>
        </template>
      </tbody>
    </v-simple-table>
    <v-dialog
      v-model="dialog"
      width="500"
    >
      <template v-slot:activator="{ attrs }">
        <v-btn
          class="mr-3 mt-3 mb-3"
          style="display: block; margin-left: auto;"
          v-bind="attrs"
          @click="putSentences"
        >
          Save
        </v-btn>
      </template>

      <v-card>
        <v-card-text class="text-h6 py-3">
          Feedback saved.
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-spacer />
          <v-btn
            color="primary"
            text
            @click="dialog = false"
          >
            Okay
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
div >>> .v-input--selection-controls__input {
  margin: auto;
}
</style>

<script>
export default {
  data () {
    return {
      newsList: [],
      news: null,
      article: null,
      responseTypes: [
        'common',
        'unique',
        'noise',
        'none'
      ],
      dialog: false
    }
  },
  computed: {
    articles () {
      return this.news ? this.news.articles : []
    },
    sentences () {
      return this.article ? this.article.sentences : []
    }
  },
  watch: {
    news () {
      this.article = null
    }
  },
  //  todo:
  async beforeMount () {
    const { data: result } = await this.$axios.get('/news/news-with-articles')
    this.newsList = result
  },
  methods: {
    //  todo
    async putSentences () {
      if (!this.article || !this.article._id || this.sentences.length === 0) {
        return
      }
      try {
        await this.$axios.put(
          `articles/${this.article._id}`,
          { sentences: this.sentences },
          { headers: { 'Content-Type': 'application/json' } }
        )
        this.dialog = true
      } catch (error) {
        // console.log(error)
      }
    }
  }
}
</script>
