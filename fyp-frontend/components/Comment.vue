<template>
  <div :class="{'mt-3': isReplyingComment}" style="display: grid; grid-template-columns: 60px 1fr;">
    <div class="d-flex justify-space-between">
      <div style="height: 48px; width: 4px; background-color: rgba(0,0,0,20%)" />
      <div>
        <i
          :class="['material-icons']"
          :style="`font-size: ${isReplyingComment ? '44px' : '60px'}`"
        >
          account_circle
        </i>
      </div>
    </div>
    <div class="pl-3" style="min-width: 0;">
      <v-card
        outlined
        width="100%"
      >
        <div class="px-3 py-2">
          <div class="text-subtitle-2 d-flex">
            <div class="clickable--text">
              {{ comment.author.name }}
            </div>
            <div class="ml-3 black-text text--disabled">
              {{ moment(comment.date).format('YYYY/MM/DD HH:mm:ss') }}
            </div>
          </div>
          <div class="text-body-1 text--primary my-3" style="white-space: pre-line;">
            {{ comment.content }}
          </div>
          <div class="d-flex flex-wrap clickable--text font-weight-bold" style="font-size: 10px">
            <div class="d-flex align-center">
              <span class="icon-long-arrow-up" style="font-size: 15px;" />
              <div class="ml-2">
                {{ comment.upvotes }}
              </div>
            </div>
            <div class="d-flex align-center mx-6">
              <span class="icon-long-arrow-down" style="font-size: 15px;" />
              <div class="ml-2">
                {{ comment.downvotes }}
              </div>
            </div>
            <div class="d-flex align-center">
              <span class="material-icons" style="font-size: 15px;">
                reply
              </span>
              <div class="ml-2">
                {{ !isReplyingComment ? comment && comment.replies && comment.replies.length : '' }}
              </div>
            </div>
          </div>
        </div>
      </v-card>
      <slot />
    </div>
  </div>
</template>

<script>
import moment from 'moment'

export default {
  props: {
    comment: {
      type: Object,
      required: true
    },
    isReplyingComment: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      moment
    }
  }
}
</script>
