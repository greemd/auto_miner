from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

def send_notification(subject: str, message: str) -> None:
    """Sends a notification (e.g., email, Slack, console)."""
    # Placeholder for actual notification logic (email, Slack, etc.)
    logger.info(f"[NOTIFICATION] Subject: {subject}, Message: {message}")
    print(f"[NOTIFICATION] Subject: {subject}, Message: {message}")


def send_success_notification(task_name: str, details: str) -> None:
    subject = f"[Auto Alpha Miner] Task Succeeded: {task_name}"
    message = f"The task \'{task_name}\' completed successfully.\n\nDetails:\n{details}"
    send_notification(subject, message)


def send_failure_notification(task_name: str, error_message: str) -> None:
    subject = f"[Auto Alpha Miner] Task Failed: {task_name}"
    message = f"The task \'{task_name}\' failed with an error.\n\nError:\n{error_message}"
    send_notification(subject, message)
