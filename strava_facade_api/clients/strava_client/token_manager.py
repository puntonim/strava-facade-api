import json
from time import time
from typing import Optional

import requests

from ..aws_parameter_store_client.aws_parameter_store_client import ParameterStoreClient

TOKEN_JSON_PARAMETER_STORE_KEY_PATH = "/strava-facade-api/production/strava-api-token-json"
CLIENT_ID_PARAMETER_STORE_KEY_PATH = "/strava-facade-api/production/strava-api-client-id"
CLIENT_SECRET_PARAMETER_STORE_KEY_PATH = "/strava-facade-api/production/strava-api-client-secret"


class TokenManager:
    SECRET_FILE = "secret"

    def __init__(self) -> None:
        self.token = None

    @staticmethod
    def get_access_token() -> str:
        """
        Get a valid access token as stored in AWS Parameter Store.
        Or, if expired, refresh it and store it in AWS Parameter Store.
        It required the client id and secret to be stored in AWS Parameter Store.

        Docs:
            - Authentication: https://developers.strava.com/docs/authentication/
        """
        token_manager = TokenManager()
        token_manager._read_token_from_aws_parameter_store()

        if token_manager.token and token_manager._is_expired():
            print("Access token expired, refreshing...")
            token_manager._refresh_from_strava()
            token_manager._write_token_to_aws_parameter_store()
        elif not token_manager.token:
            raise TokenManagerException("Token not found in Parameter Store")

        return token_manager.token["access_token"]

    def _refresh_from_strava(self) -> dict:
        client_id = ParameterStoreClient().get_parameter(
            CLIENT_ID_PARAMETER_STORE_KEY_PATH
        )
        client_secret = ParameterStoreClient().get_secret(
            CLIENT_SECRET_PARAMETER_STORE_KEY_PATH
        )

        url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": self.token["refresh_token"],
            "grant_type": "refresh_token",
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        self.token = response.json()
        if not self.token.get("access_token"):
            raise TokenManagerException("Missing 'access_token' field in JSON response")
        if not self.token.get("refresh_token"):
            raise TokenManagerException(
                "Missing 'refresh_token' field in JSON response"
            )
        if not self.token.get("expires_at"):
            raise TokenManagerException("Missing 'expires_at' field in JSON response")
        return self.token

    def _is_expired(self) -> bool:
        # `expires_at` is in seconds since the epoch.
        # Eg. 1691977531 for Monday, August 14, 2023 1:45:31 AM at GMT timezone.
        expires_at = self.token.get("expires_at")
        return expires_at <= time()

    def _read_token_from_file(self) -> Optional[dict]:
        try:
            with open(self.SECRET_FILE) as fin:
                content = fin.read()
        except FileNotFoundError:
            return None
        try:
            self.token = json.loads(content)
        except json.JSONDecodeError:
            return None

        if not self.token.get("access_token"):
            raise TokenManagerException("Missing 'access_token' field in 'secret' file")
        if not self.token.get("refresh_token"):
            raise TokenManagerException(
                "Missing 'refresh_token' field in 'secret' file"
            )
        if not self.token.get("expires_at"):
            raise TokenManagerException(
                "Missing 'expires_at' field in in 'secret' file"
            )
        return self.token

    def _write_token_to_file(self) -> None:
        with open(self.SECRET_FILE, "w") as fout:
            fout.write(json.dumps(self.token, indent=4))

    def _read_token_from_aws_parameter_store(self) -> Optional[dict]:
        token = ParameterStoreClient().get_secret(TOKEN_JSON_PARAMETER_STORE_KEY_PATH)
        self.token = json.loads(token)

        if not self.token.get("access_token"):
            raise TokenManagerException("Missing 'access_token' field in 'secret' file")
        if not self.token.get("refresh_token"):
            raise TokenManagerException(
                "Missing 'refresh_token' field in 'secret' file"
            )
        if not self.token.get("expires_at"):
            raise TokenManagerException(
                "Missing 'expires_at' field in in 'secret' file"
            )
        return self.token

    def _write_token_to_aws_parameter_store(self) -> None:
        ParameterStoreClient().put_secret(
            TOKEN_JSON_PARAMETER_STORE_KEY_PATH,
            json.dumps(self.token, indent=4),
            do_overwrite=True,
        )


class TokenManagerException(Exception):
    pass
