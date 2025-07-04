from django.urls import path
from django.http import HttpResponse
from .views import User_Registration_View,User_Login_View,ResumeSummaryView,WorkExperienceListCreateView,WorkExperienceDetailView,EducationEntryDetailView,EducationEntryListCreateView,User_Profile_View,LogoutView,InstitutionJobListView,InstitutionJobDetailView,ApplyToJobView,MyApplicationsView,SaveJobView,UnsaveJobView,SavedJobsListView,IsJobSavedView,ScrapeJobsView,JobRecommendationView,HasAppliedProxyView,SkillGapAnalyzerView
urlpatterns = [
    path('register/', User_Registration_View.as_view(),name='register'),
    path('login/', User_Login_View.as_view(), name='login'),
    path('profile/',User_Profile_View.as_view(),name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('jobs/', InstitutionJobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', InstitutionJobDetailView.as_view(), name='public-job-detail'),
    path('save-job/<int:job_id>/', SaveJobView.as_view(), name='save-job'),
    path('unsave-job/<int:job_id>/', UnsaveJobView.as_view(), name='unsave-job'),
    path('saved-jobs/<int:job_id>/', IsJobSavedView.as_view(), name='is-job-saved'),
    path('saved-jobs/', SavedJobsListView.as_view(), name='saved-jobs'),

    path("jobs/<int:job_id>/apply/", ApplyToJobView.as_view(), name="apply-job"),
    path("my-applications/", MyApplicationsView.as_view(), name="my-applications"),
    path("check-applied/<int:job_id>/", HasAppliedProxyView.as_view(), name="check-applied"),



    path('resume/summary/', ResumeSummaryView.as_view(), name='resume-summary'),
    path('resume/experience/', WorkExperienceListCreateView.as_view(), name='work-experience-list-create'),
    path('resume/experience/<int:pk>/', WorkExperienceDetailView.as_view(), name='work-experience-detail'),
    path('resume/education/', EducationEntryListCreateView.as_view(), name='education-entry-list-create'),
    path('resume/education/<int:pk>/', EducationEntryDetailView.as_view(), name='education-entry-detail'),


    path('scrape-jobs/', ScrapeJobsView.as_view(), name='scrape-jobs'),
    path('recommendations/', JobRecommendationView.as_view(), name='job-recommendations'),
    path('analyze-skill-gap/', SkillGapAnalyzerView.as_view(), name='analyze-skill-gap'),

]
