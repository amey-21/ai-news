import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def build_plain_text(articles: list[dict]) -> str:
    """
    Build a plain text fallback version of the digest.

    Why does this exist?
    MIMEMultipart("alternative") requires BOTH a plain text
    and HTML version. Some email clients (terminal clients,
    accessibility tools) can't render HTML they fall back
    to plain text. Without this, those clients show a blank email.

    This doesn't need to be beautiful — just readable.
    """
    lines = ["AI Digest\n", "="*40 + "\n"]

    # Group by topic for readability
    current_topic = None
    for article in articles:
        if article["topic"] != current_topic:
            current_topic = article["topic"]
            lines.append(f"\n{current_topic.upper()}\n{'-'*40}")

        lines.append(f"\n{article['title']}")
        lines.append(f"{article['summary']}")
        lines.append(f"Read more: {article['url']}\n")

    return "\n".join(lines)


def send_digest(html_content: str, articles: list[dict], date_str: str) -> None:
    """
    Send the HTML digest via Gmail SMTP.

    Args:
        html_content:  Complete HTML string from digest_builder
        articles:      List of summarized article dicts (for plain text fallback)
        date_str:      Human-readable date for email subject line

    Why does this function take both html_content AND articles?
    html_content → used for the HTML part of the email
    articles     → used to build the plain text fallback version
    We need both because MIMEMultipart("alternative") requires both.
    """

    # Step 1: Load credentials from environment
    # Never hardcode these — always read from .env
    sender_email    = os.getenv("GMAIL_ADDRESS")
    app_password    = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # Validate all required env vars are present before attempting connection
    # Fail fast with a clear message rather than a cryptic SMTP auth error
    missing = [
        name for name, val in {
            "GMAIL_ADDRESS":    sender_email,
            "GMAIL_APP_PASSWORD": app_password,
            "RECIPIENT_EMAIL":  recipient_email,
        }.items() if not val
    ]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Check your .env file."
        )

    # Step 2: Build the email message object
    # MIMEMultipart("alternative") = container for multiple representations
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 AI Digest — {date_str}"
    msg["From"]    = sender_email
    msg["To"]      = recipient_email

    # Step 3: Attach both versions
    # IMPORTANT: attach plain text FIRST, HTML second
    # Why? Email clients read parts in order and use the LAST one they support
    # Since all modern clients support HTML, HTML must come last
    plain_text = build_plain_text(articles)
    part_text  = MIMEText(plain_text, "plain")
    part_html  = MIMEText(html_content, "html")

    msg.attach(part_text)   # fallback — attached first
    msg.attach(part_html)   # preferred — attached last

    # Step 4: Connect to Gmail SMTP and send
    # SMTP_SSL creates encrypted connection immediately on connect (port 465)
    # Alternative is SMTP + starttls (port 587) — upgrades to encrypted after connect
    # Both are secure; SMTP_SSL is simpler for our use case
    try:
        print(f"[Email] Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

            # Login with sender address and App Password (NOT your Gmail password)
            server.login(sender_email, app_password)
            print(f"[Email] Authenticated successfully.")

            # Send the email
            server.sendmail(
                from_addr=sender_email,
                to_addrs=recipient_email,
                msg=msg.as_string()
            )

        print(f"[Email] Digest sent successfully to {recipient_email}")

    except smtplib.SMTPAuthenticationError:
        # Specific exception for wrong credentials
        # Gives a clearer error than generic Exception
        raise RuntimeError(
            "Gmail authentication failed.\n"
            "Make sure you're using an App Password, not your Gmail password.\n"
            "Generate one at: https://myaccount.google.com/apppasswords"
        )
    except smtplib.SMTPException as e:
        # All other SMTP errors — connection refused, timeout, etc.
        raise RuntimeError(f"Failed to send email: {e}")