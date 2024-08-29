# ruff: noqa: TID252
import requests
from django.conf import settings

from ..logger import log_api

config = settings.CONFIG


class ArelloService:
    endpoint = config.get("arello", "endpoint")
    username = config.get("arello", "username")
    password = config.get("arello", "password")
    search_mode = config.get("arello", "search_mode")

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
