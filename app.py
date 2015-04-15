#!/usr/bin/env python3

from datetime import datetime

from flask import Flask, redirect, request, render_template
import redis


app = Flask(__name__)
r = redis.StrictRedis(host='localhost', port=6379, charset='utf-8',
                      decode_responses=True)


@app.route('/')
def show_index():
    if r.exists('next_post_id'):
        post_keys = r.zrevrange('posts', 0, -1)
        posts = [r.hgetall(post_key) for post_key in post_keys]
    else:
        r.set('next_post_id', 0)
        posts = {}
    return render_template('index.tmpl', posts=posts)


@app.route('/source')
def show_source():
    return render_template('source.tmpl')


@app.route('/post', methods=['POST'])
def create_post():
    author = request.form.get('author') or 'Anonymous'
    content = request.form.get('content') or "Redis is awesome!"
    timestamp = datetime.now().timestamp()
    post_id = r.incr('next_post_id')
    post_key = "post:{}".format(post_id)
    r.hmset(post_key, {'author': author, 'content': content})
    r.zadd('posts', timestamp, post_key)

    return redirect('/')


if __name__ == '__main__':
    app.run()
