import os
from datetime import datetime, timedelta
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.enabled = bool(self.smtp_user and self.smtp_password)
        
        if not self.enabled:
            print("⚠️ [EMAIL] Email service disabled - SMTP credentials not configured")
    
    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Send an email"""
        if not self.enabled:
            print(f"⚠️ [EMAIL] Skipping email to {to_email} - service disabled")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ [EMAIL] Sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ [EMAIL] Failed to send to {to_email}: {e}")
            return False
    
    async def send_deadline_reminder(self, user_email: str, user_name: str, roadmap_title: str, days_left: int):
        """Send deadline reminder email"""
        subject = f"⏰ Deadline Reminder: {roadmap_title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Deadline Approaching!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>This is a friendly reminder that your learning roadmap <strong>{roadmap_title}</strong> is approaching its deadline.</p>
                    <p><strong>Days remaining: {days_left}</strong></p>
                    <p>Don't worry! You still have time to make progress. Keep up the great work!</p>
                    <a href="http://localhost:3000/roadmap" class="button">View My Roadmaps</a>
                    <p style="margin-top: 30px; font-size: 14px; color: #666;">
                        Stay consistent and you'll reach your learning goals! 🎯
                    </p>
                </div>
                <div class="footer">
                    <p>PathForge - AI-forged learning roadmaps to your career</p>
                    <p>You're receiving this because you have an active learning roadmap with us.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_module_completion_congrats(self, user_email: str, user_name: str, module_title: str, roadmap_title: str):
        """Send congratulations email for module completion"""
        subject = f"🎉 Congratulations! Module Completed: {module_title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .achievement {{ background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Amazing Progress!</h1>
                </div>
                <div class="content">
                    <h2>Congratulations, {user_name}!</h2>
                    <div class="achievement">
                        <h3>✅ Module Completed</h3>
                        <p><strong>{module_title}</strong></p>
                        <p>Roadmap: {roadmap_title}</p>
                    </div>
                    <p>You're one step closer to your career goals! Keep this momentum going.</p>
                    <a href="http://localhost:3000/roadmap" class="button">Continue Learning</a>
                </div>
                <div class="footer">
                    <p>PathForge - Building your career, one module at a time</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)
    
    async def send_weekly_progress_report(self, user_email: str, user_name: str, stats: dict):
        """Send weekly progress report"""
        subject = "📊 Your Weekly Learning Progress"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stat-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; display: flex; justify-content: space-between; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Your Weekly Progress</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>Here's your learning activity for the past week:</p>
                    
                    <div class="stat-box">
                        <span>Time Spent Learning</span>
                        <span class="stat-value">{stats.get('hours_spent', 0)}h</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Resources Completed</span>
                        <span class="stat-value">{stats.get('resources_completed', 0)}</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Current Streak</span>
                        <span class="stat-value">{stats.get('streak_days', 0)} days</span>
                    </div>
                    
                    <div class="stat-box">
                        <span>Progress Made</span>
                        <span class="stat-value">+{stats.get('progress_increase', 0)}%</span>
                    </div>
                    
                    <p style="margin-top: 30px;">
                        {stats.get('motivation_message', 'Keep up the great work! Consistency is key to mastering new skills.')}
                    </p>
                    
                    <a href="http://localhost:3000/dashboard" class="button">View Full Stats</a>
                </div>
                <div class="footer">
                    <p>PathForge - Track your progress, achieve your goals</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_content)

# Global instance
email_service = EmailService()
