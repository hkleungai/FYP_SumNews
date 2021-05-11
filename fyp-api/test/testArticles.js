const path = require('path');
require('dotenv').config({
  path: path.resolve(process.cwd(), process.env.NODE_ENV === 'production' ? '.env.prod' : '.env.dev')
})

const request = require('supertest');
const app = require('../app');

require('assert')
require('should');

describe('GET /articles', () => {
  it('It should return all articles as a array', (done) => {
    request(app)
    .get('/articles')
    .expect('Content-Type', /json/)
    .expect(200)
    .expect(res => {
      res.body.should.be.instanceof(Array);
      res.body[0].should.have.property('title');
      res.body[0].should.have.property('text');
      res.body[0].should.have.property('date_added');
      res.body[0].should.have.property('url');
      res.body[0].should.have.property('source');
      res.body[0].should.have.property('photos_url');
      res.body[0].should.have.property('is_grouped');
      res.body[0].should.have.property('upvotes');
      res.body[0].should.have.property('downvotes');
      res.body[0].should.have.property('_id');
      res.body[0].should.have.property('sentences');
    })
    .end(done)
  })
})
