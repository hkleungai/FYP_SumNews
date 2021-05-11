const express = require("express");
const router = express.Router();
const Article = require("../models/Article");
const NewsGroup = require("../models/NewsGroup");

const newsAgenciesForTesting = [
  {
    name: "news_agency_1",
    popularity: 100,
    fairness: 150,
  },
  {
    name: "news_agency_2",
    popularity: 200,
    fairness: 250,
  },
  {
    name: "news_agency_3",
    popularity: 300,
    fairness: 350,
  },
];

const imagesForTesting = [
  {
    name: "image_1",
    url: "image_1.jpg",
    source: "news_agency_1",
    upvote: 12,
  },
  {
    name: "image_2",
    url: "image_2.jpg",
    source: "news_agency_2",
    upvote: 8,
  },
  {
    name: "image_3",
    url: "image_3.jpg",
    source: "news_agency_3",
    upvote: 4,
  },
];
const selectBestAgency = (newsAgencies) => {
  return newsAgencies.reduce((previous, current) => {
    current.score = (current.popularity + current.fairness) / 2;
    return previous.score > current.score ? previous : current;
  });
};

const selectStartPhoto = (bestAgency, images) => {
  const targetImage = images.find((image) => image.source === bestAgency.name);
  return targetImage && targetImage.url;
};

const selectBestPhoto = (images) => {
  const imageWithHighestUpvote = images.reduce((previous, current) => {
    return previous.upvote > current.upvote ? previous : current;
  });
  return imageWithHighestUpvote.url;
};

// router.get('/:articleId/thumbnails', function (req, res, next) {
//     Article.findById(req.params.articleId)
//         .then(
//             (article) => {
//                 const bestAgency = selectBestAgency(newsAgenciesForTesting);
//                 const startPhoto = selectStartPhoto(
//                     bestAgency,
//                     imagesForTesting
//                 );
//                 const bestPhoto = selectBestPhoto(imagesForTesting);
//                 res.setHeader('Content-Type', 'application/json');
//                 res.json(article);
//             },
//             (err) => next(err)
//         )
//         .catch((err) => next(err));
// });

//my idea of search
// function search(searchWords) {
//     //initialise a result array which sotres the object results
//     var result = new Article[articles.length]();
//     //given a list of articles
//     for (var i = 0; i < articles.length; i++) {
//         if (articles[i].title.includes(searchWords)) {
//             //put in result array and later can be used to list out the found results
//             result.append(articles[i]);
//             return result;
//         }
//     }
//     //nothing is found
//     console.log(
//         'We couldn't find a match with\'' +
//             searchWords +
//             ''.Please try another search.'
//     );
// }

router.get("/", (_, res) => {
  res.send("respond with a resource");
});

//search articles by summary.top[0],previously title
//test of aranging articles by date
router.get("/:searchWords", (req, res, next) => {
  NewsGroup.find(
    {
      "summary.top.0": { $regex: req.params.searchWords, $options: "i" },
    },
    "summary articles update_datetime photos"
  )
    .sort({ update_datetime: "descending" })
    .then(
      (articles) => {
        res.setHeader("Content-Type", "application/json");
        res.json(articles);
      },
      (err) => next(err)
    )
    .catch((err) => next(err));
});

//new for images... thumbnails...
router.get("/:newsId/images", function (req, res, next) {
  NewsGroup.findbyId(req.params.newsId, function (err, doc) {
    if (err) {
      next(err);
    } else {
      res.contentType("String"); //With reference to others
      res.send(doc.photos[0]);
    }
  });
  // .then(
  //     (articles) => {
  //         res.setHeader('Content-Type', 'application/json');
  //         res.json(articles);
  //     },
  //     (err) => next(err)
  // )
  //.catch((err) => next(err));
});

module.exports = router;
