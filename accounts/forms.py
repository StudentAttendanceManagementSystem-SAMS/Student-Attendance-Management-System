from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm


class SamsAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Invalid username or password. Please try again.",
        "inactive": "This account is inactive.",
    }
    FAILURE_SESSION_KEY = "sams_login_failures"
    FAILURE_STARTED_KEY = "sams_login_failure_started_at"
    WARNING_THRESHOLD = 3
    FAILURE_WINDOW_SECONDS = 15 * 60

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        self.request.session.pop(self.FAILURE_SESSION_KEY, None)
        self.request.session.pop(self.FAILURE_STARTED_KEY, None)

    def clean(self):
        try:
            return super().clean()
        except ValidationError:
            now = timezone.now().timestamp()
            started_at = self.request.session.get(self.FAILURE_STARTED_KEY)
            if (
                started_at is None
                or now - started_at > self.FAILURE_WINDOW_SECONDS
            ):
                failures = 0
                self.request.session[self.FAILURE_STARTED_KEY] = now
            else:
                failures = self.request.session.get(self.FAILURE_SESSION_KEY, 0)
            failures += 1
            self.request.session[self.FAILURE_SESSION_KEY] = failures
            if failures >= self.WARNING_THRESHOLD:
                raise ValidationError(
                    "Multiple unsuccessful login attempts detected. "
                    "Check your credentials carefully before trying again.",
                    code="repeated_login_failure",
                )
            raise
