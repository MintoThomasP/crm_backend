import codecs
import hashlib
import os
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.conf import settings
import smtplib
from email.message import EmailMessage
# from django.core.mail import EmailMessage
from random import randint

# Create your views here.


@csrf_exempt
def sendTestMail(self):

    msg = EmailMessage()
    # msg['Subject'] = 'Check out Bronx as a puppy!'
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = ['', '']

    # msg.set_content('This is a plain text email')

    # msg.add_alternative("""\
    # <!DOCTYPE html>
    # <html>
    #     <body>
    #         <h1 style="color:SlateGray;">This is an HTML Email!</h1>
    #     </body>
    # </html>
    # """, subtype='html')

    msg = EmailMessage()
    msg['Subject'] = 'Verify your Account'
    msg['In-Reply-To'] = ''
    msg['From'] = settings.EMAIL_HOST_USER_NAME + \
        " <"+settings.EMAIL_HOST_USER+">"
    msg['To'] = ['', '']
    OTPCODE = str(random_with_N_digits(6))
    f = codecs.open(os.path.join(os.path.dirname(os.path.dirname(
        __file__)), "templates/app/customerVerifyAccount.html"), 'r')
    data = f.read()
    data = data.replace("{{code}}", OTPCODE)
    data = data.replace("{{BestRegrads}}", settings.PAINT_MAIL_REGRADS)
    msg.set_content(data, subtype="plain", charset='us-ascii')
    msg.add_alternative(data, subtype='html')

    response = sendPAINTMail(msg)
    return JsonResponse(response, safe=False)


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def sendPAINTMail(msg=""):
    EMAIL_ADDRESS = 'webgroup-master@outlook.com'
    EMAIL_PASSWORD = 'webgroup@123'
    with smtplib.SMTP('smtp.office365.com', 587) as server:
        server.connect('smtp.office365.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    return "Success"

@csrf_exempt
@swagger_auto_schema(method='POST',operation_description="NOTE: API for send Customer sign up success mail",)
@api_view(['POST'])
def mailforwebsite(request):

    try:
        if request.method == 'POST':
            requestData = JSONParser().parse(request)
            
            customerMailId = requestData['ToMail']
            payload=requestData['Content']
            subject=requestData['Subject']
            msg = EmailMessage()
            msg['In-Reply-To'] = ''
            msg['Subject'] = subject
            msg['From'] = "webgroup-master@outlook.com"
            msg['To'] = [" <"+customerMailId+">"]
            f = codecs.open(os.path.join(os.path.dirname(os.path.dirname(
                __file__)), "emailtemplates/app/customerSignUpConfirmation.html"), 'r')
            data = f.read().replace("{{payload}}", payload)
            
            msg.set_content(data, subtype="plain", charset='us-ascii')
            msg.add_alternative(data, subtype='html')

            response = sendPAINTMail(msg)
            # hashlib.sha1(repr(OTPCODE).encode('utf-8')).hexdigest()
            return JsonResponse("Success", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)