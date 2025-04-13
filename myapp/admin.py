from .models import ClientUser, Organization, WorkingHours, OrganizationOwner
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
                'groups',            # 🔥 додай це
                'user_permissions',  # 🔥 і це
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
                'is_superuser',       # 🔥 додай це
                'groups',             # 🔥 і це
                'user_permissions',   # 🔥 і це
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
    list_display = ('name', 'owner', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner__user=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            owner = OrganizationOwner.objects.get(user=request.user)
            obj.owner = owner
        obj.save()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or (obj and obj.owner.user == request.user):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('organization', 'day', 'start_time', 'end_time', 'is_closed')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization__owner__user=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or (obj and obj.organization.owner.user == request.user):
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)