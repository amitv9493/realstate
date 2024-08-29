import re

from django.db import models


class ThirdPartyCall(models.Model):
    status_code = models.PositiveIntegerField()
    request_body = models.TextField()
    response_body = models.TextField()
    endpoint = models.TextField()
    time_taken = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_created",)

    def __str__(self):
        return self.shortened_endpoint

    @property
    def shortened_endpoint(self):
        match = re.search(r".*?\.com", self.endpoint)
        shortened_endpoint = match.group(0) if match else self.endpoint

        return f"{self.status_code}, {shortened_endpoint}"
