const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const sentenceSchema = new Schema({
  text: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
})

const articleSchema = new Schema({
  title: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    required: true,
  },
  date_added: {
    type: Date,
    required: true,
  },
  url: {
    type: String,
    required: true,
  },
  source: {
    type: String,
    default: '',
    // required: true,
  },
  photos_url: {
    type: [String],
    required: true,
  },
  is_grouped: {
    type: Boolean,
    required: true,
  },
  upvotes: {
    type: Number,
    default: 0,
  },
  downvotes: {
    type: Number,
    default: 0,
  },
  sentences: {
    type: [sentenceSchema],
    required: true,
  }
})

module.exports = mongoose.model('Article', articleSchema)
