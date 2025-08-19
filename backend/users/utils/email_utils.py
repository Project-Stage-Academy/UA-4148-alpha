from django.conf import settings
from django.core.mail import send_mail


def send_activation_email(token=str, recipient_email=str, frontend_url=str):
    """
    Sends an activation email with HTML and plain text versions.
    """
    
    activation_url = f"{frontend_url}/verify-email?token={token}"
    
    plain_message = (
        f"Hello!\n\n"
        f"To activate your account, please click the link below or copy the token to the frontend POST /activate endpoint:\n"
        f"{activation_url}\n\n"
        f"Token: {token}\n\n"
        "Thank you!"
    )
    
    html_message = f"""
    <html>
    <body>
        <p>Hello!</p>
        <p>To activate your account, click the button below:</p>
        <a href="{activation_url}" 
           style="display:inline-block; background-color:#007bff; color:#ffffff; 
                  padding:12px 24px; text-decoration:none; border-radius:6px; font-weight:bold;">
           Activate your account
        </a>
        <p>If the button does not work, copy and paste the following URL into your browser:</p>
        <p>{activation_url}</p>
        <p>Thank you!</p>
    </body>
    </html>
    """
    
    send_mail(
        subject = "Verify your email",
        message = plain_message,
        html_message = html_message,
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [recipient_email],
        html_message = html_message,
        fail_silently =True, #TODO: Due to the lack of DEFAULT_FROM_EMAIL, set it to True for now so that these errors do not distract
    )
    return settings.DEFAULT_FROM_EMAIL