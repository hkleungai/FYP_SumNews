const express = require('express');
const router = express.Router();

// const language = require('@google-cloud/language');
// const client = new language.LanguageServiceClient();

const Comment = require('../models/Comment');

router.post('/:newsId', async ({
  body: { authorId, comment },
  params: { newsId },
}, res, next) => {
  try {
    /* No google service available at this point */
    // const [result] = await client.analyzeSentiment({
    //   document: { content: comment, type: 'PLAIN_TEXT' },
    // });
    // const sentiment = result.documentSentiment.score;
    const sentiment = null;
    await Comment.create({
      news: newsId,
      author: authorId,
      content: comment,
      sentiment,
    });
    res.setHeader('Content-Type', 'application/json');
    res.json({
      comment,
      sentiment,
    });
  } catch (error) {
    next(error);
  }
});

router.get('/:newsId', async ({
  params: { newsId },
}, res, next) => {
  try {
    const comment_list = (
      await Comment
        .find({ news: newsId })
        .sort({ date: 'descending' })
        .populate('author', 'name')
    );
    res.setHeader('Content-Type', 'application/json');
    res.json(comment_list);
  } catch (error) {
    next(error);
  }
});

router.put('/:commentId', async ({
  body,
  params: { commentId },
  query: {
    should_increase_upvotes,
    should_decrease_upvotes,
    should_increase_downvotes,
    should_decrease_downvotes,
  },
}, res, next) => {
  try {
    const update = {};
    if (body && Object.keys(body).length) {
      update.$set = body
    }
    if (should_increase_upvotes) {
      update.$inc = { upvotes: 1 }
    }
    if (should_decrease_upvotes) {
      update.$inc = { upvotes: -1 }
    }
    if (should_increase_downvotes) {
      update.$inc = { downvotes: 1 }
    }
    if (should_decrease_downvotes) {
      update.$inc = { downvotes: -1 }
    }
    const comment = await Comment.findByIdAndUpdate(commentId, update, { new: true })
    res.setHeader('Content-Type', 'application/json')
    res.json(comment);
  } catch (error) {
    next(error);
  }
});

router.delete('/:commentId', async ({
  params: { commentId },
}, res, next) => {
  try {
    const comment = await Comment.findByIdAndRemove(commentId);
    res.setHeader('Content-Type', 'application/json');
    res.json(comment);
  } catch (error) {
    next(error);
  }
});

module.exports = router;
