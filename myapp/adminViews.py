from django import forms
from myapp.models import WorkingHours, Employee


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


class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(
        required=False, widget=forms.PasswordInput, label="Password"
    )
    change_password = forms.BooleanField(
        required=False, label="Change password?"
    )

    class Meta:
        model = Employee
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        change_password = cleaned_data.get("change_password")
        instance = self.instance

        if not instance.pk:
            # новий працівник
            if not email:
                self.add_error("email", "Email обовʼязковий.")
            if not password:
                self.add_error("password", "Password обовʼязковий.")
        else:
            # редагування існуючого
            if change_password and not password:
                self.add_error("password", "Вкажіть новий пароль або зніміть галочку 'Change password'.")

        return cleaned_data