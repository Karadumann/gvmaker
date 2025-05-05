"""
Feedback dialog module for sending user feedback via email.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class FeedbackDialog(simpledialog.Dialog):
    """
    Dialog for collecting and sending user feedback via email.
    """
    
    def body(self, master):
        ttk.Label(master, text="We value your feedback! Please let us know your thoughts or suggestions:").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(master, text="Your Email (optional):").grid(row=1, column=0, sticky="e", padx=5)
        self.email_entry = ttk.Entry(master, width=40)
        self.email_entry.grid(row=1, column=1, pady=5)
        ttk.Label(master, text="Feedback:").grid(row=2, column=0, sticky="ne", padx=5)
        self.feedback_text = tk.Text(master, width=40, height=8)
        self.feedback_text.grid(row=2, column=1, pady=5)
        self.status_label = ttk.Label(master, text="", foreground="red")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        return self.feedback_text

    def validate(self):
        feedback = self.feedback_text.get("1.0", "end").strip()
        if not feedback:
            self.status_label.config(text="Feedback cannot be empty!")
            return 0
        self.status_label.config(text="")
        return 1

    def apply(self):
        feedback = self.feedback_text.get("1.0", "end").strip()
        user_email = self.email_entry.get().strip()
        try:
            self.send_feedback_email(feedback, user_email)
            messagebox.showinfo("Thank you!", "Your feedback has been sent. Thank you for helping us improve!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send feedback: {str(e)}")

    def send_feedback_email(self, feedback, user_email):
        smtp_server = "smtp.turkticaret.net"
        smtp_port = 587
        sender_email = os.environ.get("FEEDBACK_EMAIL")
        sender_password = os.environ.get("FEEDBACK_PASSWORD")
        receiver_email = os.environ.get("FEEDBACK_RECEIVER", sender_email)
        subject = "GV Maker User Feedback"
        body = f"Feedback:\n{feedback}\n\nUser Email: {user_email if user_email else 'N/A'}"
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string()) 