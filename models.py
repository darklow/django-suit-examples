from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Continent(models.Model):
    name = models.CharField(max_length=256)
    order = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None):
        return super(Continent, self).save(force_insert, force_update, using)


class Country(models.Model):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=2,
                            help_text='ISO 3166-1 alpha-2 - two character '
                                      'country code')
    independence_day = models.DateField(blank=True, null=True)
    continent = models.ForeignKey(Continent, null=True)
    area = models.BigIntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True,
                                   help_text='Try and enter few some more '
                                             'lines')
    architecture = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"


TYPE_CHOICES = ((1, 'Awesome'), (2, 'Good'), (3, 'Normal'), (4, 'Bad'))
TYPE_CHOICES2 = ((1, 'Hot'), (2, 'Normal'), (3, 'Cold'))
TYPE_CHOICES3 = ((1, 'Tall'), (2, 'Normal'), (3, 'Short'))


class KitchenSink(models.Model):
    name = models.CharField(max_length=64)
    help_text = models.CharField(max_length=64,
                                 help_text="Enter fully qualified name")
    multiple_in_row = models.CharField(max_length=64,
                                       help_text='Help text for multiple')
    multiple2 = models.CharField(max_length=10, blank=True)
    textfield = models.TextField(blank=True,
                                 verbose_name='Autosized textarea',
                                 help_text='Try and enter few some more lines')

    file = models.FileField(upload_to='.', blank=True)
    readonly_field = models.CharField(max_length=127, default='Some value here')

    date = models.DateField(blank=True, null=True)
    date_and_time = models.DateTimeField(blank=True, null=True)

    date_widget = models.DateField(blank=True, null=True)
    datetime_widget = models.DateTimeField(blank=True, null=True)

    boolean = models.BooleanField(default=True)
    boolean_with_help = models.BooleanField(
        help_text="Boolean field with help text")

    horizontal_choices = models.SmallIntegerField(choices=TYPE_CHOICES,
                                                  default=1,
                                                  help_text='Horizontal '
                                                            'choices look '
                                                            'like this')
    vertical_choices = models.SmallIntegerField(choices=TYPE_CHOICES2,
                                                default=2,
                                                help_text="Some help on "
                                                          "vertical choices")
    choices = models.SmallIntegerField(choices=TYPE_CHOICES3,
                                       default=3,
                                       help_text="Help text")
    hidden_checkbox = models.BooleanField()
    hidden_choice = models.SmallIntegerField(choices=TYPE_CHOICES3,
                                             default=2, blank=True)
    hidden_charfield = models.CharField(max_length=64, blank=True)
    hidden_charfield2 = models.CharField(max_length=64, blank=True)

    country = models.ForeignKey(Country, related_name='foreign_key_country')
    linked_foreign_key = models.ForeignKey(Country, limit_choices_to={
        'continent__name': 'Europe'}, related_name='foreign_key_linked')
    raw_id_field = models.ForeignKey(Country,
                                     help_text='Regular raw ID field',
                                     null=True, blank=True)

    enclosed1 = models.CharField(max_length=64, blank=True)
    enclosed2 = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return self.name

# Inline model for KitchenSink
class Fridge(models.Model):
    kitchensink = models.ForeignKey(KitchenSink)
    name = models.CharField(max_length=64)
    type = models.SmallIntegerField(choices=TYPE_CHOICES3)
    description = models.TextField(blank=True)
    is_quiet = models.BooleanField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return self.name


# Inline model for KitchenSink
class Microwave(models.Model):
    kitchensink = models.ForeignKey(KitchenSink)
    name = models.CharField(max_length=64)
    type = models.SmallIntegerField(choices=TYPE_CHOICES3, default=2,
                                    help_text='Choose wisely')
    is_compact = models.BooleanField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return self.name


##################################
#
# Integrations examples
#
##################################

#
# Django-mptt
# https://github.com/django-mptt/django-mptt/
#
class Category(MPTTModel):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    is_active = models.BooleanField()
    order = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories (django-mptt)"

    class MPTTMeta:
        order_insertion_by = ['order']

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        Category.objects.rebuild()


#
# Django-select2
# https://github.com/applegrew/django-select2
#
class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country)
    capital = models.BooleanField()
    area = models.BigIntegerField(blank=True, null=True)
    population = models.BigIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities (django-select2)"
        unique_together = ('name', 'country')


class WysiwygEditor(models.Model):
    name = models.CharField(max_length=64)
    redactor = models.TextField(verbose_name='Redactor small', blank=True)
    redactor2 = models.TextField(verbose_name='Redactor2', blank=True)
    ckeditor = models.TextField(verbose_name='CKEditor', blank=True)

    def __unicode__(self):
        return self.name


class ReversionedItem(models.Model):
    name = models.CharField(max_length=64)
    quality = models.SmallIntegerField(choices=TYPE_CHOICES, default=1)
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class ImportExportItem(models.Model):
    name = models.CharField(max_length=64)
    quality = models.SmallIntegerField(choices=TYPE_CHOICES, default=1)
    is_active = models.BooleanField(default=False)
