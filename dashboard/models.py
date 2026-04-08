from django.db import models


class SiteVisit(models.Model):
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=500)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["path"]),
        ]


class SearchQuery(models.Model):
    query = models.CharField(max_length=300)
    results_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
