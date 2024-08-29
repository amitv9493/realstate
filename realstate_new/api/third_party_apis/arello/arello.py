# ruff: noqa: TID252
import requests
from django.conf import settings

from ..logger import log_api

config = settings.CONFIG


class ArelloService:
    endpoint = config.get("arello", "endpoint")
    username = config.get("arello", "username")
    password = config.get("arello", "password")

    @log_api
    def get_license_info(self, user):
        return requests.post(
            self.endpoint,
            data={
                "username": self.username,
                "password": self.password,
                "jurisdiction": user.license_jurisdiction,
                "licenseNumber": user.license_number,
                "lastName": user.last_name,
                "firstName": user.first_name,
                "searchMode": "live",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
        )
