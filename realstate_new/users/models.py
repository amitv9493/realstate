from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from realstate_new.payment.models import Wallet
from realstate_new.utils import TrackingModel

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
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    job_preferences = MultiSelectField(choices=JOB_TYPES, default="SHOWING")
    email = models.EmailField(unique=True)
    # Preferences
    email_notification = models.BooleanField(default=True)
    whatsapp_notification = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=True)
    phone_notification = models.BooleanField(default=True)

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
    brokerage_name = models.CharField(
        max_length=200,
        blank=True,
    )  # also known as office_name

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

    def get_basic_info(self):
        "Returns users basic info"
        return {
            "last_login": self.last_login,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_active": self.is_active,
            "date_joined": self.date_joined,
            "phone": self.phone,
            "phone_country_code": self.phone_country_code,
        }

    def get_preferences(self):
        "Returns all uesr preferences related to a job."
        return {
            "email_notification": self.email_notification,
            "whatsapp_notification": self.whatsapp_notification,
            "push_notification": self.push_notification,
            "phone_notification": self.phone_notification,
            "job_preferences": self.job_preferences,
            "time_preference_start": self.time_preference_start,
            "time_preference_end": self.time_preference_end,
            "days_of_week_preferences": self.days_of_week_preferences,
            "mile_radius_preference": self.mile_radius_preference,
        }

    def get_all_license_info(self):
        """Returns all license related info"""
        return {
            "license_number": self.license_number,
            "license_issue_date": self.license_issue_date,
            "license_expiration_date": self.license_expiration_date,
            "license_status": self.license_status,
            "license_type": self.license_type,
            "license_jurisdiction": self.license_jurisdiction,
            "brokerage_name": self.brokerage_name,
            "suffix": self.suffix,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "state_province": self.state_province,
            "postal_code": self.postal_code,
            "country": self.country,
        }

    def get_required_license_info(self):
        "Returns only necessary license info."
        return {
            "license_number": self.license_number,
            "license_issue_date": self.license_issue_date,
            "license_expiration_date": self.license_expiration_date,
            "license_status": self.license_status,
            "license_type": self.license_type,
            "license_jurisdiction": self.license_jurisdiction,
            "suffix": self.suffix,
            "brokerage_name": self.brokerage_name,
        }


class ProfessionalDetail(TrackingModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="professional_details",
    )
    job_title = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    skills = models.CharField(max_length=255)


class EducationDetail(TrackingModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="education_details",
    )
    degree = models.CharField(max_length=50)
    institution_name = models.CharField(max_length=50)
    year_of_graduation = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
