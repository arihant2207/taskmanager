import os
import traceback
import resend

def send_email(to_email: str, subject: str, html_body: str):
    """
    Helper function to send an HTML email via Resend REST API (HTTPS).
    Avoids outbound SMTP blocking issues on platform hosts like Render.
    """
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        print("[EMAIL WARNING] RESEND_API_KEY environment variable is missing. Skipping email notification.", flush=True)
        return

    resend.api_key = api_key

    try:
        print(f"[EMAIL START] Sending email via Resend to {to_email} with subject: '{subject}'...", flush=True)
        params = {
            "from": "Task Manager <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        email_resp = resend.Emails.send(params)
        print(f"[EMAIL SUCCESS] Sent email to {to_email}, Response: {email_resp}", flush=True)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email} via Resend: {e}", flush=True)
        traceback.print_exc()

def send_task_created_email(assignee_email: str, assignee_name: str, task_title: str):
    """
    Sends an email notification when a new task is assigned to a user.
    """
    if not assignee_email:
        print("[EMAIL WARNING] assignee_email is missing, skipping email.", flush=True)
        return

    subject = f"New Task Assigned: {task_title}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4f46e5; margin-bottom: 16px;">Hello {assignee_name},</h2>
        <p style="font-size: 16px; margin-bottom: 16px;">A new task has been assigned to you in <strong>Task Manager</strong>:</p>
        <div style="background-color: #f3f4f6; border-left: 4px solid #4f46e5; padding: 16px; border-radius: 4px; margin-bottom: 24px;">
            <p style="font-size: 18px; font-weight: bold; margin: 0;">{task_title}</p>
        </div>
        <p style="font-size: 14px; color: #4b5563; margin-bottom: 24px;">Please check your dashboard to view the details and start working on it.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin-bottom: 24px;" />
        <p style="font-size: 12px; color: #9ca3af; margin: 0;">Task Manager Notification System</p>
    </div>
    """
    send_email(to_email=assignee_email, subject=subject, html_body=html_body)

def send_task_completed_email(creator_email: str, creator_name: str, task_title: str):
    """
    Sends an email notification when a task created by a user is completed.
    """
    if not creator_email:
        print("[EMAIL WARNING] creator_email is missing, skipping email.", flush=True)
        return

    subject = f"Task Completed: {task_title}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #10b981; margin-bottom: 16px;">Hello {creator_name},</h2>
        <p style="font-size: 16px; margin-bottom: 16px;">The following task created by you has been marked as <strong>Completed</strong>:</p>
        <div style="background-color: #f3f4f6; border-left: 4px solid #10b981; padding: 16px; border-radius: 4px; margin-bottom: 24px;">
            <p style="font-size: 18px; font-weight: bold; margin: 0;">{task_title}</p>
        </div>
        <p style="font-size: 14px; color: #4b5563; margin-bottom: 24px;">You can view your completed tasks on your dashboard.</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin-bottom: 24px;" />
        <p style="font-size: 12px; color: #9ca3af; margin: 0;">Task Manager Notification System</p>
    </div>
    """
    send_email(to_email=creator_email, subject=subject, html_body=html_body)
