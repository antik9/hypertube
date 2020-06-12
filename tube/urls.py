from django.urls import path

from tube.views import VideoView, watch, RegisterView, AuthView
from tube.views import uploaded_stream_detail, main_page


urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('register/', RegisterView.as_view(), name='register'),
    path('upload/', VideoView.as_view(), name='upload_video'),
    path('watch/<int:video_id>/', watch, name='video_stream_detail'),
    path('<str:name>/', uploaded_stream_detail, name='video_stream'),
    path('', main_page, name='main_page')
]
