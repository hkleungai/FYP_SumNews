const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const userSchema = new Schema({
  name: {
    type: String,
    required: true,
  },

  email: {
    type: String,
    required: true,
  },

  password: {
    type: String,
    required: true,
  },

  is_logged_in: {
    type: Boolean,
    default: false,
  },

  // Not in frontend yet
  icon: {
    type: { data: Buffer, contentType: String },
    default: {},
  },

  // Not in frontend yet
  comments: {
    type: [{
      type: Schema.Types.ObjectId,
      ref: 'Comment',
    }],
    default: [],
  },

  saved_news: {
    type: [{
      type: Schema.Types.ObjectId,
      ref: 'NewsGroup',
    }],
    default: [],
  },

  // Not in frontend yet
  viewed_articles: {
    type: [{
      type: Schema.Types.ObjectId,
      ref: 'Article',
    }],
    default: [],
  },
});

module.exports = mongoose.model('User', userSchema);
