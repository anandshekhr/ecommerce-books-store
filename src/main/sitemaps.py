from django.contrib.sitemaps import Sitemap
from .models import Book

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Book.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()
