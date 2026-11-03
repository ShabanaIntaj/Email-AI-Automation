import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask import Flask, redirect, request
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri="http://localhost:5000/oauth2callback"
)


@app.route("/")
def home():
    return '<a href="/login">Connect Gmail</a>'


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    with open("token.json", "w") as token:
        token.write(credentials.to_json())

    return "Google authentication successful!"


if __name__ == "__main__":
    app.run(port=5000, debug=True)