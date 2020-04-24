# Allows us to login with twitter
import json
import oauth2
import constants
import urllib.parse as urlparse
from users_v1 import User

# [1]: https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/pin-based-oauth
# 1) Create a Consumer. An object that represents our app. using Consumer Key and Secret to identify app uniquely
# Consumer is used to identify app, not to make requests
consumer = oauth2.Consumer(key=constants.CONSUMER_KEY, secret=constants.CONSUMER_SECRET)


def login_user_via_twitter(user_email, consumer):
    first_name = input("Enter your first name:\t")
    last_name = input("Enter your last_name:\t")

    # 2) Use the client to perform a request for the request token
    # Client needs a Consumer, which is the application the Client is going to be making requests for
    client = oauth2.Client(consumer)

    # 3) Get the request token and parse the query string returned from the client.request(...)
    # From [1] we can see that request_token URL is a "POST" URL VERB
    response, content = client.request(constants.REQUEST_TOKEN_URL, "POST")
    # Twitter does not expect anything in the BODY of the POST
    # We get a response - details of what happened during exchange
    # Content - we expect a request token

    if response.status != 200:
        # response of 200 means everything is fine, otherwise something has gone wrong
        print("An error occurred getting the request token from Twitter")

    # Content is form of a query string parameter, and parse_qsl is used to parse a query string
    request_token = dict(urlparse.parse_qsl(content.decode('utf-8')))
    # We are requesting authorization from user to use their account to access our app

    # 4) Ask the user to authorize our app and give us the PIN/authorization code
    # Lets get PIN & redirect user to the website where they login to Twitter and retrieve a PIN
    # User needs to authorize our application
    # Twitter sends them back to e.g. ww.ourwebsite.com
    # We get authorization/PIN code + request token -> twitter -> access token

    print("Go to the following site in your website:")
    print("{auth_url}?oauth_token={oauth_token}".format(
            auth_url=constants.AUTHORIZATION_URL,
            oauth_token=request_token["oauth_token"]))

    # Twitter knows the oauth_token came from our Consumer and hence it knows this is our app
    # I go to website and the PIN I got is 1410889

    # in a web app, this verifier would be sent to us by Twitter instead of relying on user
    oauth_verifier = input("What is the PIN?\t")

    # 5) Create a Token object which contains the request token and the verifier / PIN
    # Below binds the two tokens together and puts them inside one object
    token = oauth2.Token(key=request_token["oauth_token"], secret=request_token["oauth_token_secret"])
    token.set_verifier(oauth_verifier)  # Add verifier to it. Because we needed to use a Pin Code

    # 6) Create a client with our consumer (our app) and the newly created (and verified) token
    # by setting token, now Twitter knows who/what this application is and the user accessing it
    client = oauth2.Client(consumer, token=token)

    # 7) Ask Twitter for an access token, and Twitter know it should give us it because we've verified the request token
    # we can use client to get access token
    response, content = client.request(constants.ACCESS_TOKEN_URL, "POST")
    if response.status != 200:
        # response of 200 means everything is fine, otherwise something has gone wrong
        print("An error occurred getting the access token from Twitter")

    # Content is form of a query string parameter, and parse_qsl is used to parse a query string
    access_token = dict(urlparse.parse_qsl(content.decode('utf-8')))

    print(access_token)
    # This prints out
    """
    {
    'oauth_token': '1107078956291969024-coUUtnUCBC90II3A2XTduPdXwkd42q',
    'oauth_token_secret': '6m8boops0GIYY4ASgERup5Rbxb5zfdEsxg1xbSiwxGLH7',
    'user_id': '1107078956291969024',
    'screen_name': 'ArumemiJohn'}   <-- twitter username
    """
    cur_user = User(email=user_email, first_name=first_name, last_name=last_name,
                    oauth_token=access_token["oauth_token"], oauth_token_secret=access_token["oauth_token_secret"],
                    id=None)

    cur_user.save_to_db()
    return cur_user


user_email = input("Enter your email:\t")
user_from_db = User.load_from_db_by_email(email=user_email)

if not user_from_db:
    print(f"No user with email {user_from_db} found, attempting twitter authorization.")
    user_from_db = login_user_via_twitter(user_email=user_email, consumer=consumer)

oauth_token = user_from_db.oauth_token
oauth_token_secret = user_from_db.oauth_token_secret

# 8) Create an 'authorized token' Token object and use that to perform Twitter API calls on behalf of our user
# Note the user_id and screen_name it printed out
# We can now use the tokens returned to make requests to twitter
authorized_token = oauth2.Token(key=user_from_db.oauth_token, secret=user_from_db.oauth_token_secret)
# Note that access token does not need a PIN code

# Now we create a client that makes requests with our access token
authorized_client = oauth2.Client(consumer, token=authorized_token)

# 9) Make Twitter API calls !
response, content = authorized_client.request("https://api.twitter.com/1.1/search/tweets.json?q=computers+filter:images", "GET")

if response.status != 200:
    print("An error occurred when searching!")
# loads for loading string
# load for loading from a file object
tweets = json.loads(content.decode("utf-8"))

for tweet in tweets['statuses']:
    print(tweet["text"])
