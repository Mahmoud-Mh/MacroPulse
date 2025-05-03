class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        self.allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        self.allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', ['http://localhost:5173'])

    def __call__(self, request):
        response = self.get_response(request)
        
        # Get the origin from the request
        origin = request.META.get('HTTP_ORIGIN')
        
        # When using credentials, we can't use wildcard (*) for Access-Control-Allow-Origin
        # We must specify the exact origin or not send credentials
        if origin:
            # If the origin is in our allowed list or we allow all origins, set it directly
            if self.allow_all or origin in self.allowed_origins:
                response["Access-Control-Allow-Origin"] = origin
            else:
                # Default to localhost:5173 for development if not in allowed list
                response["Access-Control-Allow-Origin"] = "http://localhost:5173"
        else:
            # No origin in request, set to localhost:5173 as default
            response["Access-Control-Allow-Origin"] = "http://localhost:5173"
                
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Allow-Credentials"] = "true"
        
        if request.method == "OPTIONS":
            response.status_code = 200
        
        return response 