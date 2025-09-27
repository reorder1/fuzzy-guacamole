from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = DjangoUserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)
