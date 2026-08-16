import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_login import current_user

def generate_reset_token(email):
    """Generate a secure token for password reset"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=1800):
    """Verify the reset token and return email if valid"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=expiration  # 30 minutes
        )
        return email
    except:
        return None

def send_reset_email(user_email, reset_link, username):
    """Send password reset email using Gmail SMTP"""
    try:
        # Email configuration
        sender_email = current_app.config['MAIL_USERNAME']
        sender_password = current_app.config['MAIL_PASSWORD']
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset Request - Flask Auth App'
        msg['From'] = sender_email
        msg['To'] = user_email
        
        # Plain text version
        text = f"""
        Hello {username},
        
        We received a request to reset your password. Click the link below to reset it:
        
        {reset_link}
        
        This link will expire in 30 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Flask Auth App Team
        """
        
        # HTML version (better looking)
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; border: 1px solid #dee2e6;">
                    <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
                    <hr style="border: 1px solid #dee2e6; margin: 20px 0;">
                    
                    <p style="font-size: 16px; color: #555;">Hello <strong>{username}</strong>,</p>
                    
                    <p style="font-size: 16px; color: #555;">We received a request to reset your password. Click the button below to reset it:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #888;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="font-size: 14px; color: #888; word-break: break-all;">{reset_link}</p>
                    
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 14px; color: #856404;">
                            ⚠️ This link will expire in <strong>30 minutes</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 14px; color: #888;">If you didn't request this, please ignore this email.</p>
                    
                    <hr style="border: 1px solid #dee2e6; margin: 20px 0;">
                    
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        Best regards,<br>
                        <strong>Flask Auth App Team</strong>
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Attach both versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False