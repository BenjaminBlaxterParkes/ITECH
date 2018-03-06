from django.contrib import admin

# Register your models here.
from fan_theory.models import Category, UserProfile, Comment, FanTheory

#admin.site.register(UserProfile)
admin.site.register(Comment)

class FanTheoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug':('title',)}
admin.site.register(FanTheory, FanTheoryAdmin)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
admin.site.register(Category, CategoryAdmin)
