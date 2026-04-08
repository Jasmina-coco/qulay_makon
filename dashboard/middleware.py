from .models import SiteVisit


class VisitorTrackingMiddleware:
    IGNORE_PATHS = ["/admin-panel/", "/super-admin/", "/static/", "/media/", "/api/", "/django-admin/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == "GET" and response.status_code == 200:
            path = request.path
            if not any(path.startswith(ignore_path) for ignore_path in self.IGNORE_PATHS):
                try:
                    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
                    if "," in ip:
                        ip = ip.split(",")[0].strip()
                    SiteVisit.objects.create(
                        ip_address=ip or "127.0.0.1",
                        path=path[:500],
                        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                        referrer=request.META.get("HTTP_REFERER", "")[:500] or None,
                    )
                except Exception:
                    pass

        return response
