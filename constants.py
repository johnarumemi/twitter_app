import os
import oauth2

CONSUMER_KEY = os.getenv("TWITTER_API_KEY")
CONSUMER_SECRET = os.getenv("TWITTER_API_SECRET")

# This are obtained from Twitter API
# We need the Pin-based authorization
# https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/pin-based-oauth

base_url = "https://api.twitter.com/"

# Endpoints
request_token_ep = "oauth/request_token"
authorization_token_ep = "oauth/authorize"
access_token_ep  = "oauth/access_token"

# Complete urls
REQUEST_TOKEN_URL = base_url + request_token_ep         # Get new request token
AUTHORIZATION_URL = base_url + authorization_token_ep   # Get an authorization token (get a new pin code)
ACCESS_TOKEN_URL = base_url + access_token_ep           # Get an access token (once we have pin code)

