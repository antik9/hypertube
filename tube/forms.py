from django import forms


class UploadFileForm(forms.Form):
    video = forms.FileField(label='Select a video')
    title = forms.CharField(label='Title', max_length=255)
