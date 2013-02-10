from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.forms import TextInput, ModelForm, Textarea
from .models import *
from suit.widgets import SuitDateWidget
from django.utils.translation import ugettext_lazy as _

class CountryForm(ModelForm):
    class Meta:
        SmallInput = TextInput(attrs={'class': 'input-mini'})
        CompactTextarea = Textarea(attrs={'rows': '2'})
        widgets = {
            'code': SmallInput,
            'independence_day': SuitDateWidget,
        }


class CountryAdmin(ModelAdmin):
    form = CountryForm
    list_per_page = 15
    search_fields = ('name', 'code')
    list_display = ('name', 'code', 'continent', 'independence_day')
    list_filter = ('continent',)
    date_hierarchy = 'independence_day'


admin.site.register(Country, CountryAdmin)
