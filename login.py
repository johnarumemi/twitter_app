# Allows us to login with twitter
import oauth2
import constants
from users import User
from twitter_utils import get_request_token, get_oauth_verifier, get_access_token

user_email = input("Enter your email:\t")
user_db = User.load_from_db_by_email(email=user_email)

if not user_db:
    # User not in Database
    print(f"No user with email {user_db} found, attempting twitter authorization.")

    first_name = input("Enter your first name:\t")
    last_name = input("Enter your last_name:\t")

    # Get the request token
    request_token = get_request_token()

    # Get verifier / Authorization Token
    oauth_verifier = get_oauth_verifier(request_token=request_token)

    # Get Access Token
    access_token = get_access_token(request_token=request_token, oauth_verifier=oauth_verifier)

    # Create user
    user_db = User(email=user_email, first_name=first_name, last_name=last_name,
                   oauth_token=access_token["oauth_token"], oauth_token_secret=access_token["oauth_token_secret"],
                   id=None)

    # Save user details to Database
    user_db.save_to_db()

# Make twitter requests
tweets = user_db.twitter_request("https://api.twitter.com/1.1/search/tweets.json?q=computers+filter:images")

for tweet in tweets['statuses']:
    print(tweet["text"])
