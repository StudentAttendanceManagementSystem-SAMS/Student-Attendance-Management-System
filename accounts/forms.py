from django.contrib.auth.forms import AuthenticationForm


class SamsAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Invalid username or password. Please try again.",
        "inactive": "This account is inactive.",
    }
