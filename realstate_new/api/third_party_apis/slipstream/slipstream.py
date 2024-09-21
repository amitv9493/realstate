import requests

from config.settings.base import env
from realstate_new.api.third_party_apis import log_api


class SlipStreamApi:
    url = env("SLIPSTREAM_URL")
    public_key = env("SLIPSTREAM_PRIVATE_KEY")
    market = env("MARKET")

    @property
    def headers(self):
        return

    @log_api
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

    @log_api
    def get_agent_assigned_properties(self, mls_id):
        url = f"{self.url}/ws/listings/search"
        return requests.get(
            url,
            params={
                "authorization": self.public_key,
                "details": True,
                "id": mls_id,
                "market": self.market,
            },
            timeout=20,
        )
