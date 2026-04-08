from django import forms

from frontend.models import Banner, News, Page


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ["title", "subtitle", "image", "link", "is_active", "order"]


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["title", "slug", "content", "meta_description", "is_active"]


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            "title",
            "slug",
            "category",
            "short_description",
            "content",
            "image",
            "is_active",
        ]
