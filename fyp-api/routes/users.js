const express = require('express');
const router = express.Router();

const User = require('../models/User');

router.get('/', async (_, res, next) => {
  try {
    const users = await User.find({});
    res.setHeader('Content-Type', 'application/json');
    res.json(users);
  } catch (error) {
    next(error);
  }
});

router.post('/register', async (req, res, next) => {
  try {
    const currentUsers = await User.find({}, 'email name');
    if (currentUsers.some(({ email, name }) => (
      email === req.body.email || name === req.body.name
    ))) {
      return res.json({
        error: 'User already exists. Please use another email and/or user name for registration.'
      });
    }
    const { _id, email, name } = await User.create({ ...req.body });
    res.setHeader('Content-Type', 'application/json');
    res.json({ _id, email, name });
  } catch (error) {
    return next(error);
  }
});

router.post('/login', async (req, res, next) => {
  try {
    const users = await User.find(req.body, 'email name is_logged_in');
    if (users.length === 0) {
      return res.json({
        error: 'This email is not registered, or you have entered the wrong password. Please retry  !'
      });
    }
    if (users.length > 1) {
      return res.json({
        error: 'More than one account is found, you may not access yours for now!'
      });
    }
    const { _id, email, name, is_logged_in } = users[0];
    if (is_logged_in) {
      return res.json({
        error: 'This account is being accessed in other browsers or devices, you may not access it for now!'
      });
    } else {
      await User.findByIdAndUpdate(_id, { is_logged_in: true }, { new: true });
      res.setHeader('Content-Type', 'application/json');
      res.json({ _id, email, name });
    }
  } catch (error) {
    return next(error);
  }
});

router.post('/logout', async ({
  body: { userId }
}, res, next) => {
  try {
    await User.findByIdAndUpdate(userId, { is_logged_in: false }, { new: true });
    res.setHeader('Content-Type', 'application/json');
    res.json({ _id, email, name });
  } catch (error) {
    return next(error);
  }
});

router.post('/saved-news', async ({
  body: { userId, newsId }
}, res, next) => {
  try {
    const { _id, saved_news } = await User.findByIdAndUpdate(
      userId, { $addToSet: { saved_news: newsId } }, { new: true }
    );
    res.setHeader('Content-Type', 'application/json');
    res.json({ userId: _id, newsId, saved_news });
  } catch (error) {
    return next(error);
  }
});

router.get('/:userId/saved-news', async ({
  params: { userId }
}, res, next) => {
  try {
    const saved_news = (
      await User
        .findById(userId, 'saved_news')
        .populate('saved_news', 'summary articles update_datetime photos view_count')
        .map(({ saved_news }) => saved_news)
    );
    res.setHeader('Content-Type', 'application/json');
    res.json(saved_news);
  } catch (error) {
    return next(error);
  }
});

router.delete('/:userId', async ({ params: { userId }}, res, next) => {
  try {
    const user = await User.findByIdAndRemove(userId);
    res.setHeader('Content-Type', 'application/json');
    res.json(user);
  } catch (error) {
    next(error);
  }
})

router.delete('/deleteall', async (_, res, next) => {
  try {
    await User.remove({});
    res.send('<h1>Successfully delete all users</h1>');
  } catch (error) {
    next(error);
  }
})

module.exports = router;
