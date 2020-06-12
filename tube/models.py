from django.db import models


def get_file_path(_, filename):
    return filename


class Tag(models.Model):
    name = models.CharField('Name', max_length=255, unique=True)


class Video(models.Model):
    file = models.FileField(upload_to=get_file_path)
    title = models.CharField('Title', max_length=255)


class VideoTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['tag', 'video']
