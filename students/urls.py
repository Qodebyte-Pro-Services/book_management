from django.urls import path
from .views import (
    ClassListCreateView,
    ClassDetailView,
    StudentListCreateView,
    StudentDetailView,
    StudentAttendanceListCreateView,
    StudentAttendanceDetailView
)

urlpatterns = [
    path('classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<str:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('', StudentListCreateView.as_view(), name='student-list-create'),
    path('<str:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('attendance/', StudentAttendanceListCreateView.as_view(), name='student-attendance-list-create'),
    path('attendance/<str:pk>/', StudentAttendanceDetailView.as_view(), name='student-attendance-detail'),
]

