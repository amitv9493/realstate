from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from realstate_new.payment.models import Wallet

JOB_TYPES = (
    ("SHOWING", "Showing"),
    ("OPEN_HOUSE", "Open House"),
    ("LOCKBOX", "Lockbox Install/Remove"),
    ("SIGN", "Sign Install/Remove"),
    ("RUNNER", "Runner Task"),
    ("PROFESSIONAL", "Professional Services"),
)

DAYS_OF_WEEK = (
    ("MON", "Monday"),
    ("TUE", "Tuesday"),
    ("WED", "Wednesday"),
    ("THU", "Thursday"),
    ("FRI", "Friday"),
    ("SAT", "Saturday"),
    ("SUN", "Sunday"),
)


class User(AbstractUser):
    job_preferences = MultiSelectField(choices=JOB_TYPES, blank=True, default="SHOWING")

    # Time Preferences
    time_preference_start = models.TimeField(blank=True, default=now)
    time_preference_end = models.TimeField(blank=True, default=now)

    days_of_week_preferences = MultiSelectField(
        choices=DAYS_OF_WEEK,
        blank=True,
        default="MON",
    )

    mile_radius_preference = models.PositiveIntegerField(
        default=10,
        help_text=_("Maximum distance (in miles) willing to travel for work"),
    )

    # License Information
    license_number = models.CharField(
        max_length=50,
    )
    license_issue_date = models.DateField(blank=True, default=now)
    license_expiration_date = models.DateField(blank=True, default=now)
    license_status = models.CharField(
        max_length=20,
        blank=True,
    )
    license_type = models.CharField(
        max_length=50,
        blank=True,
    )
    license_jurisdiction = models.CharField(
        max_length=50,
    )

    # Additional License Information (to be populated by API)
    suffix = models.CharField(
        max_length=20,
        blank=True,
    )
    office_name = models.CharField(
        max_length=200,
        blank=True,
    )
    phone = models.CharField(max_length=20, default="")
    phone_country_code = models.CharField(max_length=20, default="")
    fax = models.CharField(
        max_length=20,
        blank=True,
    )
    address_line1 = models.CharField(
        max_length=200,
        blank=True,
    )
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
    )
    city = models.CharField(
        max_length=100,
        blank=True,
    )
    state_province = models.CharField(
        max_length=50,
        blank=True,
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )
    country = models.CharField(
        max_length=50,
        blank=True,
    )

    @property
    def total_reviews(self):
        return self.review_creator.count()

    @property
    def average_rating(self):
        return self.review_creator.all().aggregate(Avg("rating"))["rating__avg"] or None

    def get_recent_reviews(self, limit=5):
        return self.review_creator.all()[:limit]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            Wallet.objects.create(user=self, balance=00.00)
