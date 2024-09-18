from django.conf import settings

def reverse_proxy(get_response):
    def process_request(request):
        request.META['REMOTE_ADDR'] = request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0].trim() if not settings.DEBUG else '127.0.0.1'
        return get_response(request)
    return process_request
