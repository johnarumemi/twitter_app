import oauth2
import constants
import urllib.parse as urlparse

# This is our app and persists with same variables everywhere
consumer = oauth2.Consumer(key=constants.CONSUMER_KEY, secret=constants.CONSUMER_SECRET)


def get_request_token():
    client = oauth2.Client(consumer)

    # 3) Get the request token and parse the query string returned from the client.request(...)
    # From [1] we can see that ddrequest_token URL is a "POST" URL VERB
    response, content = client.request(constants.REQUEST_TOKEN_URL, "POST")

    if response.status != 200:
        print("An error occurred getting the request token from Twitter")

    # Content is form of a query string parameter, and parse_qsl is used to parse a query string
    return dict(urlparse.parse_qsl(content.decode('utf-8')))


def get_oauth_verifier(request_token):
    print("Go to the following site in your website:")
    print(get_oauth_verifier_url(request_token))

    # Twitter knows the oauth_token came from our Consumer and hence it knows this is our app
    # I go to website and the PIN I got is 1410889

    # in a web app, this verifier would be sent to us by Twitter instead of relying on user
    oauth_verifier = input("What is the PIN?\t")
    return oauth_verifier

def get_oauth_verifier_url(request_token):
    url = "{auth_url}?oauth_token={oauth_token}".format(
            auth_url=constants.AUTHORIZATION_URL,
            oauth_token=request_token["oauth_token"])
    return url

def get_access_token(request_token, oauth_verifier):
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

    return access_token
