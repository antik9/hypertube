from django.urls import path

from tube.views import VideoView, VideoDetailView, watch, uploaded_stream_detail


urlpatterns = [
    path('upload/', VideoView.as_view(), name='upload_video'),
    path('uploaded/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    path('watch/<int:video_id>/', watch, name='video_stream_detail'),
    path('<str:name>/', uploaded_stream_detail, name='video_stream'),
]
