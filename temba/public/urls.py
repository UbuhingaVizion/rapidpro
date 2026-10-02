from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from temba.settings import DEBUG

from .sitemaps import PublicViewSitemap, VideoSitemap
from .views import (
    Android,
    DemoGenerateCoupon,
    DemoOrderStatus,
    IndexView,
    LeadCRUDL,
    LeadViewer,
    Style,
    VideoCRUDL,
    Welcome,
    WelcomeRedirect,
)

sitemaps = {"public": PublicViewSitemap, "video": VideoSitemap}

urlpatterns = [
    path("", IndexView.as_view(), {}, "public.public_index"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="public.sitemaps"),
    path("welcome/", Welcome.as_view(), {}, "public.public_welcome"),
    path("android/", Android.as_view(), {}, "public.public_android"),
    path("public/welcome/", WelcomeRedirect.as_view(), {}, "public.public_welcome_redirect"),
    path("demo/status/", csrf_exempt(DemoOrderStatus.as_view()), {}, "demo.order_status"),
    path("demo/coupon/", csrf_exempt(DemoGenerateCoupon.as_view()), {}, "demo.generate_coupon"),
]

if DEBUG:  # pragma: needs cover
    (urlpatterns.append(path("style/", Style.as_view(), {}, "public.public_style")),)


urlpatterns += LeadCRUDL().as_urlpatterns()
urlpatterns += LeadViewer().as_urlpatterns()
urlpatterns += VideoCRUDL().as_urlpatterns()
