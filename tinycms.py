"""
todo: robots.txt
todo: feed/
todo: sitemap.xml
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, g, render_template, redirect, flash, request, session,\
    url_for

from forms import ContactForm, LoginForm

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'articles.db'),
    DEBUG=True,
    SECRET_KEY='wdcig3624dYISD68goyg*G^G*^)TGUTsd',
    USERNAME='admin',
    PASSWORD='default',
    RECAPTCHA_PUBLIC_KEY='6Ld54iETAAAAACIPaOotIXvhboTihxFU5F6Hrb-e',
    RECAPTCHA_PRIVATE_KEY='6Ld54iETAAAAAHm0sjKT-C8WJng7ilRfl2qNqcEr',
    WTF_CSRF_SECRET_KEY='ubILYBLIyb8867gb*^BOybhliiigb'
))


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
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


@app.context_processor
def inject_utils():
    def get_dt(fmt='%d.%m.%Y'):
        return datetime.now().strftime(fmt)
    return dict(
        now=get_dt
    )


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
                return redirect(url_for('index'))
        else:
            flash('Fill form', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('index'))


@app.route('/')
def index():
    #db = get_db()
    #cur = db.execute('select title, text from entries order by id desc')
    #entries = cur.fetchall()
    return render_template('base.html')#, entries=entries)


if __name__ == '__main__':
    app.run(debug=True)
