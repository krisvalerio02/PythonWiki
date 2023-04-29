from flaskr.backend import Backend
from flask import Flask, render_template, send_file, request, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
from firebase import firebase
from datetime import datetime
import pandas as pd
import json
import plotly
import plotly.express as px

firebase_url = "https://wikigroup10-default-rtdb.firebaseio.com/"
firebase = firebase.FirebaseApplication(firebase_url, None)


def make_endpoints(app, db_client, bucket_client):
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = request.cookies.get('welcome')
        return render_template("home.html",
                               value=value,
                               username=username,
                               welcome=welcome)

    """ Defines the route URL or home page of the applciation.

    Args:  None.

    Returns: a render template of the home html page.
    It retrieves values from cookies: value, username and welcome using "request.cookies.get()
    and renders "home.html"

    """

    @app.route("/about")
    def about():
        backend = Backend('wiki-viewer-data', bucket_client)
        author_1 = backend.get_image('kemar_j.jpg')
        author_2 = backend.get_image('danielle.jpg')
        author_3 = backend.get_image('kris.jpg')
        value = request.cookies.get('value')
        username = request.cookies.get('username')
        welcome = True
        resp = make_response(
            render_template("about.html",
                            author_1=author_1,
                            author_2=author_2,
                            author_3=author_3,
                            value=value,
                            username=username,
                            welcome=welcome))
        resp.set_cookie('welcome', '', expires=0)
        return resp

    """ Defines the "/about" URL of the application.

    Args:

    None

    Returns: a render template of the about html page. It retrieves 
    an image for three authors using backend.get_image() and values from
    cookies and 'value' and 'username'.
    """

    # Sign up route
    @app.route("/signup", methods=['GET', 'POST'])
    def sign_up():
        backend = Backend('wiki-credentials', bucket_client)
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if backend.sign_up(username, password):
                return redirect(url_for('login'))
            else:
                return "Username already exists"
        else:
            return render_template('signup.html')

    @app.route("/signin", methods=['GET', 'POST'])
    def login():
        backend = Backend('wiki-credentials', bucket_client)
        message = ''
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            session['username'] = username
            value = backend.sign_in(username, password)
            if value:
                welcome = 'True'
                resp = make_response(
                    render_template('home.html',
                                    value=value,
                                    username=username,
                                    welcome=welcome))
                resp.set_cookie('value', 'True')
                resp.set_cookie('username', username)
                resp.set_cookie('welcome', 'True')
                return resp
            else:
                session['username'] = None
                message = 'ERROR: Your login attempt has failed. Make sure the username and password are correct.'
                return render_template('signin.html', message=message)
        else:
            return render_template('signin.html', message=message)

    # # Pages route
    @app.route("/pages", methods=['GET', 'POST'])
    def pages():
        if request.method == 'POST':
            username = session['username']
            author = request.form['author']
            backend = Backend('wiki-user-uploads', bucket_client)
            pages = backend.get_all_page_names(author)
            if pages == []:
                pages = backend.get_authors()
                message = 'Error: Author does not exist.'
                return render_template('pages.html',
                                       message=message,
                                       pages=pages,
                                       username=username)
            return render_template('authors.html',
                                   author=author,
                                   pages=pages,
                                   username=username)
        else:
            backend = Backend('wiki-user-uploads', bucket_client)
            pages = backend.get_authors()
            value = request.cookies.get('value')
            username = request.cookies.get('username')
            resp = make_response(
                render_template('pages.html', value=value, username=username))
            resp.set_cookie('welcome', '', expires=0)
            return render_template('pages.html',
                                   pages=pages,
                                   value=value,
                                   username=username)

    @app.route("/author_page/<page>", methods=['GET', 'POST'])
    def show_author_uploads(page):
        username = session['username']
        author = page[1:-1]
        backend = Backend('wiki-user-uploads', bucket_client)
        pages = backend.get_all_page_names(author)
        return render_template('authors.html',
                               author=author,
                               pages=pages,
                               username=username)

    # # Upload Route
    @app.route("/upload", methods=['GET', 'POST'])
    def upload():
        backend = Backend('wiki-user-uploads', bucket_client)
        username = session['username']
        if request.method == 'POST':
            wikiname = request.form['wikiname']
            wiki = request.files['wiki']
            filepath = '/tmp/' + wiki.filename
            wiki.save(filepath)
            backend.upload(filepath, wikiname, username)
            message = wikiname + ' has been uploaded successfully!'
            return render_template('upload.html',
                                   username=username,
                                   message=message)
        return render_template('upload.html', username=username)

    # # Logout route
    @app.route("/logout")
    def logout():
        resp = make_response(render_template("home.html"))
        resp.set_cookie('value', '', expires=0)
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('welcome', '', expires=0)
        session.pop('username', None)
        return resp

    # @app.before_request
    # def track_user_metadata():
    #     page = request.path
    #     # In the case of home (/) path, set page to /home
    #     if page == '/':
    #         page = '/home'
    #     elif page == '/pages':
    #         page = '/authors'
    #     elif page == '/signin':
    #         page = '/login'

    #     if session.get('username'):
    #         username = session['username']

    #         # Access the user's metadata within firebase
    #         parent_key = '/' + username + '_metadata'
    #         page_count = 0
    #         page_count = db_client.get(parent_key, page)

    #         # If the page doesn't exist then initialize it
    #         if page_count is None:
    #             page_count = 0
    #             db_client.put(parent_key, page, page_count)

    #         # Increment the page count
    #         db_client.put(parent_key, page, page_count + 1)

    # """ Defines the "/author_page/<page>" URL of the application.

    # Args:

    # None

    # Returns: It renders home.html when user logs out with cookies updated to expired.
    # """

    @app.route('/submit_comment', methods=['POST'])
    def submit_comment():
        backend = Backend('wiki-user-uploads', bucket_client)
        username = session['username']
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        author = session.get('author')
        # Get the comment data from the request
        comment = request.form['comment']
        comment_id = backend.get_comment_ID(current_time, comment)
        user_id = backend.get_userID(username, current_time)
        data = {
            'Username': username,
            'Comment': comment,
            'Comment_ID': comment_id,
            'User_ID': user_id,
            'Time': current_time
        }
        firebase.post(author, data)
        result = firebase.get(firebase_url, author)
        print(result)

        return render_template('authors.html')

    """ Defines the "/author_page/<page>" URL of the application.

    Args:

    None

    Returns: It renders page which shows author.html page after user has made a comment.Handles 
    how the data is tranferred to the database after the website receives it from the form.
    """

    @app.route('/view_comment', methods=['GET', 'POST'])
    def view_comment():
        backend = Backend('wiki-user-uploads', bucket_client)
        username = session['username']
        author = session.get('author')
        result = firebase.get(firebase_url, author)
        print(result)

        return render_template('view_comments.html',
                               result=result,
                               username=username)

    @app.route('/metadata')
    def visualize_metadata():
        username = session['username']
        # Access user metadata
        parent_key = '/' + username + '_metadata'
        visits = db_client.get(parent_key, "")
        metadata = {'Username': username, 'Pages': [], 'Visits': []}
        for key in visits:
            metadata['Pages'].append(key)
            metadata['Visits'].append(visits[key])
        df = pd.DataFrame(metadata)
        fig1 = px.bar(df, x='Pages', y='Visits', color='Username')
        graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('chart.html',
                               graphJSON=graphJSON,
                               username=username)

    """ Defines the "/author_page/<page>" URL of the application.

    Args:

    None

    Returns: It renders charts.html with metadata represented graphically in charts.
    """
