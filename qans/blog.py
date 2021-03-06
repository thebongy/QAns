from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from qans.auth import login_required
from qans.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


def get_post(id):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post

def get_reply(id):
    reply = get_db().execute(
        'SELECT p.id, p.post_id, body, created, author_id, username'
        ' FROM answers p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if reply is None:
        abort(404, "Reply id {0} doesn't exist.".format(id))

    return reply

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/postReply', methods=('POST',))
@login_required
def postReply(id):
    body = request.form["body"]
    
    db = get_db()
    db.execute(
        'INSERT INTO answers (body, author_id, post_id)'
        ' VALUES (?, ?, ?)',
        (body, g.user['id'], id)
    )
    db.commit()
    return redirect(url_for('blog.thread', id=id))

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.thread', id=id))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/updateReply', methods=('GET', 'POST'))
@login_required
def updateReply(id):
    reply = get_reply(id)
    error = None
    if request.method == 'POST':
        body = request.form['body']
        postID = request.form['postID']

        if not body:
            error = 'Reply cannot be empty'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE answers SET body=? WHERE id=?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('blog.thread', id=postID))
    return render_template('blog/updateReply.html', reply=reply)

@bp.route('/<int:id>/thread', methods=('GET', ))
@login_required
def thread(id):
    post = get_post(id)

    db = get_db()
    replies = db.execute(
        'SELECT p.id, body, created, author_id, post_id, username'
        ' FROM answers p JOIN user u ON p.author_id = u.id'
        ' WHERE p.post_id=?'
        ' ORDER BY created ASC',
        (id, )
    ).fetchall()
    return render_template('blog/thread.html', post=post, replies=replies)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    if g.user['id'] != post['author_id']:
        abort(403)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.execute('DELETE FROM answers WHERE post_id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/deleteReply', methods=('POST',))
@login_required
def deleteReply(id):
    reply = get_reply(id)
    if g.user['id'] != reply['author_id']:
        abort(403)
    db = get_db()
    db.execute('DELETE FROM answers WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.thread', id=reply['post_id']))
