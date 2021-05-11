const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const newsGroupSchema = new Schema({
  articles: {
    type: [{
      type: Schema.Types.ObjectId,
      ref: 'Article',
    }],
    required: true,
  },
  summary: {
    top: {
      type: [String],
      required: true,
    },
    originals: {
      type: Map,
      of: [String],
      required: true,
    },
  },
  photos: {
    type: [String],
    required: true,
  },
  creation_datetime: {
    type: Date,
    required: true,
  },
  update_datetime: {
    type: Date,
    required: true,
  },
  vector: {
    type: [Number],
    required: true,
  },
  related_news_groups: {
    type: [{
      type: Schema.Types.ObjectId,
      ref: 'NewsGroup',
    }],
  },
  // comments: {
  //   type: [{
  //     type: Schema.Types.ObjectId,
  //     ref: 'Comment',
  //   }],
  //   required: true,
  // },
  view_count: {
    type: Number,
    default: 0,
  },
  // most_positive_comment: {
  //   type: Schema.Types.ObjectId,
  //   ref: 'Comment',
  // },
  // most_negative_comment: {
  //   type: Schema.Types.ObjectId,
  //   ref: 'Comment',
  // },
})

module.exports = mongoose.model('NewsGroup', newsGroupSchema)
