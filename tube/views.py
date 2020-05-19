from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, DetailView

from .forms import UploadFileForm
from .models import Video


class VideoView(FormView):
    template_name = 'tube/upload_file.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        video = Video(
            file=self.get_form_kwargs().get('files')['video']
        )
        video.save()
        video_id = video.id

        return HttpResponseRedirect(self.__get_success_url(video_id))

    @staticmethod
    def __get_success_url(video_id):
        return reverse('video_detail', kwargs={'pk': video_id})


class VideoDetailView(DetailView):
    model = Video
    template_name = 'tube/video_detail.html'
    context_object_name = 'video_data'
