from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Achievements


class AchievementForm(ModelForm):
    class Meta:
        model = Achievements
        fields = [
            "title",
            "description",
            "field",
            "image_url",
        ]
        labels = {
            "title": "Nama Prestasi",
            "description": "Deskripsi Prestasi",
            "field": "Bidang",
            "image_url": "URL Gambar Prestasi",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Nama prestasimu",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan prestasimu",
                    "rows": 3,
                }
            ),
            "field": TextInput(
                attrs={
                    "placeholder": "Robotika, Akademik, atau bidang lainnya",
                }
            ),
            "image_url": URLInput(
                attrs={
                    "placeholder": "https://example.com/gambar.jpg",
                }
            ),
        }