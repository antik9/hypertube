import os
import re
import mimetypes
from wsgiref.util import FileWrapper


from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http.response import StreamingHttpResponse, HttpResponse
from django.template import loader
from django.urls import reverse
from django.views.generic import FormView, View

from .forms import UploadFileForm
from .models import Video, Tag, VideoTag


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class VideoView(FormView):
    template_name = 'tube/upload_file.html'
    form_class = UploadFileForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('auth'))

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            kwargs = self.get_form_kwargs()
            tags_str = kwargs['data'].get('tags')
            tags = [x.strip() for x in tags_str.split('#')][1:]
            existed_tags = {tag.name: tag.id for tag
                            in Tag.objects.filter(name__in=tags)}
            tags_to_create = [tag for tag in tags if tag not in existed_tags]
            tags_ids = list(existed_tags.values())
            for tag in tags_to_create:
                created_tag = Tag.objects.create(name=tag)
                tags_ids.append(created_tag.id)

            video = Video(
                file=kwargs.get('files')['video'],
                title=kwargs['data'].get('title'),
            )
            video.save()
            video_id = video.id

            for tags_id in tags_ids:
                VideoTag.objects.create(tag_id=tags_id, video_id=video_id)

            return HttpResponseRedirect(reverse('main_page'))
        else:
            return HttpResponseRedirect(reverse('auth'))


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
    tags = [tag.name for tag
            in Tag.objects.filter(videotag__video__id=video_id)]

    template = loader.get_template('tube/video_detail.html')

    context = {
        'url': f'/tube/{name}',
        'tags': tags,
        'title': video.title,
    }
    return HttpResponse(template.render(context, request))


def main_page(request):
    tag = request.GET.get('tag', '')
    if tag:
        videos = Video.objects.filter(videotag__tag__name= tag.strip('#'))

    else:
        videos = Video.objects.all()

    template = loader.get_template('tube/main_page.html')

    context = {
        'videos': videos,
        'tag': tag,
        'video_count': videos.count()
    }
    return HttpResponse(template.render(context, request))


class AuthView(View):

    def get(self, request):
        template = loader.get_template('tube/auth.html')
        context = {}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            main_page = reverse('main_page')
            return HttpResponseRedirect(main_page)
        else:
            template = loader.get_template('tube/auth.html')
            context = {}
            return HttpResponse(template.render(context, request))


class RegisterView(View):

    def get(self, request):
        template = loader.get_template('tube/register.html')
        context = {}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        login = request.POST.get('login')
        password = request.POST.get('password')
        email = request.POST.get('email')
        User.objects.create_user(login, email, password)
        main_page = reverse('main_page')
        return HttpResponseRedirect(main_page)
