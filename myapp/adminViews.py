from django import forms
from myapp.models import WorkingHours

class WorkingHoursForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=WorkingHours.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Days"
    )

    class Meta:
        model = WorkingHours
        exclude = ('day',)

    def save(self, commit=True):
        org = self.cleaned_data['organization']
        days = self.cleaned_data['days']
        start = self.cleaned_data['start_time']
        end = self.cleaned_data['end_time']
        closed = self.cleaned_data['is_closed']

        instances = []
        for day in days:
            if not WorkingHours.objects.filter(organization=org, day=day).exists():
                instance = WorkingHours(
                    organization=org,
                    day=day,
                    start_time=start,
                    end_time=end,
                    is_closed=closed
                )
                if commit:
                    instance.save()
                instances.append(instance)

        return instances[0] if instances else None