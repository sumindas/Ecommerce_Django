from django import forms
from .models import Offer, Category

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = []  
    offer = forms.ModelChoiceField(queryset=Offer.objects.all(), label='Select an Offer')
    

class ProductReviewForm(forms.Form):
    user_name = forms.CharField(max_length=100)
    user_email = forms.EmailField()
    review_text = forms.CharField(widget=forms.Textarea)
    star_rating = forms.IntegerField(min_value=1, max_value=5)




