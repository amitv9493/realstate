import logging

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Avg
from django.db.models import Index
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from realstate_new.task.models import JOB_TYPE_MAPPINGS
from realstate_new.utils import TrackingModel

_logger = logging.getLogger(__name__)
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


def upload_to(instance, filename):
    return f"uploads/{instance.username}/{filename}"


class Rating(models.Model):
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="ratings",
        on_delete=models.CASCADE,
    )
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="ratings_given",
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.content_object} {self.rating}"


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    profile_picture = models.ImageField(upload_to=upload_to, null=True, blank=True)
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
    ratings = GenericRelation(Rating)

    hyperwallet_token = models.TextField(default="")
    stripe_customer_id = models.TextField(default="")
    stripe_account_id = models.TextField(default="", blank=True)
    is_details_submitted = models.BooleanField(default=False)
    is_charges_enabled = models.BooleanField(default=False)
    is_payouts_enabled = models.BooleanField(default=False)

    class Meta:
        indexes = [Index(fields=["email"], name="idx_email")]

    @property
    def total_reviews(self):
        return self.ratings.count()

    @property
    def average_rating(self):
        return float(self.ratings.all().aggregate(Avg("rating"))["rating__avg"]) or None

    def get_recent_ratings(self, limit=5):
        raise NotImplementedError

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_jobs_completed_qs(self):
        """
        Returns a queryset jobs completed by a this user.
        """
        return [job.objects.filter(assigned_to=self) for job in JOB_TYPE_MAPPINGS.values()]

    @property
    def basic_info(self):
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
            "profile_picture": self.profile_picture,
        }

    @property
    def preferences(self):
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

    @property
    def license_info(self):
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

    @property
    def required_license_info(self):
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

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                customer = stripe.Customer.create(
                    name=f"{self.get_full_name()}",
                    email=self.email,
                )
            except Exception:
                msg = f"unable to create stripe customer for user {self.email}"
                _logger.exception(msg)
            else:
                self.stripe_customer_id = customer.id

        super().save(*args, **kwargs)


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


class FCMDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fcmdevices")
    device_type = models.CharField(max_length=55, blank=True, default="")
    registration_id = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s device"
