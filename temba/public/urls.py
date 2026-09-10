from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from temba.settings import DEBUG

from .sitemaps import PublicViewSitemap, VideoSitemap
from .views import (
    Android,
    Blog,
    GenerateCoupon,
    IndexView,
    LeadCRUDL,
    LeadViewer,
    OrderStatus,
    Style,
    VideoCRUDL,
    Welcome,
    WelcomeRedirect,
)

sitemaps = {"public": PublicViewSitemap, "video": VideoSitemap}

urlpatterns = [
    path("", IndexView.as_view(), {}, "public.public_index"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="public.sitemaps"),
    path("blog/", Blog.as_view(), {}, "public.public_blog"),
    path("welcome/", Welcome.as_view(), {}, "public.public_welcome"),
    path("android/", Android.as_view(), {}, "public.public_android"),
    path("public/welcome/", WelcomeRedirect.as_view(), {}, "public.public_welcome_redirect"),
    path("demo/status/", csrf_exempt(OrderStatus.as_view()), {}, "demo.order_status"),
    path("demo/coupon/", csrf_exempt(GenerateCoupon.as_view()), {}, "demo.generate_coupon"),
]

if DEBUG:  # pragma: needs cover
    (urlpatterns.append(path("style/", Style.as_view(), {}, "public.public_style")),)


urlpatterns += LeadCRUDL().as_urlpatterns()
urlpatterns += LeadViewer().as_urlpatterns()
urlpatterns += VideoCRUDL().as_urlpatterns()
