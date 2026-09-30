from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, URLInput
from django.utils.html import strip_tags

from main.models import Achievements, Experience


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

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError(
                "Nama prestasi tidak boleh hanya berisi tag HTML."
            )
        return title

    def clean_field(self):
        return strip_tags(self.cleaned_data["field"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
        ]
