from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.forms import TextInput, ModelForm, Textarea, Select
from reversion import VersionAdmin
from import_export.admin import ImportExportModelAdmin
from suit_ckeditor.widgets import CKEditorWidget
from suit_redactor.widgets import RedactorWidget
from .models import Country, Continent, KitchenSink, Category, City, \
    Microwave, Fridge, WysiwygEditor, ReversionedItem, ImportExportItem
from suit.admin import SortableTabularInline, SortableModelAdmin, \
    SortableStackedInline
from suit.widgets import SuitDateWidget, SuitSplitDateTimeWidget, \
    EnclosedInput, LinkedSelect, AutosizedTextarea
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget
from mptt.admin import MPTTModelAdmin


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
    verbose_name_plural = 'Countries (Sortable example)'
    sortable = 'order'


class ContinentAdmin(SortableModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'countries')
    inlines = (CountryInline,)
    sortable = 'order'

    def countries(self, obj):
        return len(obj.country_set.all())

    def suit_row_attributes(self, obj):
        class_map = {
            'Europe': 'success',
            'South America': 'warning',
            'North America': 'success',
            'Africa': 'error',
            'Australia': 'warning',
            'Asia': 'info',
            'Antarctica': 'info',
        }

        css_class = class_map.get(obj.name)
        if css_class:
            return {'class': css_class}

    def suit_cell_attributes(self, obj, column):
        if column == 'countries':
            return {'class': 'text-center'}
        elif column == 'right_aligned':
            return {'class': 'text-right muted'}


admin.site.register(Continent, ContinentAdmin)


class CityInlineForm(ModelForm):
    class Meta:
        widgets = {
            'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                                  attrs={'class': 'input-small'}),
            'population': EnclosedInput(append='icon-user',
                                        attrs={'class': 'input-small'}),
        }


class CityInline(admin.TabularInline):
    form = CityInlineForm
    model = City
    extra = 3
    verbose_name_plural = 'Cities'
    suit_classes = 'suit-tab suit-tab-cities'


class CountryForm(ModelForm):
    class Meta:
        widgets = {
            'code': TextInput(attrs={'class': 'input-mini'}),
            'independence_day': SuitDateWidget,
            'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                                  attrs={'class': 'input-small'}),
            'population': EnclosedInput(prepend='icon-user',
                                        append='<input type="button" '
                                               'class="btn" onclick="window'
                                               '.open(\'https://www.google'
                                               '.com/\')" value="Search">',
                                        attrs={'class': 'input-small'}),
            'description': AutosizedTextarea,
            'architecture': AutosizedTextarea(attrs={'class': 'span5'}),
        }


class CountryAdmin(ModelAdmin):
    form = CountryForm
    search_fields = ('name', 'code')
    list_display = ('name', 'code', 'continent', 'independence_day')
    list_filter = ('continent',)
    date_hierarchy = 'independence_day'
    list_select_related = True

    inlines = (CityInline,)

    fieldsets = [
        (None, {
            'classes': ('suit-tab suit-tab-general',),
            'fields': ['name', 'continent', 'code', 'independence_day']
        }),
        ('Statistics', {
            'classes': ('suit-tab suit-tab-general',),
            'description': 'EnclosedInput widget examples',
            'fields': ['area', 'population']}),
        ('Autosized textarea', {
            'classes': ('suit-tab suit-tab-general',),
            'description': 'AutosizedTextarea widget example - adapts height '
                           'based on user input',
            'fields': ['description']}),
        ('Architecture', {
            'classes': ('suit-tab suit-tab-cities',),
            'description': 'Tabs can contain any fieldsets and inlines',
            'fields': ['architecture']}),
    ]

    suit_form_tabs = (('general', 'General'), ('cities', 'Cities'),
                      ('flag', 'Flag'), ('info', 'Info on tabs'))

    suit_form_includes = (
        ('admin/examples/country/tab_disclaimer.html', 'middle', 'cities'),
        ('admin/examples/country/tab_flag.html', '', 'flag'),
        ('admin/examples/country/tab_info.html', '', 'info'),
    )


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
            'textfield': AutosizedTextarea(attrs={'rows': '2'}),
            'linked_foreign_key': LinkedSelect,

            'enclosed1': EnclosedInput(append='icon-plane',
                                       attrs={'class': 'input-medium'}),
            'enclosed2': EnclosedInput(prepend='icon-envelope',
                                       append='<input type="button" '
                                              'class="btn" value="Send">',
                                       attrs={'class': 'input-medium'}),
        }


