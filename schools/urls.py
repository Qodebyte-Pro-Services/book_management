from django.urls import path
from .views import CreateSchoolView, SchoolDetailView

urlpatterns = [
    path('create/', CreateSchoolView.as_view(), name='create-school'),
    path('detail/', SchoolDetailView.as_view(), name='school-detail'),
]
