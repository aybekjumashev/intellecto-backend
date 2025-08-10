from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    UserProfileSerializer, UserProgressSerializer, ModuleProgressSerializer, TopicContentSerializer,
    AssessmentSerializer, AssessmentSubmitSerializer, AssessmentResultSerializer,
    TopicExerciseSerializer, ExerciseSubmitSerializer, UnlockModuleSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .models import (
    UserProfile, Module, Topic, TopicContent, UserModuleProgress, Assessment,
    AssessmentSubmission, ExerciseSubmission
)

# Authentication Views
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "success": True,
            "data": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "createdAt": user.createdAt
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.context['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "data": {
                "accessToken": str(refresh.access_token),
                "refreshToken": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }
            }
        }, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# User API Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "data": serializer.data
        })

class UserProgressView(generics.RetrieveAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })


# Learning Path API Views
class ModuleListView(generics.ListAPIView):
    serializer_class = ModuleProgressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        modules = Module.objects.all()
        for module in modules:
            UserModuleProgress.objects.get_or_create(user=user, module=module)
        return UserModuleProgress.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        })

class TopicContentView(generics.RetrieveAPIView):
    serializer_class = TopicContentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = "topicId"

    def get_queryset(self):
        return TopicContent.objects.filter(topic_id=self.kwargs.get('topicId'))

    def get_object(self):
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })


# Assessment API Views
class AssessmentView(generics.RetrieveAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return Assessment.objects.first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

class AssessmentSubmitView(generics.CreateAPIView):
    serializer_class = AssessmentSubmitSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(request=request)
        return Response({
            "success": True,
            "data": {
                "submissionId": submission.id
            }
        }, status=status.HTTP_200_OK)

class AssessmentResultView(generics.RetrieveAPIView):
    serializer_class = AssessmentResultSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = "submissionId"

    def get_queryset(self):
        return AssessmentSubmission.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'processing':
            return Response({
                "success": True,
                "status": "processing",
                "message": "AI is analyzing your results. Please check back in a moment."
            }, status=status.HTTP_202_ACCEPTED)

        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "status": "complete",
            "data": serializer.data
        })


# Exercise API Views
class TopicExerciseView(generics.RetrieveAPIView):
    serializer_class = TopicExerciseSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = "topicId"

    def get_queryset(self):
        return Topic.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })

class ExerciseSubmitView(generics.CreateAPIView):
    serializer_class = ExerciseSubmitSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        topicId = self.kwargs.get('topicId')
        topic = Topic.objects.get(id=topicId)
        serializer = self.get_serializer(data=request.data, context={'request': request, 'topic': topic})
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        dummy_result = {
            "submissionId": submission.id,
            "correctCount": 3,
            "totalQuestions": 4,
            "starsEarned": 2,
            "performanceAnalysis": "You might want to review this topic again to improve your understanding.",
            "results": [
                {"exerciseId": 6, "isCorrect": True, "correctAnswer": "went", "explanation": "\"Went\" is the past form of \"go\"."},
                {"exerciseId": 7, "isCorrect": True, "correctAnswer": 1, "explanation": "\"Ate\" is the irregular past form of \"eat\"."},
                {"exerciseId": 3, "isCorrect": False, "correctAnswer": "He always drinks coffee in the morning.", "explanation": "The correct word order is Subject-Adverb-Verb."},
                {"exerciseId": 4, "isCorrect": True, "correctAnswer": "The weather is beautiful today.", "explanation": "Well done!"}
            ]
        }
        return Response({
            "success": True,
            "data": dummy_result
        })

# Payment API Views
class UnlockModuleView(generics.GenericAPIView):
    serializer_class = UnlockModuleSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        moduleId = self.kwargs.get('moduleId')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        try:
            module = Module.objects.get(id=moduleId)
            progress, created = UserModuleProgress.objects.get_or_create(user=user, module=module)

            if progress.status == 'locked':
                # Here you would validate the paymentToken
                progress.status = 'active'
                progress.save()
                return Response({
                    "success": True,
                    "message": "Module unlocked successfully!",
                    "data": {
                        "moduleId": module.id,
                        "newStatus": "active"
                    }
                })
            else:
                return Response({
                    "success": False,
                    "error": {
                        "code": "MODULE_ALREADY_UNLOCKED",
                        "message": "This module is already unlocked."
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except Module.DoesNotExist:
            return Response({
                    "success": False,
                    "error": {
                        "code": "MODULE_NOT_FOUND",
                        "message": "Module not found."
                    }
                }, status=status.HTTP_404_NOT_FOUND)
