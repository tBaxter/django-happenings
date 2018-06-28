from django import forms
from django.forms import ModelForm, HiddenInput, TextInput

from .models import Event, Memory


class AdminAddEventForm(ModelForm):
    class Meta:
        model = Event
        fields = [
            'submitted_by', 'subhead', 'name', 'slug', 'info',
            'start_date', 'end_date',
            'region', 'venue',
            'address', 'city', 'state', 'zipcode',
            'phone', 'website',
            'admin_notes', 'featured',
            'offsite_tickets', 'ticket_sales_end', 'related_events',
        ]


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 'info',
            'start_date', 'end_date',
            'region', 'venue',
            'address', 'city', 'state', 'zipcode', 'website'
        ]
        widgets = {
            'start_date': TextInput(attrs={'class': 'datepicker'}),
            'end_date': TextInput(attrs={'class': 'datepicker'}),
        }


class AddEventForm(EventForm):
    def clean(self):
        """
        Validate that an event with this name on this date does not exist.
        """
        cleaned = super(EventForm, self).clean()
        if Event.objects.filter(name=cleaned['name'], start_date=cleaned['start_date']).count():
            raise forms.ValidationError(u'This event appears to be in the database already.')
        return cleaned


class EventUpdateForm(EventForm):
    def clean_name(self):
        return self.cleaned_data['name']


class EventRecapForm(EventUpdateForm):
    class Meta:
        fields = EventUpdateForm.Meta.fields + ['recap']


class MemoryForm(ModelForm):
    photos = forms.FileField(
        required=False,
        label="Or upload your photos(s)",
        help_text="You can upload one or several JPG files. Be kind, this isn't photobucket.",
        widget=forms.FileInput(attrs={'multiple': 'multiple'})
    )
    upload_caption = forms.CharField(
        label="Caption",
        required=False,
        help_text="""
            You can add an optional caption.
            Note: if you are uploading multiple photos, one caption will be used.
        """,
        widget=forms.TextInput()
    )

    def clean_upload(self):
        data = self.cleaned_data['upload']
        if data:
            upload_name = data.name.lower()
            if not any(upload_name.endswith(x) for x in ('.jpg', '.jpeg', '.zip')):
                raise forms.ValidationError("Your upload must be in JPG or ZIP formats.")
            return data

    class Meta:
        model = Memory
        fields = ['offsite_photos', 'photos', 'upload_caption']
        widgets = {
            'photos': HiddenInput()
        }
