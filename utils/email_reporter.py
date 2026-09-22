import os
import smtplib
from pathlib import Path
from email.message import EmailMessage


REPORT_DIR = Path("reports")


def send_email():
    username = os.getenv("GMAIL_USERNAME")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not username or not app_password:
        print("Email notification skipped: Gmail credentials are not set.")
        return

    pytest_report = REPORT_DIR / "pytest-report.html"
    manager_report = REPORT_DIR / "manager-summary.html"

    message = EmailMessage()

    message["From"] = username
    message["To"] = username
    message["Subject"] = "Selenium Python Pytest - Test Report"

    message.set_content(
        "Hello,\n\n"
        "Selenium Python Pytest test execution is complete.\n\n"
        "Manager Summary Report:\n"
        "The manager summary report is attached to this email.\n\n"
        "Detailed Pytest Report:\n"
        "http://localhost:8000/pytest-report.html\n\n"
        "Regards,\n"
        "Selenium Python Pytest Automation Framework"
    )

    for report_file in [manager_report]:

        if not report_file.exists():
            print(f"Report file not found: {report_file}")
            continue

        with report_file.open("rb") as file:
            file_data = file.read()

        message.add_attachment(
            file_data,
            maintype="text",
            subtype="html",
            filename=report_file.name
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(username, app_password)
            server.send_message(message)

        print("Email sent successfully.")

    except Exception as exc:
        print(f"Email notification error: {exc}")


if __name__ == "__main__":
    send_email()