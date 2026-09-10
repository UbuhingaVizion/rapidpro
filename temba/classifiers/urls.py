from django.urls import include, path
from django.urls import re_path

from .models import Classifier
from .views import ClassifierCRUDL

# build up all the type specific urls
type_urls = []
for cl_type in Classifier.get_types():
    cl_urls = cl_type.get_urls()
    for u in cl_urls:
        u.name = f"classifiers.types.{cl_type.slug}.{u.name}"

    if cl_urls:
        type_urls.append(re_path(f"^{cl_type.slug}/", include(cl_urls)))

urlpatterns = [
    path("", include(ClassifierCRUDL().as_urlpatterns())),
    path("classifiers/types/", include(type_urls)),
]
