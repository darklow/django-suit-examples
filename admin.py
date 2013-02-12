from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import TextInput, ModelForm, Textarea, Select
from .models import Country, Continent, KitchenSink, Category
from mptt.admin import MPTTModelAdmin
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget


class ContinentAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('name_', 'name',)
    list_editable = ('name',)
    list_display_links = ('name_',)

    def name_(self, obj):
        return unicode(obj)


admin.site.register(Continent, ContinentAdmin)


class CountryForm(ModelForm):
    class Meta:
        widgets = {
            'code': TextInput(attrs={'class': 'input-mini'}),
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


class CountryFilter(SimpleListFilter):
    """
    List filter example that shows only referenced(used) values
    """
    title = 'country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        # You can use also "Country" instead of "model_admin.model"
        # if this is not direct relation
        countries = set([c.country for c in model_admin.model.objects.all()])
        return [(c.id, c.name) for c in countries]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country__id__exact=self.value())
        else:
            return queryset


class KitchenSinkForm(ModelForm):
    class Meta:
        SmallInput = TextInput(attrs={'class': 'input-small'})
        CompactTextarea = Textarea(attrs={'rows': '2'})
        widgets = {
            'multiple2': SmallInput,
            'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
            'date_widget': SuitDateWidget,
            'datetime_widget': SuitSplitDateTimeWidget,
            'textfield': CompactTextarea,
            'linked_foreign_key': Select(attrs={'class': 'linked-select'}),
        }

#
# class FridgeInlineForm(ModelForm):
#     class Meta:
#         model = Fridge
#         CompactTextArea = Textarea(
#             attrs={'class': 'input-large', 'rows': 2, 'style': 'width:95%'})
#         widgets = {
#             'description': CompactTextArea,
#             'type': Select(attrs={'class': 'input-medium'}),
#             }
#
#
# class FridgeInline(admin.TabularInline):
#     model = Fridge
#     form = FridgeInlineForm
#     extra = 1
#     verbose_name_plural = 'Fridges (Tabular inline)'
#
# class CountryInline(admin.StackedInline):
#     model = Microwave
#     extra = 1
#     verbose_name_plural = 'Microwaves (Stacked inline)'


class KitchenSinkAdmin(admin.ModelAdmin):
    raw_id_fields = ()
    form = KitchenSinkForm
    # inlines = (FridgeInline, MicrowaveInline)
    search_fields = ['name']
    radio_fields = {"horizontal_choices": admin.HORIZONTAL,
                    'vertical_choices': admin.VERTICAL}
    list_editable = ('boolean', )
    list_filter = ('choices', 'date', CountryFilter)
    readonly_fields = ('readonly_field',)
    raw_id_fields = ('raw_id_field',)
    fieldsets = [
        (None, {'fields': ['name', 'help_text', 'textfield',
                           ('multiple_in_row', 'multiple2'),
                           'file', 'readonly_field']}),
        ('Date and time', {
            'description': 'Improved date/time widgets (SuitDateWidget, '
                           'SuitSplitDateTimeWidget) . Uses original JS.',
            'fields': ['date_widget', 'datetime_widget']}),

        ('Foreign key relations',
         {'description': 'Original select and linked select feature',
          'fields': ['country', 'linked_foreign_key', 'raw_id_field']}),

        ('Boolean and choices',
         {'fields': ['boolean', 'boolean_with_help', 'choices',
                     'horizontal_choices', 'vertical_choices']}),

        ('Collapsed settings', {
            'classes': ('collapse',),
            'fields': ['hidden_checkbox', 'hidden_choice']}),
        ('And one more collapsable', {
            'classes': ('collapse',),
            'fields': ['hidden_charfield', 'hidden_charfield2']}),

    ]
    list_display = (
        'name', 'help_text', 'choices', 'horizontal_choices', 'boolean')


admin.site.register(KitchenSink, KitchenSinkAdmin)

##################################
#
# Integrations examples
#
##################################

#
# Django-mptt
# https://github.com/django-mptt/django-mptt/
#
class CategoryAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'is_active')


admin.site.register(Category, CategoryAdmin)
