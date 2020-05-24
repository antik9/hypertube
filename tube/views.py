import os
import re
import mimetypes
from wsgiref.util import FileWrapper

from django.http import HttpResponseRedirect
from django.http.response import StreamingHttpResponse, HttpResponse
from django.template import loader
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
        return reverse('video_stream_detail', kwargs={'video_id': video_id})


class VideoDetailView(DetailView):
    model = Video
    template_name = 'tube/video_detail.html'
    context_object_name = 'video_data'


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, path):
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(
            RangeFileWrapper(open(path, 'rb'), offset=first_byte,length=length),
            status=206, content_type=content_type
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')),
                                     content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


def uploaded_stream_detail(request, name):
    path = f'media/{name}'
    return stream_video(request, path)


def watch(request, video_id):
    video = Video.objects.filter(id=video_id).first()
    name = video.file.name if video else None
    template = loader.get_template('tube/video_detail.html')

    context = {
        'url': f'/tube/{name}',
    }
    return HttpResponse(template.render(context, request))
