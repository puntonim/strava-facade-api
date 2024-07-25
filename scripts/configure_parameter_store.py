"""
Run this during the first deployment in order to fill AWS Parameter Store
 with a valid Strava API token.

$ python scripts/configure_parameter_store.py
"""
import json
import sys

import requests

from strava_facade_api.clients.aws_parameter_store_client.aws_parameter_store_client import (
    ParameterStoreClient,
)
from strava_facade_api.clients.strava_client.token_manager import (
    CLIENT_ID_PARAMETER_STORE_KEY_PATH,
    CLIENT_SECRET_PARAMETER_STORE_KEY_PATH,
    TOKEN_PARAMETER_STORE_KEY_PATH,
)


def main():
    ssm_client = ParameterStoreClient()

    # Prompt the user for the API authorizer for this app.
    data = input(
        "Type a secret for the API authorizer of this app and to be used in every requests' headers: "
    )
    if not data.strip():
        print("Invalid", file=sys.stderr)
        sys.exit(1)
    api_authorizer_secret = data.strip()
    ssm_client.put_secret(
        "/strava-facade-api/production/api-authorizer-token", api_authorizer_secret
    )

    # Prompt the user for the client_id.
    data = input("Type your Strava app client_id: ")
    if not data.strip():
        print("Invalid", file=sys.stderr)
        sys.exit(1)
    client_id = data.strip()

    # Prompt the user for the client_secret.
    data = input("And type your Strava app client_secret: ")
    if not data.strip():
        print("Invalid", file=sys.stderr)
        sys.exit(1)
    client_secret = data.strip()

    # Perform the Oauth2 dance to get an access token.
    url = f"http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://127.0.0.1&approval_prompt=force&scope=read,activity:read_all,activity:write"
    print(
        f"Now open your browser at this url, then click 'Authorize' and copy the code in the url of the final blank page:\n{url}",
        file=sys.stderr,
    )
    data = input("Type the code you copied from the url of the final blank page: ")
    if not data.strip():
        print("Invalid", file=sys.stderr)
        sys.exit(1)
    auth_code = data.strip()

    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    token = response.json()
    print(f"> You got the token:\n{token}", file=sys.stderr)

    if not token.get("access_token"):
        raise Exception("Missing 'access_token' field in JSON response")
    if not token.get("refresh_token"):
        raise Exception("Missing 'refresh_token' field in JSON response")
    if not token.get("expires_at"):
        raise Exception("Missing 'expires_at' field in JSON response")

    # Now store the data in AWS Parameter STore.
    ssm_client.put_parameter(CLIENT_ID_PARAMETER_STORE_KEY_PATH, client_id)
    ssm_client.put_secret(CLIENT_SECRET_PARAMETER_STORE_KEY_PATH, client_secret)
    ssm_client.put_secret(TOKEN_PARAMETER_STORE_KEY_PATH, json.dumps(token, indent=4))


if __name__ == "__main__":
    print("START")
    main()
    print("END")
