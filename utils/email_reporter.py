# import os
# import smtplib
# from pathlib import Path
# from email.message import EmailMessage
#
#
# REPORT_DIR = Path("reports")
#
#
# def send_email():
#     username = os.getenv("GMAIL_USERNAME")
#     app_password = os.getenv("GMAIL_APP_PASSWORD")
#
#     if not username or not app_password:
#         print("Email notification skipped: Gmail credentials are not set.")
#         return
#
#     pytest_report = REPORT_DIR / "pytest-report.html"
#     manager_report = REPORT_DIR / "manager-summary.html"
#
#     message = EmailMessage()
#
#     message["From"] = username
#     message["To"] = username
#     message["Subject"] = "Selenium Python Pytest - Test Report"
#
#     message.set_content(
#         "Hello,\n\n"
#         "Selenium Python Pytest test execution is complete.\n\n"
#         "Manager Summary Report:\n"
#         "The manager summary report is attached to this email.\n\n"
#         "Detailed Pytest Report:\n"
#         "http://localhost:8000/pytest-report.html\n\n"
#         "Regards,\n"
#         "Selenium Python Pytest Automation Framework"
#     )
#
#     for report_file in [manager_report]:
#
#         if not report_file.exists():
#             print(f"Report file not found: {report_file}")
#             continue
#
#         with report_file.open("rb") as file:
#             file_data = file.read()
#
#         message.add_attachment(
#             file_data,
#             maintype="text",
#             subtype="html",
#             filename=report_file.name
#         )
#
#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(username, app_password)
#             server.send_message(message)
#
#         print("Email sent successfully.")
#
#     except Exception as exc:
#         print(f"Email notification error: {exc}")
#
#
# if __name__ == "__main__":
#     send_email()

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

    # Jenkins provides BUILD_URL automatically.
    # When running locally, BUILD_URL will not exist,
    # so we use the local report server URLs.
    #build_url = os.getenv("BUILD_URL")

    # if build_url:
    #     manager_report_url = f"{build_url}Manager_Report/"
    #     pytest_report_url = f"{build_url}Pytest_HTML_Report/"
    # else:
    #     manager_report_url = "http://localhost:8000/manager-summary.html"
    #     pytest_report_url = "http://localhost:8000/pytest-report.html"
    #
    # message = EmailMessage()

    job_url = os.getenv("JOB_URL")

    if job_url:
        manager_report_url = f"{job_url}Manager_20Report/"
        pytest_report_url = f"{job_url}Detailed_20Pytest_20Report/"
    else:
        manager_report_url = "http://localhost:8000/manager-summary.html"
        pytest_report_url = "http://localhost:8000/pytest-report.html"

    message = EmailMessage()

    message["From"] = username
    message["To"] = username
    message["Subject"] = "Selenium Python Pytest - Test Report"

    message.set_content(
        "Hello,\n\n"
        "Selenium Python Pytest test execution is complete.\n\n"
        "Manager Summary Report:\n"
        "The manager summary report is attached to this email.\n\n"
        f"Manager Report:\n"
        f"{manager_report_url}\n\n"
        "Detailed Pytest Report:\n"
        f"{pytest_report_url}\n\n"
        "Regards,\n"
        "Selenium Python Pytest Automation Framework"
    )

    # Attach only the manager report.
    # Gmail previously blocked pytest-report.html as an attachment.
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