import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body: str):
    """
    Helper function to send a plain text email via Gmail SMTP server using TLS.
    """
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_APP_PASSWORD")

    if not email_address or not email_password:
        print("[EMAIL ERROR] EMAIL_ADDRESS or EMAIL_APP_PASSWORD environment variables are missing.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        
        print(f"[EMAIL SUCCESS] Sent email to {to_email} with subject: '{subject}'")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")

def send_task_created_email(assignee_email: str, assignee_name: str, task_title: str):
    """
    Sends an email notification when a new task is assigned to a user.
    """
    subject = f"New Task Assigned: {task_title}"
    body = (
        f"Hello {assignee_name},\n\n"
        f"A new task has been assigned to you:\n\n"
        f"Task Title: {task_title}\n\n"
        f"Please check your dashboard to view the details and start working on it.\n\n"
        f"Best regards,\nTask Manager App"
    )
    send_email(to_email=assignee_email, subject=subject, body=body)

def send_task_completed_email(creator_email: str, creator_name: str, task_title: str):
    """
    Sends an email notification when a task created by a user is completed.
    """
    subject = f"Task Completed: {task_title}"
    body = (
        f"Hello {creator_name},\n\n"
        f"The following task created by you has been marked as completed:\n\n"
        f"Task Title: {task_title}\n\n"
        f"You can view your completed tasks in the dashboard.\n\n"
        f"Best regards,\nTask Manager App"
    )
    send_email(to_email=creator_email, subject=subject, body=body)
