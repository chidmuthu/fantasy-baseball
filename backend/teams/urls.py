from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, UserRegistrationViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'register', UserRegistrationViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
] 