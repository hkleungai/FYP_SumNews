const express = require('express');
const router = express.Router();

const Article = require('../models/Article')

router.get('/', ({
  query: {
    should_get_id_only,
    should_get_url_only,
    should_get_features_for_preprocessing,
    ...articleQuery
  }
}, res, next) => {
  const projection =
    should_get_id_only
      ? ''
      : should_get_url_only
        ? 'url'
        : should_get_features_for_preprocessing
          ? 'title text date_added'
          : null;
  Article.find({ ...articleQuery }, projection)
  .then(articles => {
    res.setHeader('Content-Type', 'application/json')
    if (should_get_id_only) {
      return res.json(articles.map(({ _id }) => _id));
    }
    if (should_get_url_only) {
      return res.json(articles.map(({ url }) => url));
    }
    res.json(articles);
  }, err => next(err))
  .catch(err => next(err))
});

router.get('/:articleId', ({
  params: { articleId },
  query: { should_get_photos_only, should_get_features_for_summarization }
}, res, next) => {
  const projection =
    should_get_photos_only
      ? 'photos_url'
      : should_get_features_for_summarization
        ? '-summary -vector -related_news_groups -update_datetime'
        : null;
  Article.findById(articleId, projection)
  .then(article => {
    res.setHeader('Content-Type', 'application/json')
    if (should_get_photos_only) {
      return res.json(article.photos_url);
    }
    res.json(article);
  }, err => next(err))
  .catch(err => next(err))
});

router.post('/', (req, res, next) => {
  Article.create(req.body)
  .then(articles => {
    res.setHeader('Content-Type', 'application/json');
    res.json(articles.map(a => a._id));
  }, err => next(err))
  .catch(err => next(err))
})

router.put('/:articleId', async ({
  body,
  params: { articleId },
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
    const article = await Article.findByIdAndUpdate(articleId, update, { new: true })
    res.setHeader('Content-Type', 'application/json')
    res.json(article);
  } catch (error) {
    next(error)
  }
});

router.delete('/deleteall', (req, res, next) => {
  Article.remove({})
  .then(() => {
    res.send('<h1>Successfully delete all articles</h1>')
  }, err => next(err))
  .catch(err => next(err))
})

router.delete('/:articleId', (req, res, next) => {
  Article.findByIdAndRemove(req.params.articleId)
  .then(article => {
    res.setHeader('Content-Type', 'application/json')
    res.json(article)
  }, err => next(err))
  .catch(err => next(err))
})

module.exports = router;
