# corsmiddleware.py

from django.utils.deprecation import MiddlewareMixin

class DynamicCORSOriginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        current_host = request.get_host()
        origin = request.META.get('HTTP_ORIGIN')
        print(current_host)
        # Define the development and production hosts
        dev_hosts = ['127.0.0.1','127.0.0.1:8000', 'crm-api.cubexizsoft.com']
        prod_host = ['crm-api-live.cubexizsoft.com','https://crm-api-live.cubexizsoft.com','https://crm-api-live.cubexizsoft.com/']
        allowed_origin = '*'

        # Allow all origins for development hosts
        
        if current_host in prod_host:
            allowed_origin = "https://crm.cubexizsoft.com"
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

        return self.get_response(request)
