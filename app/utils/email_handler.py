from pydantic import BaseModel, EmailStr
import os
import requests
from app.config import MAIL_API_KEY, DOMAIN, SENDER_EMAIL, SENDER_NAME

class EmailVerification(BaseModel):
    email: EmailStr
    verification_url: str

async def send_verification_email(email: EmailStr, url: str):
    api_key = MAIL_API_KEY
    domain = DOMAIN
    sender_email = SENDER_EMAIL
    sender_name = SENDER_NAME
    from_address = f"{sender_name} <{sender_email}>"
    
    # HTML version of email
    html_content = f"""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {{
            color-scheme: light dark;
        }}
        
        body {{
            font-family: 'Inter', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 600px;
            margin: 20px auto;
            border-radius: 16px;
            overflow: hidden;
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            box-shadow: 0 8px 32px rgba(123, 31, 162, 0.1);
        }}
        
        .header {{
            background: linear-gradient(to right, #9333ea, #ec4899);
            color: white;
            padding: 24px;
            text-align: center;
            position: relative;
        }}
        
        .logo-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 8px;
        }}
        
        .logo {{
            width: 40px;
            height: 40px;
            background: linear-gradient(to right, #9333ea, #ec4899);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
        }}
        
        .logo svg {{
            width: 20px;
            height: 20px;
        }}
        
        .brand-name {{
            font-size: 24px;
            font-weight: bold;
            color: white;
        }}
        
        .content {{
            padding: 32px 24px;
            position: relative;
            z-index: 1;
        }}
        
        .button {{
            display: inline-block;
            background: linear-gradient(to right, #9333ea, #ec4899);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            margin: 24px 0;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
        }}
        
        .button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(236, 72, 153, 0.4);
        }}
        
        .footer {{
            border-top: 1px solid #e5e7eb;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
        }}
        
        .pro-badge {{
            display: inline-flex;
            align-items: center;
            background-color: #f3e8ff;
            border-radius: 16px;
            padding: 6px 12px;
            margin: 16px 0;
        }}
        
        .pro-badge svg {{
            width: 12px;
            height: 12px;
            margin-right: 6px;
            color: #9333ea;
        }}
        
        .pro-badge span {{
            font-size: 12px;
            font-weight: 500;
            color: #9333ea;
        }}
        
        .url-text {{
            background-color: #f9fafb;
            border-radius: 8px;
            padding: 12px;
            word-break: break-all;
            font-size: 14px;
            color: #4b5563;
            border: 1px solid #e5e7eb;
        }}
        
        .premium-box {{
            margin-top: 32px;
            padding: 16px;
            background-color: #fdf4ff;
            border-radius: 12px;
            border: 1px solid #f5d0fe;
        }}
        
        .premium-button {{
            display: block;
            background: linear-gradient(to right, #9333ea, #ec4899);
            text-align: center;
            padding: 10px;
            border-radius: 8px;
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
        }}
        
        @media (prefers-color-scheme: dark) {{
            body {{
                color: #f8f9fa;
                background-color: #121212;
            }}
            
            .container {{
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px rgba(123, 31, 162, 0.2);
            }}
            
            .footer {{
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.6);
            }}
            
            .pro-badge {{
                background-color: rgba(255, 255, 255, 0.1);
                color: #d8b4fe;
            }}
            
            .pro-badge svg {{
                color: #d8b4fe;
            }}
            
            .pro-badge span {{
                color: #c4b5fd;
            }}
            
            .url-text {{
                background-color: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .premium-box {{
                background-color: rgba(147, 51, 234, 0.1);
                border: 1px solid rgba(147, 51, 234, 0.2);
            }}
            
            .premium-box p {{
                color: rgba(255, 255, 255, 0.8);
            }}
        }}
        
        @media only screen and (max-width: 600px) {{
            .container {{
                width: 100%;
                margin: 0;
                border-radius: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-container">
                <div class="logo">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 3l1.912 5.813a2 2 0 0 0 1.899 1.337h6.189l-5.011 3.641a2 2 0 0 0-.726 2.236l1.91 5.812-5.011-3.641a2 2 0 0 0-2.236 0L6.926 21.839l1.91-5.812a2 2 0 0 0-.726-2.236L3.1 10.15h6.189a2 2 0 0 0 1.898-1.337L12 3Z"></path>
                    </svg>
                </div>
                <div class="brand-name">TuneLoom</div>
            </div>
            <h2>Email Verification</h2>
        </div>
        <div class="content">
            <p>Hi there,</p>
            <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
            <p style="text-align: center;">
                <a href="{url}" class="button">Verify Email Address</a>
            </p>
            <p>If the button doesn't work, you can also click on the link below or copy it to your browser:</p>
            <div class="url-text">
                <a href="{url}" style="color: #ec4899; text-decoration: none;">{url}</a>
            </div>
            
            <div class="premium-box">
                <div class="pro-badge">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 3l1.912 5.813a2 2 0 0 0 1.899 1.337h6.189l-5.011 3.641a2 2 0 0 0-.726 2.236l1.91 5.812-5.011-3.641a2 2 0 0 0-2.236 0L6.926 21.839l1.91-5.812a2 2 0 0 0-.726-2.236L3.1 10.15h6.189a2 2 0 0 0 1.898-1.337L12 3Z"></path>
                    </svg>
                    <span>Pro</span>
                </div>
                <p style="font-size: 14px; margin: 8px 0;">Upgrade to Premium for exclusive features</p>
                <a href="#" class="premium-button">Unlock All Features</a>
            </div>
            
            <p style="margin-top: 24px;">If you did not create an account, please ignore this email.</p>
            <p>Best regards,<br>{sender_name} Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply directly to this email.</p>
            <p style="margin-top: 12px;">© 2025 MeloMind. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Plain text version as fallback
    text_content = f"""
    Email Verification
    
    Hi there,
    
    Thank you for signing up! Please verify your email address by clicking on the link below:
    
    {url}
    
    If you did not create an account, please ignore this email.
    
    Best regards,
    {sender_name} Team
    """
    
    # Send the email using Mailgun API
    response = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": from_address,
            "to": email,
            "subject": "Email Verification",
            "text": text_content,
            "html": html_content
        }
    )
    
    # Return success status
    return response.status_code == 200

# Example usage in a FastAPI route
"""
@router.post("/send-verification")
async def send_verification(email_data: EmailVerification):
    result = await send_verification_email(email_data.email, email_data.verification_url)
    if result:
        return {"message": "Verification email sent successfully"}
    return {"message": "Failed to send verification email"}, 500
"""