from django.urls import path
from .views import (
    TeacherListCreateView,
    TeacherDetailView,
    TeacherProfileView,
    TeacherClassListView,
    TeacherAttendanceListCreateView,
    TeacherAttendanceDetailView,
    resend_teacher_credentials,
    teacher_dashboard
)

urlpatterns = [
    # Teacher endpoints
    path('profile/', TeacherProfileView.as_view(), name='teacher-profile'),
    path('', TeacherListCreateView.as_view(), name='teacher-list'),
    path('<str:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('<str:teacher_id>/classes/', TeacherClassListView.as_view(), name='teacher-classes'),
    path('<str:pk>/resend-credentials/', resend_teacher_credentials, name='teacher-resend-credentials'),
    
    # Teacher attendance endpoints
    path('attendance/', TeacherAttendanceListCreateView.as_view(), name='teacher-attendance-list'),
    path('attendance/<int:pk>/', TeacherAttendanceDetailView.as_view(), name='teacher-attendance-detail'),
    
    # Dashboard
    path('dashboard/', teacher_dashboard, name='teacher-dashboard'),
]