# Inlines for KitchenSink
class FridgeInlineForm(ModelForm):
    class Meta:
        model = Fridge
        widgets = {
            'description': AutosizedTextarea(
                attrs={'class': 'input-medium', 'rows': 2,
                       'style': 'width:95%'}),
            'type': Select(attrs={'class': 'input-small'}),
        }


class FridgeInline(SortableTabularInline):
    model = Fridge
    form = FridgeInlineForm
    extra = 1
    verbose_name_plural = 'Fridges (Tabular inline)'


class MicrowaveInline(SortableStackedInline):
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

        ('EnclosedInput widget',
         {
             'description': 'Supports Twitter Bootstrap prepended, '
                            'appended inputs',
             'fields': ['enclosed1', 'enclosed2']}),

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
class CategoryAdmin(MPTTModelAdmin, SortableModelAdmin):
    """
    Example of django-mptt and sortable together. Important note:
    If used together MPTTModelAdmin must be before SortableModelAdmin
    """
    mptt_level_indent = 20
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    list_display_links = ('name',)
    sortable = 'order'


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

    class Meta:
        model = City
        widgets = {
            'area': EnclosedInput(prepend='icon-globe', append='km<sup>2</sup>',
                                  attrs={'class': 'input-small'}),
            'population': EnclosedInput(prepend='icon-user',
                                        append='<input type="button" '
                                               'class="btn" onclick="window'
                                               '.open(\'https://www.google'
                                               '.com/\')" value="Search">',
                                        attrs={'class': 'input-small'}),
        }


class CityAdmin(ModelAdmin):
    form = CityForm
    search_fields = ('name', 'country__name')
    list_display = ('name', 'country', 'capital', 'continent')
    list_filter = (CountryFilter, 'capital')
    fieldsets = [
        (None, {'fields': ['name', 'country', 'capital']}),
        ('Statistics', {
            'description': 'EnclosedInput widget examples',
            'fields': ['area', 'population']}),
    ]

    def continent(self, obj):
        return obj.country.continent


admin.site.register(City, CityAdmin)

#
# Wysiwyg editor integration examples
#
class WysiwygEditorForm(ModelForm):
    class Meta:
        model = WysiwygEditor

        _ck_editor_toolbar = [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph',
             'groups': ['list', 'indent', 'blocks', 'align']},
            {'name': 'document', 'groups': ['mode']}, '/',
            {'name': 'styles'}, {'name': 'colors'},
            {'name': 'insert_custom',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule']},
            {'name': 'about'}]

        _ck_editor_config = {'autoGrow_onStartup': True,
                             'autoGrow_minHeight': 100,
                             'autoGrow_maxHeight': 250,
                             'extraPlugins': 'autogrow',
                             'toolbarGroups': _ck_editor_toolbar}
        widgets = {
            'redactor': RedactorWidget(editor_options={
                'buttons': ['html', '|', 'formatting', '|', 'bold', 'italic']}),
            'redactor2': RedactorWidget,
            'ckeditor': CKEditorWidget(editor_options=_ck_editor_config),
        }


class WysiwygEditorAdmin(ModelAdmin):
    form = WysiwygEditorForm
    search_fields = ('name',)
    list_display = ('name',)
    fieldsets = [
        (None, {'fields': ['name', 'redactor']}),

        ('Redactor', {
            'classes': ('full-width',),
            'description': 'Full width example',
            'fields': ['redactor2']}),

        ('CK Editor', {
            'classes': ('full-width',),
            'description': 'CKEditor 4.x custom toolbar configuration example',
            'fields': ['ckeditor']})
    ]


admin.site.register(WysiwygEditor, WysiwygEditorAdmin)


class ReversionedItemAdmin(VersionAdmin):
    search_fields = ('name',)
    list_display = ('name', 'quality', 'is_active')


admin.site.register(ReversionedItem, ReversionedItemAdmin)


class ImportExportDemoAdmin(ImportExportModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'quality', 'is_active')


admin.site.register(ImportExportItem, ImportExportDemoAdmin)
