import contextlib
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from realstate_new.application.models import JobApplication
from realstate_new.notification.models import Notification
from realstate_new.payment.models.stripe import StripeTranscation
from realstate_new.utils.base_models import TrackingModel

from .choices import BrokerageType
from .choices import JobType
from .choices import TaskStatusChoices
from .verification_image import VerificationDocument


class BaseTask(TrackingModel):
    client_name = models.CharField(max_length=50, default="", blank=True)
    client_phone = ArrayField(
        base_field=models.CharField(max_length=50),
        null=True,
        blank=True,
    )
    client_email = ArrayField(base_field=models.EmailField(), null=True, blank=True)

    task_time = models.DateTimeField()
    asap = models.BooleanField(_("As Soon As Possible"), default=False)
    notes = models.TextField(blank=True, default="")

    payment_amount = models.DecimalField(max_digits=6, decimal_places=2)
    is_verified = models.BooleanField(default=False)
    application_type = models.CharField(
        max_length=5,
        choices=JobType.choices,
        default=JobType.apply,
    )
    apply_deadline = models.DateTimeField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_assigned",
    )
    brokerage = models.CharField(
        max_length=50,
        choices=BrokerageType.choices,
        default=BrokerageType.my_brokerage,
    )

    show_client_info = models.BooleanField(default=False)

    # extra info

    not_acceptance_notification_sent = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    marked_completed_by_assignee = models.BooleanField(default=False)
    audio_file = models.FileField(
        upload_to="additional-audio-notes/",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        default=TaskStatusChoices.CREATED,
        choices=TaskStatusChoices.choices,
    )
    # GenericRelations
    notifications = GenericRelation(Notification)
    applications = GenericRelation(JobApplication)
    txn = GenericRelation(StripeTranscation)

    verification_images = GenericRelation(VerificationDocument)
    payment_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client_name}-{self.payment_amount}"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if (
            self.assigned_to
            and not self._state.adding
            and self.status == TaskStatusChoices.ASSIGNED
        ):
            self.change_assigned_user_application_status()
            self.reject_all_other_applications()
        return super().save(*args, **kwargs)

    def change_assigned_user_application_status(self):
        with contextlib.suppress(JobApplication.DoesNotExist):
            user_application = self.applications.all().get(applicant=self.assigned_to)
            if user_application:
                user_application.status = "ACCEPTED"
                user_application.save()

    def reject_all_other_applications(self):
        qs = self.applications.all().exclude(applicant=self.assigned_to)
        if qs:
            qs.update(status="REJECTED")

    @property
    def stripe_fees(self):
        payable_amt = self.payment_amount if self.payment_amount else 5
        return ((payable_amt * Decimal(settings.STRIPE_FEE_PERCENT)) / 100) + Decimal(
            settings.STRIPE_FIXED_FEE,
        )

    @property
    def platform_fees(self):
        if self.payment_amount:
            return (self.payment_amount * Decimal(settings.PLATFORM_FEES_PERCENT)) / 100
        return Decimal(5.0)

    @property
    def payment_amt_for_task_creater(self):
        return self.payment_amount

    @property
    def payment_amt_for_payout(self):
        if self.payment_amount:
            return self.payment_amount * (1 - (settings.PLATFORM_FEES_PERCENT / 100))
        return Decimal(0)

    @property
    def payment_for_instance_payout(self):
        if self.payment_amount:
            instant_charges = (self.payment_amount * 1) / 100
            amt = self.payment_amount - instant_charges - self.platform_fees
            return round(amt, 2)
        return Decimal(0)
