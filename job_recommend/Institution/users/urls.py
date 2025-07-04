from django.urls import path,include
from .views import User_Registration_View,UserLoginView,Institution_Profile_View,JobPostCreateView,LogoutView,JobPostCreateView, PublicJobListView, PublicJobDetailView,JobPostUpdateDeleteView,InstitutionJobListView,ApplyToJobView,InstitutionJobApplicationsView,UpdateApplicationStatus,PublicApplicationsView,SaveApplicationView,UnsaveApplicationView,IsApplicationSavedView,SavedApplicationsListView,PerformanceDashboardView,CheckAppliedInstitutionView

urlpatterns = [
    path('Institution_register/', User_Registration_View.as_view(),name='register'),
    path('Institution_login/', UserLoginView.as_view(),name='login'),
    path('Institution_profile/', Institution_Profile_View.as_view(), name='profile'),
    path('Institution_logout/', LogoutView.as_view(), name='logout'),
    
    path('create/', JobPostCreateView.as_view(), name='job-create'),
    path('jobs/', PublicJobListView.as_view(), name='public-job-list'),
    path('jobs/<int:pk>/', PublicJobDetailView.as_view(), name='public-job-detail'),
    path('jobs/<int:pk>/edit/', JobPostUpdateDeleteView.as_view(), name='job-update-delete'),
    path('institution_jobs/', InstitutionJobListView.as_view(), name='institution-job-list'),

    path("jobs/<int:job_id>/apply/", ApplyToJobView.as_view(), name="apply-to-job"),
    path("applications/", InstitutionJobApplicationsView.as_view(), name="view-applications"),
    path("applications/<int:app_id>/update/", UpdateApplicationStatus.as_view(), name="update-application-status"),
    path('public-applications/', PublicApplicationsView.as_view()),

   

    path('save-application/<int:app_id>/', SaveApplicationView.as_view(), name='save-application'),
    path('unsave-application/<int:app_id>/', UnsaveApplicationView.as_view(), name='unsave-application'),
    path('saved-applications/<int:app_id>/', IsApplicationSavedView.as_view(), name='is-application-saved'),
    path('saved-applications/', SavedApplicationsListView.as_view(), name='saved-applications'),


    path("public-applications/check-applied/", CheckAppliedInstitutionView.as_view(), name="check-applied"),
    path('performance-dashboard/', PerformanceDashboardView.as_view(), name='performance-dashboard'),


]
