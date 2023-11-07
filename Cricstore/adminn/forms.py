
from django import forms
from .models import *

class SliderForm(forms.ModelForm):
    class Meta:
        model = slider
        fields = '__all__'

class BannerForm(forms.ModelForm):
    class Meta:
        model = banner_area
        fields = '__all__'
        
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'