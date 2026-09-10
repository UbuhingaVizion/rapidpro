from django.urls import path

from .views import Home, MessageHistory, RangeDetails

urlpatterns = [
    path("dashboard/home/", Home.as_view(), {}, "dashboard.dashboard_home"),
    path("dashboard/message_history/", MessageHistory.as_view(), {}, "dashboard.dashboard_message_history"),
    path("dashboard/range_details/", RangeDetails.as_view(), {}, "dashboard.dashboard_range_details"),
]
