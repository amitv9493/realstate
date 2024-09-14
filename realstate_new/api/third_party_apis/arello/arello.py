# ruff: noqa: TID252
import requests

from config.settings.base import env

from ..logger import log_api


class ArelloService:
    endpoint = env("ARELLO_ENDPOINT")
    username = env("ARELLO_USERNAME")
    password = env("ARELLO_PASSWORD")
    search_mode = env("ARELLO_SEARCH_MODE")

    @log_api
    def get_license_info(self, vals):
        data = {
            "username": self.username,
            "password": self.password,
            "jurisdiction": vals.get("license_jurisdiction"),
            "licenseNumber": vals.get("license_number"),
            "lastName": vals.get("last_name"),
            "firstName": vals.get("first_name"),
            "searchMode": self.search_mode,
        }
        data = {k: v for k, v in data.items() if v}
        return requests.post(
            self.endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
            data=data,
        )
