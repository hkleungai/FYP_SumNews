const createError = require("http-errors");
const express = require("express");
const path = require("path");
const cookieParser = require("cookie-parser");
const logger = require("morgan");

require("dotenv").config({
  path: path.resolve(
    process.cwd(),
    process.env.NODE_ENV === "production" ? ".env.prod" : ".env.dev"
  ),
});

require("mongoose")
  .connect(process.env.DB_URL, { useNewUrlParser: true })
  .then(() => console.log("Connected to database"), console.error);

const indexRouter = require("./routes/index");
const usersRouter = require("./routes/users");
const articlesRouter = require("./routes/articles");
const newsRouter = require("./routes/news");
const commentRouter = require("./routes/comments");
const searchRouter = require("./routes/search");

const app = express();

// view engine setup
app.set("views", path.join(__dirname, "views"));
app.set("view engine", "pug");

app.use(logger("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "public")));

app.use(({ headers: { origin = "" } }, res, next) => {
  const allowedOrigins = [
    "(https?://)?ceci1.vercel.app", // master branch deployment
    "(https?://)?fyp-frontend-git-[0-9A-Za-zs-]+.vercel.app", // git pull request build
    "(http?://)?localhost:\\d{4,5}", // localhost with port
    "(https?://)?127(?:.[0-9]+){0,2}.[0-9]+:\\d{4,5}", // ipv4 address
  ];
  if (origin.match(new RegExp(`^${allowedOrigins.join("|")}\$`))) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Methods", "*");
    res.setHeader("Access-Control-Allow-Headers", "*");
    res.setHeader("Access-Control-Allow-Credentials", true);
  }
  next();
});

app.use("/", indexRouter);
app.use("/users", usersRouter);
app.use("/articles", articlesRouter);
app.use("/news", newsRouter);
app.use("/comments", commentRouter);
app.use("/search", searchRouter);

// catch 404 and forward to error handler
app.use((req, res, next) => {
  next(createError(404));
});

// error handler
app.use((err, req, res) => {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get("env") === "development" ? err : {};

  console.error(err);

  // render the error page
  res.status(err.status || 500);
  res.render("error");
});

module.exports = app;
