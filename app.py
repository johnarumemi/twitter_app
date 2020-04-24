from flask import Flask, render_template, session, redirect, request, url_for, g
from twitter_utils import get_request_token, get_oauth_verifier_url, get_access_token
from users import User
import requests

app = Flask(__name__)
#app.run(port=4995)  # GET HTTP/2 www.api.example.com/
# "GET / HTTP/1.1" 404 is showing us equivalent of
# GET  www.api.example.com/ HTTP/2  so we are at that '/' which is at end of .com/  i.e the root directory
# If we type in http://127.0.0.1:4995/users the console below will print
# "GET /users HTTP/1.1" 404 - that we were trying to access the users endpoint.
# Flask does not show the http://www.example.com part !
app.secret_key = '1234'  # secret key is required to ensure cookies are secured
# so that other users cannot change cookie and access somebody else's data


# This function will execute before a request method / endpoint
@app.before_request
def load_user():
    if 'screen_name' in session:
        # g is Flask globals
        g.user = User.load_from_db_by_screen_name(session['screen_name'])
    else:
        g.user = None

# Define Various Endpoints
@app.route('/')   # we are setting what is going to happen when we access the "home page"
def homepage():
    # A GET request will return "hello world" if the request is to '/'
    return render_template('home.html')

@app.route("/login/twitter")
def twitter_login():
    # if user is already logged in, redirect them to /profile endpoint
    if 'screen_name' in session and g.user:
        return redirect(url_for('profile'))

    # Get a request token
    request_token = get_request_token()

    # redirecting the user to Twitter so they can confirm authorization

    # we need to store token since after redirection to Twitter, user has left our site and
    # above variable is not available (we have left this function)
    session['request_token'] = request_token  # session is persistent between requests to twitter
    # Flask links users cookie (unique number) to a session. A session is unique for the user and stores data.
    oauth_url = get_oauth_verifier_url(request_token=request_token)
    return redirect(oauth_url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("homepage"))

# Request Twitter to redirect user back to use with the token
@app.route("/auth/twitter")
def twitter_auth():
    # Set Callback url to get redirection back to our site. http://127.0.0.1:4995/auth/twitter
    # User has arrived to this endpoint with a request of form
    # http://127.0.0.1:4995/auth/twitter?oauth_token=...&oauth_verifier=...
    # the args are the query string parameter containing the oauth_verifier
    oauth_verifier = request.args.get("oauth_verifier")
    request_token = session["request_token"]

    access_token = get_access_token(request_token=request_token, oauth_verifier=oauth_verifier)

    # access_token is a dictionary which has the screen_name in it
    user = User.load_from_db_by_screen_name(screen_name=access_token['screen_name'])
    if not user:
        user = User(access_token['screen_name'], access_token['oauth_token'], access_token['oauth_token_secret'])
        user.save_to_db()

    # Save the screen name
    session['screen_name'] = user.screen_name
    return redirect(url_for('profile'))  # Note that it is the name of the METHOD we pass, not the endpoint
    # return redirect('http://127.0.0.1:4559/profile') <-- this is one method of doing it


@app.route('/profile')
def profile():
    # Pass in variable to the template
    return render_template('profile.html', user=g.user)

@app.route('/search')
def search():
    # Make twitter requests

    base_search = "https://api.twitter.com/1.1/search/tweets.json"

    # request stores POST sent to this endpoint
    received_query = request.args.get('q') # "q=computers+filter:images"
    query = received_query.replace(' ', '+')
    uri = f"{base_search}?q={query}"
    tweets = g.user.twitter_request(uri=uri)
    tweets_text = [{"tweet": tweet['text'], "label": "neutral"} for tweet in tweets['statuses']]

    for tweet in tweets_text:

        r = requests.post("http://text-processing.com/api/sentiment/", data={"text": tweet["tweet"]})
        json_response = r.json()
        tweet["label"] = json_response["label"]
    return render_template('search.html', content=tweets_text)

# we are setting what is going to happen when we access http://127.0.0.1@4995/hello_world"
@app.route('/hello_world')
def hello_world():
    # A GET request will return "hello world" if the request is to '/'
    return "hello world!"

# Start app event loop and listen for requests on port 4995
app.run(port=4995)
