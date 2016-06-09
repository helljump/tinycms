# TODO: robots.txt
# TODO: feed/
# TODO: sitemap.xml


import functools
import os
import sqlite3
from datetime import datetime
from slugify import slugify
from flask import Flask, g, render_template, redirect, flash, request, session,\
    url_for, abort
from werkzeug.utils import secure_filename
from flask_wtf import CsrfProtect
from flask_babel import Babel, format_datetime
import time
from forms import ContactForm, LoginForm, ArticleForm
from pagination import Pagination

PER_PAGE = 2

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'articles.db'),
    DEBUG=True,
    SECRET_KEY='wdcig3624dYISD68goyg*G^G*^)TGUTsd',
    USERNAME='admin',
    PASSWORD='default',
    RECAPTCHA_PUBLIC_KEY='6Ld54iETAAAAACIPaOotIXvhboTihxFU5F6Hrb-e',
    RECAPTCHA_PRIVATE_KEY='6Ld54iETAAAAAHm0sjKT-C8WJng7ilRfl2qNqcEr',
    WTF_CSRF_SECRET_KEY='ubILYBLIyb8867gb*^BOybhliiigb',
    UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
    ALLOWED_EXTENSIONS=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'],
    BABEL_DEFAULT_LOCALE='ru'
    #BABEL_DEFAULT_TIMEZONE='Europe/Moscow'
))

CsrfProtect(app)
Babel(app)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'], isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def get_db():
    if not hasattr(g, 'conn'):
        g.conn = connect_db()
    return g.conn


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'conn'):
        g.conn.close()


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner


@app.context_processor
def inject_utils():
    def get_dt(fmt='dd MMMM YY'):
        return format_datetime(datetime.now(), fmt)
    return dict(
        now=get_dt
    )


@app.template_filter('date')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return format_datetime(date, fmt)
    else:
        return format_datetime(date, 'dd MMMM YY, HH:mm')


@app.route('/contact', methods=('GET', 'POST'))
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash("Сообщение отправлено", category='success')
            return redirect('/contact')
        else:
            flash("Исправьте ошибки", category='warning')
    return render_template('contact.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    app.logger.info("next: %s", next_url)
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.name.data != app.config['USERNAME']:
                flash('Invalid username', 'danger')
            elif form.password.data != app.config['PASSWORD']:
                flash('Invalid password', 'danger')
            else:
                session['logged_in'] = True
                flash('You were logged in', 'success')
                return redirect(next_url or url_for('index'))
        else:
            flash('Fill form', 'danger')
    return render_template('login.html', form=form, next=next_url)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('index'))


@app.route('/edit', methods=['GET', 'POST'])
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_article(post_id=None):
    form = ArticleForm()
    db = get_db()
    if request.method == 'POST' and form.validate():
        slug = slugify(form.title.data, max_length=50)
        data = [
            slug,
            form.title.data,
            form.intro.data,
            form.text.data,
            form.date.data,
            form.published.data,
            form.description.data,
            form.keywords.data
        ]
        if form.pk.data is not None:
            data.append(form.pk.data)
            db.execute("update articles set slug=?, title=?, intro=?, text=?, date=?, published=?, "
                       "description=?, keywords=? where id=?", data)
            flash('Статья обновлена', 'success')
            return redirect(url_for('edit_article', post_id=form.pk.data))
        else:
            cur = db.execute("insert into articles (slug, title, intro, text, date, published, "
                             "description, keywords) values(?,?,?,?,?,?,?,?)", data)
            flash('Статья добавлена', 'success')
            return redirect(url_for('edit_article', post_id=cur.lastrowid))
    if request.method == 'GET':
        if post_id is not None:
            cur = db.execute("select * from articles where id=?", [post_id])
            article = cur.fetchone()
            if article is None:
                abort(404)
            app.logger.debug("edit article %i", article['id'])
            form.pk.data = article['id']
            form.title.data = article['title']
            form.intro.data = article['intro']
            form.text.data = article['text']
            form.date.data = article['date']
            form.published.data = article['published']
            form.description.data = article['description']
            form.keywords.data = article['keywords']
    return render_template('edit.html', form=form)


@app.route('/<slug>.html')
def view_article(slug):
    db = get_db()
    row = db.execute("select * from articles where slug=? and published", [slug]).fetchone()
    if row is None:
        abort(404)
    return render_template('article.html', article=row)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if not request.is_xhr:
        abort(401)
    if not file.filename.strip():
        abort(401)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fout = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(fout):
            egg = os.path.splitext(fout)
            fout = "{}{:x}{}".format(egg[0], int(time.time()*10), egg[1])
            app.logger.debug("make new name %s", fout)
        file.save(fout)
        return '/static/uploads/{}'.format(filename)
    abort(401)


@app.route('/')
def index():
    db = get_db()
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    search_query = request.args.get('q')
    if search_query:
        egg = "%{}%".format(search_query[:20])
        articles = db.execute("select slug, title, intro, date from articles "
                              "where published and (title like ? or intro like ?) "
                              "order by date desc limit ?", [egg, egg, PER_PAGE])
        pagination = Pagination(1, PER_PAGE, PER_PAGE)
    else:
        cnt = db.execute("select count(*) from articles where published").fetchone()[0]
        pagination = Pagination(page, PER_PAGE, cnt)
        articles = db.execute("select slug, title, intro, date from articles where published "
                              "order by date desc "
                              "limit ? offset ?", [PER_PAGE, (pagination.page-1)*PER_PAGE])
    return render_template('index.html', articles=articles, pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)
