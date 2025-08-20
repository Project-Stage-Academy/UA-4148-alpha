from django.conf import settings
from django.core.mail import send_mail


def send_activation_email(token=str, recipient_email=str, frontend_url=str):
    """
    Sends an activation email with HTML and plain text versions.
    """

    activation_url = f"{frontend_url}/activate_page?token={token}"

    plain_message = (
        "Hello!\n\n"
        "Copy the token below and send it to the frontend POST /activate endpoint:\n"
        f"{token}\n\n"
        "Thank you!"
    )

    html_message = f"""
    <html>
    <body>
        <p>Hello!</p>
        <p>Click the button below to activate your account:</p>
        <form action="{activation_url}" method="POST" style="display:inline;">
            <input type="hidden" name="token" value="{token}">
            <button type="submit">Activate your account</button>
        </form>
        <p>Thank you!</p>
    </body>
    </html>
    """

    send_mail(
        subject="Activate your account",
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=True,  # TODO: Due to the lack of DEFAULT_FROM_EMAIL, set it to True for now so that these errors do not distract
    )
    return settings.DEFAULT_FROM_EMAIL
