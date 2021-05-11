![title](assets/title.png)

[![package manager - yarn](https://img.shields.io/badge/package_manager-yarn-blue?logo=yarn)](https://yarnpkg.com/)
[![package manager - pip](https://img.shields.io/badge/package_manager-pip-blue?logo=python)](https://pypi.org/project/pip)
[![package manager - anaconda](https://img.shields.io/badge/package_manager-anaconda-blue?logo=anaconda)](https://www.anaconda.com/)
[![deployment - colab](https://img.shields.io/badge/deployment-colab-green?logo=google)](https://colab.research.google.com/)
[![deployment - vercel](https://img.shields.io/badge/deployment-vercel-green?logo=vercel)](https://vercel.com/)
[![deployment - heroku](https://img.shields.io/badge/deployment-heroku-green?logo=heroku)](https://www.heroku.com/)
[![language - python](https://img.shields.io/badge/language-python-yellow?logo=python)](https://www.python.org/)
[![language - node.js](https://img.shields.io/badge/language-node.js-yellow?logo=node.js)](https://nodejs.org/en/)
[![language - scss](https://img.shields.io/badge/language-scss-yellow?logo=sass)](https://sass-lang.com/)
[![framework - selenium](https://img.shields.io/badge/framework-selenium-red?logo=selenium)](https://www.selenium.dev/)
[![framework - tensorflow](https://img.shields.io/badge/framework-tensorflow-red?logo=tensorflow)](https://www.tensorflow.org/)
[![framework - keras](https://img.shields.io/badge/framework-keras-red?logo=keras)](https://keras.io/)
[![framework - express.js](https://img.shields.io/badge/framework-express.js-red?logo=express)](https://expressjs.com/)
[![framework - vue.js](https://img.shields.io/badge/framework-vue.js-red?logo=vue.js)](https://vuejs.org/)
[![framework - nuxt.js](https://img.shields.io/badge/framework-nuxt.js-red?logo=nuxt.js)](https://nuxtjs.org/)
[![framework - mongodb](https://img.shields.io/badge/framework-mongodb-red?logo=mongodb)](https://www.mongodb.com/)
[![library - nltk](https://img.shields.io/badge/library-nltk-purple?logo=python)](https://www.nltk.org/)
[![library - spacy](https://img.shields.io/badge/library-spacy-purple?logo=python)](https://spacy.io/)
[![library - beautiful soup](https://img.shields.io/badge/library-beautiful_soup-purple?logo=python)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
[![library - newspaper3k](https://img.shields.io/badge/library-newspaper3k-purple?logo=python)](https://pypi.org/project/newspaper3k/)
[![library - swiper](https://img.shields.io/badge/library-swiper-purple?logo=javascript)](https://swiperjs.com/)
[![library - swiper](https://img.shields.io/badge/library-moment-purple?logo=javascript)](https://momentjs.com/)


Many thanks to our advisor, Dr. Cecia Chan, and my passionate groupmates, [Martin](https://github.com/lhfmartin), [Anson](https://github.com/Anson-To), and [Klaus](https://github.com/ChauShunWai), for the successful delivery of this project.

---

## Table of contents
* [Overview](#overview)
* [AI + Scraper](#ai--scraper)
  * [Getting Started](#getting-started)
  * [Sequential Diagrams](#sequential-diagrams)
      * [News Scraping](#news-scraping)
      * [News Processing](#news-processing)
* [API](#api)
  * [Getting Started](#getting-started)
  * [Testing](#testing)
  * [Documentation](#documentation)
* [Database](#database)
* [Frontend](#frontend)
  * [Getting Started](#getting-started)
  * [Testing](#testing)

---

## Overview

Our project can be briefly summarized by the table below.

![overview](assets/overview.png)

Frontend web component is built for displaying the computed news result,

![overview](assets/system-flow.png)

and data are scraped and computed in backend.

![data-flow](assets/data-flow.png)

Of course the development of database is essential along the way.

![schema](assets/schema.png)

More details about this project can be found in our final delivery.
- [Presentation Slides](assets/final-presentation.pptx)
- [Report](assets/final-report.pdf)

See [this link](https://ceci1.vercel.app) for an experimental deployment of the project. Interested visitors can follow the instructions below to start your local development.

---

## AI + Scraper

### Getting Started

It is understandable that not everyone owns a machine with powerful hardwares. In this case, using **Google Colab** to run the codes in this repository might be your way to go. Just visit our [colab notebook](./colab_driver.ipynb) and have some fun with it. 

Alternatively you may install the dependencies via conda (with [requirements.txt](./requirements.txt)) or via pip (with [requirements_pip.txt](./requirements_pip.txt)), and you may still wanna refer to the step 4 in the [colab notebook](./colab_driver.ipynb) for the exact commands that need to be executed.

### Sequential Diagrams

Below gives a rough sketch on backend data flow.

#### News Scraping
![](https://i.imgur.com/pekJyWh.png)

```
title News Scraping

participant News AI
participant External News Source
database News Database

News AI->External News Source: Request news on reqular interval
External News Source-->News AI: Return news
News AI->News Database: Save news
```

#### News Processing
![](https://i.imgur.com/7leB8PT.png)

```
title News Processing

participant News AI
database News Database

News AI->News Database: Request news from past day
News Database-->News AI: Return news
box over News AI: Assign a group for newly downloaded news
News AI->News Database: Save group ids for newly downloaded news
box over News AI: Summarization for news groups
News AI->News Database: Save group summary
```

---

## API

### Getting Started
0. Install MongoDB 
1. Install dependencies with `yarn install`
2. Start the server with `yarn start`
3. The API is now served at port 3000

### Testing
Run `yarn test`. This part in terms of code coverage is largely incomplete, due to time limit.

### Documentation
Most logic inside the API endpoints are quite self-explainatory, but it can for sure be made better.

---

## Database

- Schema is displayed in the [overview](#overview) section. 
- Inside the [`fyp-db/`](fyp-db/) folder, there are also some precomputed data (stored in a [`temp/`](fyp-db/temp/) that can be used for model training or for demos trials in the [`fyp-ai/`](fyp-ai/) folder.

---

## Frontend

### Getting Started

```bash
# install dependencies
$ yarn install

# serve with hot reload at localhost:3000
$ yarn dev

# build for production and launch server
$ yarn build
$ yarn start

# generate static project
$ yarn generate
```

For detailed explanation on how things work, check out [Nuxt.js docs](https://nuxtjs.org).

### Testing
Run `yarn test`. This part in terms of code coverage is largely incomplete, due to time limit.
