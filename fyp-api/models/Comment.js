const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const commentSchema = new Schema({
  content: {
    type: String,
    required: true,
  },

  sentiment: {
    type: Number,
    default: null,
  },

  date: {
    type: Date,
    default: Date.now,
    required: true,
  },

  author: {
    type: Schema.Types.ObjectId,
    required: true,
    ref: 'User',
  },

  news: {
    type: Schema.Types.ObjectId,
    required: true,
    ref: 'NewsGroup',
  },

  upvotes: {
    type: Number,
    default: 0,
  },

  downvotes: {
    type: Number,
    default: 0,
  },
});

module.exports = mongoose.model("Comment", commentSchema);
