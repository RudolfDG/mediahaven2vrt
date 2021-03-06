import functools
import time

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException


class AuthenticationException(Exception):
    """Exception raised when authentication fails."""

    pass


class MediahavenService:
    def __init__(self, config: dict = None):
        self.cfg: dict = config
        self.token_info = None

    def __authenticate(function):
        @functools.wraps(function)
        def wrapper_authenticate(self, *args, **kwargs):
            if not self.token_info:
                self.token_info = self.__get_token()
            try:
                return function(self, *args, **kwargs)
            except AuthenticationException as error:
                self.token_info = self.__get_token()
            return function(self, *args, **kwargs)

        return wrapper_authenticate

    def __get_token(self) -> str:
        """Gets an OAuth token that can be used in mediahaven requests to authenticate."""
        user: str = self.cfg["environment"]["mediahaven"]["username"]
        password: str = self.cfg["environment"]["mediahaven"]["password"]
        url: str = self.cfg["environment"]["mediahaven"]["host"] + "/oauth/access_token"
        payload = {"grant_type": "password"}

        try:
            r = requests.post(
                url,
                auth=HTTPBasicAuth(user.encode("utf-8"), password.encode("utf-8")),
                data=payload,
            )

            if r.status_code != 201:
                raise RequestException(
                    f"Failed to get a token. Status: {r.status_code}"
                )
            token_info = r.json()
        except RequestException as e:
            raise e
        return token_info

    @__authenticate
    def get_fragment(self, fragment_id: str) -> dict:
        url: str = (self.cfg["environment"]["mediahaven"]["host"] + "/media/")

        headers: dict = {
            "Authorization": f"Bearer {self.token_info['access_token']}",
            "Accept": "application/vnd.mediahaven.v2+json",
        }

        params: dict = {
            "q": f'%2b(fragmentId:"{fragment_id}")',
            "nrOfResults": 1,
        }

        response = requests.get(url, headers=headers, params=params,)

        if response.status_code == 401:
            # AuthenticationException triggers a retry with a new token
            raise AuthenticationException(response.text)

        return response.json()
