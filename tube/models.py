from django.db import models


def get_file_path(_, filename):
    return filename


class Video(models.Model):
    file = models.FileField(upload_to=get_file_path)
