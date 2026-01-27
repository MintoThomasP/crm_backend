import base64
import datetime
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# Microsoft Graph Configuration
MS_CONFIG = {
    "tenant_id": "22ed5850-9cb2-404c-b644-a0f2987881fb",
    "client_id": "ab3e8431-9019-4d60-ae79-9511ead4705d",
    "client_secret": "REMOVED_AZURE_SECRET",
    "scope": "https://graph.microsoft.com/.default",
    "sender_email": "connect@mintothomas.com",
    "recipient_email": "mintothomas.p@gmail.com",
    # Update this path to where your logo is stored in your Django static files
    "logo_path": "assets/images/logo.png"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #0a0a0a; padding: 30px; text-align: center; border-bottom: 4px solid #FF4D00; }}
        .logo {{ height: 40px; width: auto; }}
        .content {{ padding: 40px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #0a0a0a; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .field {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #FF4D00; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; display: block; margin-bottom: 5px; }}
        .value {{ font-size: 16px; color: #555; }}
        .message-box {{ background: #f9f9f9; padding: 20px; border-radius: 5px; border-left: 4px solid #FF4D00; margin-top: 20px; font-style: italic; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="cid:logo_cid" alt="Minto Thomas Logo" class="logo">
        </div>
        <div class="content">
            <div class="title">New Inquiry from Portfolio</div>
            <div class="field"><span class="label">From</span><span class="value">{name}</span></div>
            <div class="field"><span class="label">Email Address</span><span class="value">{email}</span></div>
            <div class="field"><span class="label">Message</span><div class="message-box">{message}</div></div>
        </div>
        <div class="footer">&copy; {year} Minto Thomas Portfolio. All rights reserved.</div>
    </div>
</body>
</html>
"""

THANK_YOU_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #0a0a0a; padding: 30px; text-align: center; border-bottom: 4px solid #FF4D00; }}
        .logo {{ height: 40px; width: auto; }}
        .content {{ padding: 40px; text-align: center; }}
        .title {{ font-size: 24px; font-weight: bold; color: #0a0a0a; margin-bottom: 20px; }}
        .message {{ font-size: 16px; color: #555; margin-bottom: 30px; }}
        .btn {{ background-color: #FF4D00; color: #ffffff !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><img src="cid:logo_cid" alt="Minto Thomas Logo" class="logo"></div>
        <div class="content">
            <div class="title">Thank You, {name}!</div>
            <p class="message">I've received your message and will get back to you as soon as possible.</p>
            <div style="margin-bottom: 30px;"><a href="https://mintothomas.com" class="btn">Visit Website</a></div>
            <p class="message" style="font-size: 14px;">Talk soon,<br><strong>Minto Thomas</strong></p>
        </div>
        <div class="footer">&copy; {year} Minto Thomas Portfolio. All rights reserved.</div>
    </div>
</body>
</html>
"""


def get_access_token():
    url = f"https://login.microsoftonline.com/{MS_CONFIG['tenant_id']}/oauth2/v2.0/token"
    data = {
        'client_id': MS_CONFIG['client_id'],
        'scope': MS_CONFIG['scope'],
        'client_secret': MS_CONFIG['client_secret'],
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get('access_token')


def send_ms_graph_email(to_email, subject, body_html, logo_base64=None):
    token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/users/{MS_CONFIG['sender_email']}/sendMail"

    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
            "attachments": [{
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "logo.png",
                "contentType": "image/png",
                "contentBytes": logo_base64,
                "contentId": "logo_cid",
                "isInline": True
            }] if logo_base64 else []
        },
        "saveToSentItems": "false"
    }

    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}
    return requests.post(url, json=email_data, headers=headers)


@csrf_exempt
@require_POST
def send_contact_email(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

        year = datetime.datetime.now().year

        # Prepare Logo
        logo_base64 = ""
        try:
            with open(MS_CONFIG["logo_path"], "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Logo error: {e}")

        # 1. Send Inquiry
        inquiry_html = HTML_TEMPLATE.format(
            name=name, email=email, message=message.replace('\n', '<br>'), year=year)
        inquiry_res = send_ms_graph_email(
            MS_CONFIG['recipient_email'], f"New Inquiry from {name}", inquiry_html, logo_base64)

        # 2. Send Thank You
        thank_you_html = THANK_YOU_TEMPLATE.format(name=name, year=year)
        thank_you_res = send_ms_graph_email(
            email, f"Thank you for contacting me, {name}!", thank_you_html, logo_base64)

        if inquiry_res.status_code == 202:
            return JsonResponse({"status": "success", "message": "Emails sent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Failed to send inquiry email"}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
