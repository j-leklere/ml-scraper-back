from django.contrib import admin
from .models import Role, User, Product, Search

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Search)