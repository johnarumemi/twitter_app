# class to model our users by
from database import CursorFromConnectionFromPool
import json
import oauth2
from twitter_utils import consumer


class User(object):

    def __init__(self, email, first_name, last_name, oauth_token, oauth_token_secret, id):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id

    def __repr__(self):
        return "<User {}>".format(self.email)

    def save_to_db(self):

        with CursorFromConnectionFromPool() as cursor:
            # Context manage ensures cursor is closed at the end
            cursor.execute('INSERT INTO users (email, first_name, last_name, oauth_token, oauth_token_secret) VALUES (%s, %s, %s, %s, %s)',
                           (self.email, self.first_name, self.last_name, self.oauth_token, self.oauth_token_secret))

    @classmethod
    def load_from_db_by_email(cls, email):

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT * FROM users WHERE users.email=%s",
                           (email,))
            # do not remove parentheses around the (email), just use (email,) to tell python it is a tuple

            user_data = cursor.fetchone()  # get 1 row of data from retrieved query

            if not user_data:
                # No user data found, return None
                return None

            # When we select email column we get a whole row of data [id, email, first_name, ... etc] in column order
            return cls(email=user_data[1],
                       first_name=user_data[2], last_name=user_data[3],
                       oauth_token=user_data[4], oauth_token_secret=user_data[5],
                       id=user_data[0])

    def twitter_request(self, uri, verb="GET"):

        # Generate authorized tokens and an authorised client to make requests on our behalf
        authorized_token = oauth2.Token(key=self.oauth_token, secret=self.oauth_token_secret)
        authorized_client = oauth2.Client(consumer, token=authorized_token)

        # Make Twitter API request
        response, content = authorized_client.request(uri, verb)

        if response.status != 200:
            print("An error occurred when searching!")

        return json.loads(content.decode("utf-8"))

