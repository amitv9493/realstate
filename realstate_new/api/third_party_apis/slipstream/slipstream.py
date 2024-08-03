import requests
from django.conf import settings

config = settings.CONFIG


class SlipStreamApi:
    url = config.get("slipstream", "url")
    public_key = config.get("slipstream", "public_key")

    @property
    def headers(self):
        return

    def get_zipcode_details(self, zipcode: list):
        url = f"{self.url}/ws/areas/zipcodes/get"
        zipcode_param = "".join(str(i) + "|" for i in zipcode)[:-1]
        return requests.get(
            url,
            params={
                "id": zipcode_param,
                "authorization": self.public_key,
            },
            timeout=20,
        )

    def get_agent_assigned_properties(self, license_number, market):
        url = f"{self.url}/ws/listings/search"
        return requests.get(
            url,
            params={
                "agent.licenseNumber": license_number,
                "authorization": self.public_key,
                "market": market,
            },
            timeout=20,
        )
