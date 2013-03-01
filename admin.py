from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, ModelForm, Textarea, Select
from .models import Country, Continent, KitchenSink, Category, City, \
    Microwave, Fridge
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, NumberInput
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget
from mptt.admin import MPTTModelAdmin


class SortableTabularInline(admin.TabularInline):
    sortable = 'order'

    def __init__(self, *args, **kwargs):
        super(SortableTabularInline, self).__init__(*args, **kwargs)

        self.ordering = (self.sortable,)
        if self.sortable not in self.fields:
            self.fields = list(self.fields) + [self.sortable]

        self.form.Meta.widgets[self.sortable] = NumberInput(
            attrs={'class': 'input-mini suit-sortable inline-sortable'})

    class Media:
        js = ('suit/js/sortables.js',)


# Inlines for KitchenSink
class CountryInlineForm(ModelForm):
    class Meta:
        widgets = {
            'code': TextInput(attrs={'class': 'input-mini'}),
            'population': TextInput(attrs={'class': 'input-medium'}),
            'independence_day': SuitDateWidget,
        }


class CountryInline(SortableTabularInline):
    form = CountryInlineForm
    model = Country
    fields = ('name', 'code', 'population',)
    extra = 1
    verbose_name_plural = 'Cities (Sortable example)'
    sortable = 'order'


class ContinentAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('name_', 'name')
    list_editable = ('name',)
    list_display_links = ('name_',)
    inlines = (CountryInline,)

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
    search_fields = ('name', 'code')
    list_display = ('name', 'code', 'continent', 'independence_day')
    list_filter = ('continent',)
    date_hierarchy = 'independence_day'
    exclude = ('order',)

    fieldsets = [
        (None, {'fields': ['name', 'continent', 'code', 'independence_day']}),
        ('Statistics', {
            'description': 'Country statistics',
            'fields': ['area', 'population']}),
    ]


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
        widgets = {
            'multiple2': TextInput(attrs={'class': 'input-small'}),
            'date': AdminDateWidget(attrs={'class': 'vDateField input-small'}),
            'date_widget': SuitDateWidget,
            'datetime_widget': SuitSplitDateTimeWidget,
            'textfield': Textarea(attrs={'rows': '2'}),
            'linked_foreign_key': Select(attrs={'class': 'linked-select'}),
        }


# Inlines for KitchenSink
class FridgeInlineForm(ModelForm):
    class Meta:
        model = Fridge
        widgets = {
            'description': Textarea(attrs={'class': 'input-large', 'rows': 2,
                                           'style': 'width:95%'}),
            'type': Select(attrs={'class': 'input-medium'}),
        }


class FridgeInline(admin.TabularInline):
    model = Fridge
    form = FridgeInlineForm
    extra = 1
    verbose_name_plural = 'Fridges (Tabular inline)'


class MicrowaveInline(admin.StackedInline):
    model = Microwave
    extra = 1
    verbose_name_plural = 'Microwaves (Stacked inline)'

# Kitchen sink model admin
class KitchenSinkAdmin(admin.ModelAdmin):
    raw_id_fields = ()
    form = KitchenSinkForm
    inlines = (FridgeInline, MicrowaveInline)
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

    def get_formsets(self, request, obj=None):
        """
        Set extra=0 for inlines if object already exists
        """
        for inline in self.get_inline_instances(request):
            formset = inline.get_formset(request, obj)
            if obj:
                formset.extra = 0
            yield formset


admin.site.register(KitchenSink, KitchenSinkAdmin)

#
# Extend original user admin class
# Limit user change list queryset
# Add suit date widgets and special warning for user save
#
class SuitUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        widgets = {
            'last_login': SuitSplitDateTimeWidget,
            'date_joined': SuitSplitDateTimeWidget,
        }


class SuitAdminUser(UserAdmin):
    form = SuitUserChangeForm

    def queryset(self, request):
        qs = super(SuitAdminUser, self).queryset(request)
        return qs.filter(id=6) if request.user.username == 'demo' else qs

    def response_change(self, request, obj):
        messages.warning(request, 'User data change is prevented in demo mode')
        return super(SuitAdminUser, self).response_change(request, obj)


admin.site.unregister(User)
admin.site.register(User, SuitAdminUser)



##################################
#
# Integrations examples
#
##################################

#
# Django-mptt
# https://github.com/django-mptt/django-mptt/
#
class CategoryListForm(ModelForm):
    class Meta:
        widgets = {
            'order': NumberInput(attrs={'class': 'input-mini'})
        }


class CategoryAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order',)

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', CategoryListForm)
        return super(CategoryAdmin, self).get_changelist_form(request,
                                                              **kwargs)


admin.site.register(Category, CategoryAdmin)


#
# Django-select2
# https://github.com/applegrew/django-select2
#
class CountryChoices(AutoModelSelect2Field):
    queryset = Country.objects
    search_fields = ['name__icontains', ]


class CityForm(ModelForm):
    country_verbose_name = Country._meta.verbose_name
    country = CountryChoices(
        label=country_verbose_name.capitalize(),
        widget=AutoHeavySelect2Widget(
            select2_options={
                'width': '220px',
                'placeholder': 'Lookup %s ...' % country_verbose_name
            }
        )
    )


class CityAdmin(ModelAdmin):
    form = CityForm
    search_fields = ('name', 'country__name')
    list_display = ('name', 'country', 'capital', 'continent')
    list_filter = (CountryFilter, 'capital')

    def continent(self, obj):
        return obj.country.continent


admin.site.register(City, CityAdmin)
