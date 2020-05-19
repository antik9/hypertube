from django import forms


class UploadFileForm(forms.Form):
    video = forms.FileField(label='Select a video')
