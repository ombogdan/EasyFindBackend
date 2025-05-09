from .adminViews import WorkingHoursForm, EmployeeForm
from .models import ClientUser, Organization, WorkingHours, OrganizationOwner, Employee, ServiceType
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

@admin.register(ClientUser)
class ClientUserAdmin(UserAdmin):
    model = ClientUser
    list_display = ('email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(OrganizationOwner)
class OrganizationOwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'owner', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if not request.user.is_authenticated:
            return qs.none()
        return qs.filter(owner__user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.is_authenticated:
            owner = OrganizationOwner.objects.filter(user=request.user).first()
            if owner:
                obj.owner = owner
        obj.save()

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or OrganizationOwner.objects.filter(user=request.user).exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        if obj is None:
            return OrganizationOwner.objects.filter(user=request.user).exists()
        return obj.owner.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.owner.user == request.user

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or (
                    request.user.is_authenticated and OrganizationOwner.objects.filter(user=request.user).exists())


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    form = WorkingHoursForm
    list_display = ('organization', 'day', 'start_time', 'end_time', 'is_closed')

    def save_related(self, request, form, formsets, change):
        pass

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if not request.user.is_authenticated:
            return qs.none()
        return qs.filter(organization__owner__user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.is_authenticated:
            owner = OrganizationOwner.objects.filter(user=request.user).first()
            if owner:
                obj.organization = owner.organizations.first()
        obj.save()

    def has_module_permission(self, request):
        return request.user.is_superuser or (
                    request.user.is_authenticated and OrganizationOwner.objects.filter(user=request.user).exists())

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        if obj is None:
            return OrganizationOwner.objects.filter(user=request.user).exists()
        return obj.organization.owner.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.organization.owner.user == request.user

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or (
                    request.user.is_authenticated and OrganizationOwner.objects.filter(user=request.user).exists())


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'organization')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if not request.user.is_authenticated:
            return qs.none()
        return qs.filter(organization__owner__user=request.user)

    def has_module_permission(self, request):
        return request.user.is_superuser or (
                    request.user.is_authenticated and OrganizationOwner.objects.filter(user=request.user).exists())

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return OrganizationOwner.objects.filter(user=request.user).exists()
        return obj.organization.owner.user == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return obj and obj.organization.owner.user == request.user

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or (
                    request.user.is_authenticated and OrganizationOwner.objects.filter(user=request.user).exists())

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization" and not request.user.is_superuser:
            kwargs["queryset"] = Organization.objects.filter(owner__user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeForm

    def get_organizations(self, obj):
        return ", ".join([org.name for org in obj.organizations.all()])
    get_organizations.short_description = 'Organizations'
    autocomplete_fields = ['organizations', 'service_types']
    list_display = ('first_name', 'last_name', 'get_email', 'get_organizations')
    fields = (
        'first_name', 'last_name', 'middle_name', 'photo',
        'organizations', 'service_types', 'email', 'password', 'change_password'
    )

    def get_email(self, obj):
        return obj.email or '-'
    get_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        change_password = form.cleaned_data.get('change_password')

        if not change:
            pass
        else:
            if change_password and password:
                obj.password = password
            if email and obj.email != email:
                obj.email = email

        super().save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'organizations' and not request.user.is_superuser:
            kwargs["queryset"] = Organization.objects.filter(owner__user=request.user)
        if db_field.name == 'service_types' and not request.user.is_superuser:
            kwargs["queryset"] = ServiceType.objects.filter(organization__owner__user=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organizations__owner__user=request.user).distinct()

    def has_module_permission(self, request):
        return request.user.is_superuser or (
                request.user.is_authenticated and hasattr(request.user, 'organizationowner')
        )
