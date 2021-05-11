const express = require('express');
const router = express.Router();

const NewsGroup = require('../models/NewsGroup')
const Article = require('../models/Article')

router.get('/', async ({
  query: {
    should_get_id_only,
    should_get_articles_and_id_only,
    should_get_vector_and_id_only,
    should_get_req_info_for_frontend,
    ...newsQuery
  }
}, res, next) => {
  try {
    const projection =
      should_get_id_only
        ? ''
        : should_get_articles_and_id_only
          ? 'articles'
          : should_get_vector_and_id_only
            ? 'vector'
            : should_get_req_info_for_frontend
              ? 'summary articles update_datetime photos view_count'
              : null;
    const ng = await NewsGroup.find({ ...newsQuery }, projection).sort({ update_datetime: 'descending' });
    res.setHeader('Content-Type', 'application/json');
    if (should_get_id_only) {
      return res.json(ng.map(({ _id }) => _id));
    }
    res.json(ng);
  } catch (error) {
    next(error);
  }
});

router.get('/news-with-articles', async (_, res, next) => {
  try {
    const news = await NewsGroup.find({}).populate('articles', 'sentences url').select('articles')
    return res.json(news)
  } catch (error) {
    next(error)
  }
});

router.get('/:newsId', ({
  params: { newsId },
  query: { should_get_articles_and_id_only }
}, res, next) => {
  const projection = should_get_articles_and_id_only ? 'articles' : null;
  NewsGroup.findById(newsId, projection)
  .then(ng => {
    res.setHeader('Content-Type', 'application/json')
    res.json(ng)
  }, err => next(err))
  .catch(err => next(err))
});

router.get('/:newsId/populated', async ({ params: { newsId }}, res, next) => {
  try {
    const news = (
      await NewsGroup
        .findByIdAndUpdate(newsId, { $inc: { view_count: 1 } }, { new: true })
        .populate('articles', 'source upvotes downvotes url date_added photos_url')
        .populate('related_news_groups', '-vector')
        .select('-vector')
    );
    return res.json(news);
  } catch (error) {
    next(error)
  }
});

const updateGroupedAndPhotosProperties = async articles => {
  const ng_photos = [];
  for (const article of articles) {
    const { photos_url } = await Article.findByIdAndUpdate(
      article,
      { is_grouped: true },
      { new: true }
    );
    // indexOf() trick for removing self-duplicate,
    // and includes() trick remove duplicates from existing set
    const photos_url_to_be_injected = photos_url.filter(
      (url, index, arr) => arr.indexOf(url) === index && !(ng_photos.includes(url))
    );
    ng_photos.push.apply(ng_photos, photos_url_to_be_injected);
  }
  return ng_photos;
}

router.post('/', async (req, res, next) => {
  try {
    const body = [];
    for (req_ng of req.body) {
      const photos = await updateGroupedAndPhotosProperties(req_ng.articles);
      body.push({ ...req_ng, photos });
    }
    const ng = await NewsGroup.create(body);
    res.setHeader('Content-Type', 'application/json')
    res.json(ng.map(({ _id }) => _id))
  } catch (error) {
    next(error);
  }
})

router.put('/:newsId', async (req, res, next) => {
  try {
    const old_ng = await NewsGroup.findById(req.params.newsId);
    const articles_to_be_handled = (req.body.articles || []).filter(
      article => !(old_ng.articles.includes(article))
    );
    const new_photos = await updateGroupedAndPhotosProperties(
      req.query.should_handle_old_photos ? old_ng.articles : articles_to_be_handled
    );
    const ng = await NewsGroup.findByIdAndUpdate(
      req.params.newsId,
      { ...req.body, photos: old_ng.photos.concat(new_photos) },
      { new: true }
    );
    res.json(ng);
  } catch (error) {
    next(error);
  }
})

router.delete('/deleteall', (_, res, next) => {
  Article.update({}, {is_grouped: false}, {multi: true})
  .catch(err => next(err))

  NewsGroup.remove({})
  .then(() => {
    res.send('<h1>Successfully delete all news group</h1>')
  }, err => next(err))
  .catch(err => next(err))
})

router.delete('/:newsId', (req, res, next) => {
  NewsGroup.findByIdAndRemove(req.params.newsId)
  .then(ng => {
    res.setHeader('Content-Type', 'application/json')
    res.json(ng)
  }, err => next(err))
  .catch(err => next(err))
})

module.exports = router;
