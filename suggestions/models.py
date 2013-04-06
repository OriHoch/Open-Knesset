from datetime import datetime
import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .consts import (CREATE, ADD, REMOVE, SET, NEW, FIXED, WONTFIX)
from .managers import SuggestionsManager


class Suggestion(models.Model):
    """Data improvement suggestions.  Designed to implement suggestions queue
    for content editors.

    .. warning::
        Don't use ``Suggestion.objects.create()`` ! Instead use
        ``Suggestion.objects.create_suggestion()``. It also validates contents
        and handles actions/fields relations as it should !

    A suggestion can be either:
    * Automatically applied once approved (for that data needs to to supplied
      and action be one of: ADD, REMOVE, SET, CREATE. If the the field to be
      modified is a relation manger, action's `subject` should be provided as
      well.
    * Manually applied, in that case a content should be provided for
      `content`.

    The model is generic when possible, and designed for building custom
    suggestion forms for each content type.

    For now see ``suggestions/tests.py`` for usage examples
    """

    RESOLVE_CHOICES = (
        (NEW, _('New')),
        (FIXED, _('Fixed')),
        (WONTFIX, _("Won't Fix")),
    )

    suggested_at = models.DateTimeField(
        _('Suggested at'), blank=True, default=datetime.now, db_index=True)
    suggested_by = models.ForeignKey(User, related_name='suggestions')

    comment = models.TextField(blank=True, null=True)

    resolved_at = models.DateTimeField(_('Resolved at'), blank=True, null=True)
    resolved_by = models.ForeignKey(
        User, related_name='resolved_suggestions', blank=True, null=True)
    resolved_status = models.IntegerField(
        _('Resolved status'), db_index=True, default=NEW,
        choices=RESOLVE_CHOICES)

    objects = SuggestionsManager()

    class Meta:
        verbose_name = _('Suggestion')
        verbose_name_plural = _('Suggestions')

    def auto_apply(self, resolved_by):

        if not self.actions.count():
            raise ValueError("Can't be auto applied, no actions")

        # subject's are carried from action to action, to make sure CREATE
        # follwed by ADD for m2m will work
        subject = None
        for action in self.actions.all():
            subject = action.auto_apply(subject)

        self.resolved_by = resolved_by
        self.resolved_status = FIXED
        self.resolved_at = datetime.now()

        self.save()
        return subject


class SuggestedAction(models.Model):
    """Suggestion can be of multiple action"""

    SUGGEST_CHOICES = (
        (CREATE, _('Create new model instance')),
        (ADD, _('Add related object to m2m relation or new model instance')),
        (REMOVE, _('Remove related object from m2m relation')),
        (SET, _('Set field value. For m2m _replaces_ (use ADD if needed)')),
    )

    suggestion = models.ForeignKey(Suggestion, related_name='actions')
    action = models.PositiveIntegerField(
        _('Suggestion type'), choices=SUGGEST_CHOICES)

    # The Model instance (or model itself in case of create) to work on
    subject_type = models.ForeignKey(ContentType, related_name='action_subjects',
                                     blank=True, null=True)
    subject_id = models.PositiveIntegerField(
        blank=True, null=True, help_text=_('Can be blank, for create operations'))
    subject = generic.GenericForeignKey(
        'subject_type', 'subject_id')

    def auto_apply(self, subject=None):
        """Auto apply the action. subject is optional, and needs to be passed in
        case of adding to m2m after create.

        """
        work_on = subject or self.subject

        actions = {
            SET: self.do_set,
            ADD: self.do_add,
            REMOVE: self.do_remove,
            CREATE: self.do_create,
        }

        doer = actions.get(self.action)
        return doer(work_on)

    @property
    def action_params(self):
        return (x.field_and_value for x in self.action_fields.all())

    def do_set(self, subject):
        "Set subject fields"
        for field, value in self.action_params:
            setattr(subject, field, value)
        subject.save()
        return subject

    def do_add(self, subject):
        "Add an instance to subject's m2m attribute"

        for fname, value in self.action_params:
            field, model, direct, m2m = subject._meta.get_field_by_name(fname)

            if not m2m:
                raise ValueError("{0} can be auto applied only on m2m".format(
                    self.get_action_display()
                ))
            getattr(subject, fname).add(value)

        return subject

    def do_remove(self, subject):
        "Remove an instance to subject's m2m attribute"

        for fname, value in self.action_params:
            field, model, direct, m2m = subject._meta.get_field_by_name(fname)

            if not m2m:
                raise ValueError("{0} can be auto applied only on m2m".format(
                    self.get_action_display()
                ))
            getattr(subject, fname).remove(value)

        return subject

    def do_create(self, subject):
        """Create a new instance.

        we don't care about prev subjects, as we're creating a new one
        """
        model = self.subject_type.model_class()
        subject = model.objects.create(**dict(self.action_params))

        return subject


class ActionFields(models.Model):
    """Fields for each suggestion"""

    action = models.ForeignKey(SuggestedAction, related_name='action_fields')
    name = models.CharField(
        _('Field or relation set name'), null=False, blank=False, max_length=50)

    # general value
    value = models.TextField(blank=True, null=True)

    # In case value is a related object
    value_type = models.ForeignKey(
        ContentType, related_name='action_values', blank=True, null=True)
    value_id = models.PositiveIntegerField(blank=True, null=True)
    value_object = generic.GenericForeignKey('value_type', 'value_id')

    @property
    def field_and_value(self):
        "Return a tuple of field name and actual value"

        if self.value_id is not None:
            return self.name, self.value_object

        return self.name, json.loads(self.value)
