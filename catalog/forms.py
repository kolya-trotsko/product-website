import re
from django import forms
from django.core.validators import EmailValidator
from .models import Review, ConditionerOrder


PHONE_RE = re.compile(r"^[0-9+()\\-\\s]{7,20}$")


class ReviewForm(forms.ModelForm):
    user = forms.EmailField(validators=[EmailValidator()])

    class Meta:
        model = Review
        fields = ['text', 'rating', 'user']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            return rating
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Invalid rating.")
        return rating

    def clean_text(self):
        text = (self.cleaned_data.get('text') or "").strip()
        if len(text) < 10:
            raise forms.ValidationError("Review is too short.")
        return text


class ConditionerOrderForm(forms.ModelForm):
    class Meta:
        model = ConditionerOrder
        fields = ['name', 'phone', 'address', 'color']

    def __init__(self, *args, conditioner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditioner = conditioner

    def clean_name(self):
        name = (self.cleaned_data.get('name') or "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Invalid name.")
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or "").strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Invalid phone.")
        return phone

    def clean_address(self):
        address = (self.cleaned_data.get('address') or "").strip()
        if len(address) < 5:
            raise forms.ValidationError("Invalid address.")
        return address

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if self.conditioner and not self.conditioner.colors.filter(id=color.id).exists():
            raise forms.ValidationError("Invalid color.")
        return color
