from django.contrib import admin
from users.models import Roles ,User,UserProfile

# Register your models here.
admin.site.register(Roles)
admin.site.register(User)
admin.site.register(UserProfile)
