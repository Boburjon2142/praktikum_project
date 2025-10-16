from django.contrib import admin
from .models import Profile
# Register your models here.

# admin.site.register(Profile)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'photo')
    # search_fields = ('user__username', 'user__email')
    
    
admin.site.register(Profile, ProfileAdmin)