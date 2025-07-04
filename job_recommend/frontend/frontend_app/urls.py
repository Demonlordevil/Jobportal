from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('industries/', views.industries, name='industries'),

    # User authentication
    path('login_user/', views.login_user, name='login_user'),
    path('register_user/', views.register_user, name='register_user'),
    path('jobseeker_about/', views.jobseeker_about, name='jobseeker_about'),
    path('jobseeker_contact/', views.jobseeker_contact, name='jobseeker_contact'),
    path('User_create_profile/', views.create_user_profile, name='create_user_profile'),
    path('User_profile/', views.view_user_profile, name='view_user_profile'),
    path('User_edit_profile/', views.edit_user_profile, name='edit_user_profile'),
    path('User_dashboard/', views.dashboard_user, name='dashboard_user'),
    path('recommendations/', views.recommendations_view, name='recommendations'),

    path('jobseeker_tools/', views.jobseeker_tools, name='jobseeker_tools'),
    path('jobs/', views.job_list, name='job_list'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs_list'),
    path('jobs/<int:job_id>/detail/', views.job_detail, name='job-detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job_with_profile, name='apply-job-form'),
    path('jobs/<int:job_id>/submit-application/', views.submit_application, name='submit-application'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('skill-gap-analyzer/', views.skill_gap_analyzer_view, name='skill-gap-analyzer'),



    # Institution authentication and profile
    path('login_institute/', views.login_institute, name='login_institute'),
    path('register_institute/', views.register_institute, name='register_institute'),
    path('about_institute/', views.Institutionabout, name='about_institute'),
    path('contact_institute/', views.contact_institution, name='contact_institute'),
    path('institution_create_profile/', views.create_institution_profile, name='create_institution_profile'),
    path('institution_profile/', views.view_institution_profile, name='view_institution_profile'),
    path('institution_edit_profile/', views.edit_institution_profile, name='edit_institution_profile'),
    path('institution_dashboard/', views.dashboard_institution, name='dashboard_institution'),

    path('institution_tools/', views.Institution_tools, name='institution_tools'),
    path('job-performance/', views.job_performance, name='job_performance'),
    path('create-job/', views.create_job_post, name='create_job_post'),
    
    path("applications/", views.institution_applications, name="institution-applications"),
    path('applications/save/<int:app_id>/', views.save_application, name='save-application'),
    path('applications/unsave/<int:app_id>/', views.unsave_application, name='unsave-application'),
    path("applications/<int:app_id>/update/", views.update_application_status, name="update-application-status"),
    path("saved-applications/", views.saved_applications, name="saved-applications"),
    path('export-applicants/', views.export_applicants, name='export_applicants'),

    path("performance-dashboard/", views.performance_dashboard, name="performance-dashboard"),

]
