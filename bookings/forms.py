from django import forms
from .models import Booking, Rating
from accounts.models import User

class BookingCreateForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'address', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Service Location Address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any specific instructions or requirements...'}),
        }


class AssignProviderForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.PROVIDER),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Booking
        fields = ['provider']


class RatingForm(forms.ModelForm):
    stars = forms.ChoiceField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Rating
        fields = ['stars', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review about the service provided...'}),
        }
