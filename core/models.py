from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    currentLevel = models.CharField(max_length=10, default='A1')
    totalStars = models.IntegerField(default=0)
    completedModules = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # This is called to save the profile instance whenever the user instance is saved.
    # It's needed for the create_user_profile signal to work correctly.
    # We can just check if the profile exists, if not, create it.
    # This is a bit redundant with create_user_profile, but it's a safeguard.
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class Module(models.Model):
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Topic(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class TopicContent(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='content')
    content = models.JSONField()

    def __str__(self):
        return f"Content for {self.topic.title}"

class UserModuleProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='locked') # completed, active, locked
    finalScore = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'module')

class UserTopicProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='locked') # completed, active, locked

    class Meta:
        unique_together = ('user', 'topic')


class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=50)
    question = models.TextField()
    options = models.JSONField()
    category = models.CharField(max_length=100)
    correct_answer = models.JSONField()

    def __str__(self):
        return self.question

class AssessmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    answers = models.JSONField()
    status = models.CharField(max_length=20, default='processing')
    level = models.CharField(max_length=10, blank=True, null=True)
    correctCount = models.IntegerField(default=0)
    totalQuestions = models.IntegerField(default=0)
    aiAnalysis = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.email} for {self.assessment.title}"


class Exercise(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='exercises')
    type = models.CharField(max_length=50)
    question = models.TextField()
    data = models.JSONField()
    correct_answer = models.JSONField()

    def __str__(self):
        return self.question

class ExerciseSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    answers = models.JSONField()
    correctCount = models.IntegerField(default=0)
    totalQuestions = models.IntegerField(default=0)
    starsEarned = models.IntegerField(default=0)
    performanceAnalysis = models.TextField(blank=True, null=True)
    results = models.JSONField(blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.email} for topic {self.topic.title}"
