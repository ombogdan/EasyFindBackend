from .models import ClientUser, Organization, WorkingHours, OrganizationOwner
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


@admin.register(ClientUser)
class ClientUserAdmin(UserAdmin):
    model = ClientUser
    list_display = ('email', 'is_active')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active',)}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(OrganizationOwner)
class OrganizationOwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email',)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone')
    list_filter = ('owner',)
    search_fields = ('name', 'address')


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ('organization', 'day', 'start_time', 'end_time', 'is_closed')
    list_filter = ('day', 'organization')