from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    UserProfileView, UserProgressView,
    ModuleListView, TopicContentView,
    AssessmentView, AssessmentSubmitView, AssessmentResultView,
    TopicExerciseView, ExerciseSubmitView, UnlockModuleView
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Authentication
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout', LogoutView.as_view(), name='logout'),

    # User
    path('user/profile', UserProfileView.as_view(), name='user-profile'),
    path('user/progress', UserProgressView.as_view(), name='user-progress'),

    # Learning Path
    path('modules', ModuleListView.as_view(), name='module-list'),
    path('topics/<int:topicId>/content', TopicContentView.as_view(), name='topic-content'),

    # Assessment
    path('assessment', AssessmentView.as_view(), name='assessment'),
    path('assessment/submit', AssessmentSubmitView.as_view(), name='assessment-submit'),
    path('assessment/result/<uuid:submissionId>', AssessmentResultView.as_view(), name='assessment-result'),

    # Exercise
    path('topics/<int:topicId>/exercises', TopicExerciseView.as_view(), name='topic-exercises'),
    path('topics/<int:topicId>/exercises/submit', ExerciseSubmitView.as_view(), name='exercise-submit'),

    # Payment
    path('modules/<int:moduleId>/unlock', UnlockModuleView.as_view(), name='unlock-module'),
]
