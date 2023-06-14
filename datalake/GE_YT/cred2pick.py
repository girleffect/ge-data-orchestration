import argparse
import os
import pickle
from google.oauth2.credentials import Credentials

creds = Credentials(
    token='INSERT HERE',
    refresh_token='INSERT HERE',
    token_uri="https://www.googleapis.com/oauth2/v3/token",
    client_id='INSERT HERE',
    client_secret='INSERT HERE',
    scopes=[
         'https://www.googleapis.com/auth/yt-analytics-monetary.readonly'
     ]
    )

with open('token.pickle', 'wb') as handle:
    pickle.dump(creds, handle, protocol = pickle.HIGHEST_PROTOCOL)