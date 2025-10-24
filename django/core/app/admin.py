from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.forms import UserCForm, UserMForm
from app.models import User, Appointment


# Register your models here.
@admin.register(User)
class UserAdmin(UserAdmin):
    def user_id(self,obj):
        return obj.username if obj.username else obj.chat_id
    list_display = ['user_id']
    add_form = UserCForm
    form = UserMForm
    model=User
    add_fieldsets = (
        ('Info',{'fields':('chat_id',)}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    fieldsets = (
        ('Info', {'fields': ('username', 'chat_id', 'password')}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id','from_date','is_booking','user__chat_id']
