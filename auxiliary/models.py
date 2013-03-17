from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as tinymce_models

ICON_CHOICES = (
    ('quote', _('Quote')),
    ('stat', _('Statistic')),
    ('hand', _('Hand')),
)


class TidbitManager(models.Manager):

    def get_query_set(self):
        return super(TidbitManager, self).get_query_set().filter(
            is_active=True).order_by('ordering')


class Tidbit(models.Model):
    """Entries for 'Did you know ?' section in the index page"""

    title = models.CharField(_('title'), max_length=40,
                             default=_('Did you know ?'))
    icon = models.CharField(_('Icon'), max_length=15, choices=ICON_CHOICES)
    content = tinymce_models.HTMLField(_('Content'))
    button_text = models.CharField(_('Button text'), max_length=100)
    button_link = models.CharField(_('Button link'), max_length=255)

    is_active = models.BooleanField(_('Active'), default=True)
    ordering = models.IntegerField(_('Ordering'), default=20, db_index=True)

    objects = models.Manager()
    active = TidbitManager()

    class Meta:
        verbose_name = _('Tidbit')
        verbose_name_plural = _('Tidbits')

    def __unicode__(self):
        return u'{0.title} {0.content}'.format(self)
