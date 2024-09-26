# corsmiddleware.py

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class DynamicCORSOriginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_host = request.get_host()
        origin = request.META.get('HTTP_ORIGIN')
        # Define the development and production hosts
        dev_hosts = ['127.0.0.1','127.0.0.1:8000', 'crm-api.cubexizsoft.com','192.168.1.14:8000']
        prod_host = 'crm-api-live.cubexizsoft.com'
        allowed_origin = '*'
        prod_orgin=[
            'https://crm.cubexizsoft.com','https://www.crm.cubexizsoft.com','https://crm.cubexizsoft.com/',
            'https://one.acumen.ae','https://www.one.acumen.ae','https://one.acumen.ae/'
                    ]
        # Allow all origins for development hosts
        if request.method=="GET":
            allowed_origin = '*'
        elif current_host == prod_host:
            # is_cron_job = request.headers.get('X-CRON-JOB') == 'true'
            if origin != None and origin in prod_orgin:
                allowed_origin = origin
            else:
                allowed_origin = None
                
        elif current_host in dev_hosts:
            allowed_origin = '*'
        else:
            allowed_origin = None

        if allowed_origin:
            # Only set CORS headers if an allowed origin is determined
            response = self.get_response(request)
            response["Access-Control-Allow-Origin"] = allowed_origin
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, Authorization"
            response["Access-Control-Allow-Credentials"] = "true"

            # Handle preflight (OPTIONS) requests
            if request.method == "OPTIONS":
                response.status_code = 200
                return response

            return response
        else:
            return JsonResponse({'error': 'Your requests are not allowed here.'}, status=403)
