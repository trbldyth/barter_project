from django.contrib import admin
from .models import Ad, Category, Condition, ExchangeProposal

admin.site.register(Ad)
admin.site.register(Category)
admin.site.register(Condition)
admin.site.register(ExchangeProposal)
