from django.urls import path

from tube.views import VideoView, VideoDetailView


urlpatterns = [
    path('upload/', VideoView.as_view(), name='upload_video'),
    path('uploaded/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
]
