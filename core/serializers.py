from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'createdAt')
        read_only_fields = ('id', 'createdAt')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                self.context['user'] = user
                return data
        raise serializers.ValidationError(_('Invalid credentials'))

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            raise serializers.ValidationError(e)


from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email', read_only=True)
    memberSince = serializers.DateTimeField(source='user.createdAt', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'username', 'email', 'currentLevel', 'totalStars', 'completedModules', 'memberSince')
        read_only_fields = ('id', 'email', 'memberSince', 'currentLevel', 'totalStars', 'completedModules')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        name = user_data.get('name')
        if name:
            instance.user.name = name
            instance.user.save()

        # Update UserProfile fields
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        return instance

class UserProgressSerializer(serializers.Serializer):
    overview = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    skillProgress = serializers.SerializerMethodField()
    weeklyActivity = serializers.SerializerMethodField()
    areasForImprovement = serializers.SerializerMethodField()

    def get_overview(self, instance):
        # This is dummy data, will be replaced with actual data later
        return {
            "currentLevel": "A2",
            "totalStars": 47,
            "completedModules": 2,
            "completedTopics": 6
        }

    def get_statistics(self, instance):
        # This is dummy data
        return {
            "dayStreak": 7,
            "avgScore": 87,
            "wordsLearned": 156,
            "studyTimeHours": 23
        }

    def get_skillProgress(self, instance):
        # This is dummy data
        return [
            { "skill": "Grammar", "progress": 85 },
            { "skill": "Vocabulary", "progress": 92 },
            { "skill": "Listening", "progress": 78 },
            { "skill": "Reading", "progress": 89 }
        ]

    def get_weeklyActivity(self, instance):
        # This is dummy data
        return [
            { "day": "Mon", "active": True },
            { "day": "Tue", "active": True },
            { "day": "Wed", "active": True },
            { "day": "Thu", "active": True },
            { "day": "Fri", "active": True },
            { "day": "Sat", "active": False },
            { "day": "Sun", "active": False }
        ]

    def get_areasForImprovement(self, instance):
        # This is dummy data
        return [
            {
                "topicId": 2,
                "topicTitle": "Articles (a, an, the)",
                "accuracy": 65,
                "recommendation": "Needs practice"
            },
            {
                "topicId": 5,
                "topicTitle": "Past Simple vs Present Perfect",
                "accuracy": 72,
                "recommendation": "Review recommended"
            }
        ]

from .models import Module, Topic, TopicContent, UserModuleProgress, UserTopicProgress

class TopicProgressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='topic.id')
    title = serializers.CharField(source='topic.title')

    class Meta:
        model = UserTopicProgress
        fields = ('id', 'title', 'stars', 'status')

class ModuleProgressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='module.id')
    title = serializers.CharField(source='module.title')
    topics = serializers.SerializerMethodField()

    class Meta:
        model = UserModuleProgress
        fields = ('id', 'title', 'status', 'finalScore', 'topics')

    def get_topics(self, obj):
        user = self.context['request'].user
        topics = Topic.objects.filter(module=obj.module)
        user_topic_progress = UserTopicProgress.objects.filter(user=user, topic__in=topics)

        progress_map = {utp.topic_id: utp for utp in user_topic_progress}

        serialized_topics = []
        for topic in topics:
            progress = progress_map.get(topic.id)
            if progress:
                serialized_topics.append(TopicProgressSerializer(progress).data)
            else:
                # If no progress entry, it means it's locked
                serialized_topics.append({
                    "id": topic.id,
                    "title": topic.title,
                    "stars": 0,
                    "status": "locked"
                })
        return serialized_topics

class TopicContentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='topic.id')
    title = serializers.CharField(source='topic.title')

    class Meta:
        model = TopicContent
        fields = ('id', 'title', 'content')

from .models import Assessment, Question, AssessmentSubmission

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'type', 'question', 'options', 'category')

class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    assessmentId = serializers.UUIDField(source='id')

    class Meta:
        model = Assessment
        fields = ('assessmentId', 'questions')

class AnswerSerializer(serializers.Serializer):
    questionId = serializers.IntegerField()
    answer = serializers.JSONField()

class AssessmentSubmitSerializer(serializers.Serializer):
    assessmentId = serializers.UUIDField()
    answers = AnswerSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        assessment_id = validated_data['assessmentId']
        answers = validated_data['answers']

        assessment = Assessment.objects.get(id=assessment_id)

        # In a real app, we would have a background task to process the assessment
        # For now, we'll just create the submission record.
        submission = AssessmentSubmission.objects.create(
            user=user,
            assessment=assessment,
            answers=answers,
            totalQuestions=assessment.questions.count()
        )
        return submission

class AssessmentResultSerializer(serializers.ModelSerializer):
    submissionId = serializers.UUIDField(source='id')
    class Meta:
        model = AssessmentSubmission
        fields = ('submissionId', 'status', 'level', 'correctCount', 'totalQuestions', 'aiAnalysis')

from .models import Exercise, ExerciseSubmission

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ('id', 'type', 'question', 'data')

class TopicExerciseSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    topicId = serializers.IntegerField(source='id')
    topicTitle = serializers.CharField(source='title')

    class Meta:
        model = Topic
        fields = ('topicId', 'topicTitle', 'exercises')

class ExerciseAnswerSerializer(serializers.Serializer):
    exerciseId = serializers.IntegerField()
    answer = serializers.JSONField()

class ExerciseSubmitSerializer(serializers.Serializer):
    answers = ExerciseAnswerSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        topic = self.context['topic']
        answers = validated_data['answers']

        # In a real app, we would have a background task to process the submission
        # For now, we'll just create the submission record.
        submission = ExerciseSubmission.objects.create(
            user=user,
            topic=topic,
            answers=answers,
            totalQuestions=len(answers)
        )
        return submission

class ExerciseResultSerializer(serializers.ModelSerializer):
    submissionId = serializers.UUIDField(source='id')
    results = serializers.JSONField()
    class Meta:
        model = ExerciseSubmission
        fields = ('submissionId', 'correctCount', 'totalQuestions', 'starsEarned', 'performanceAnalysis', 'results')

class UnlockModuleSerializer(serializers.Serializer):
    paymentToken = serializers.CharField()
