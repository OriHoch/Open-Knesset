# encoding: utf-8
import re

from django.db import models
import logging

logger = logging.getLogger("open-knesset.laws.models")


class BillProposal(models.Model):
    class Meta:
        app_label = 'laws'
        abstract = True

    knesset_id = models.IntegerField(blank=True, null=True)
    law = models.ForeignKey('Law', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    title = models.CharField(max_length=1000)
    date = models.DateField(blank=True, null=True)
    source_url = models.URLField(max_length=1024, null=True, blank=True)
    content_html = models.TextField(blank=True, default="")
    committee_meetings = models.ManyToManyField('committees.CommitteeMeeting',
                                                related_name="%(app_label)s_%(class)s_related", blank=True, null=True)
    votes = models.ManyToManyField('Vote', related_name="%(app_label)s_%(class)s_related", blank=True, null=True)

    def __unicode__(self):
        return u"%s %s" % (self.law, self.title)

    def get_absolute_url(self):
        if self.bill:
            return self.bill.get_absolute_url()
        return ""

    def get_explanation(self):
        r = re.search(r"דברי הסבר.*?(<p>.*?)<p>-+".decode('utf8'), self.content_html, re.M | re.DOTALL)
        return r.group(1) if r else self.content_html


class PrivateProposal(BillProposal):
    class Meta:
        app_label = 'laws'
        ordering = ['date']

    proposal_id = models.IntegerField(blank=True, null=True)
    proposers = models.ManyToManyField('mks.Member', related_name='proposals_proposed', blank=True, null=True)
    joiners = models.ManyToManyField('mks.Member', related_name='proposals_joined', blank=True, null=True)
    bill = models.ForeignKey('Bill', related_name='proposals', blank=True, null=True)


class KnessetProposal(BillProposal):
    class Meta:
        app_label = 'laws'
        ordering = ['date']

    committee = models.ForeignKey('committees.Committee', related_name='bills', blank=True, null=True)
    booklet_number = models.IntegerField(blank=True, null=True)
    originals = models.ManyToManyField('PrivateProposal', related_name='knesset_proposals', blank=True, null=True)
    bill = models.OneToOneField('Bill', related_name='knesset_proposal', blank=True, null=True)


class GovProposal(BillProposal):
    class Meta:
        app_label = 'laws'
        ordering = ['date']

    booklet_number = models.IntegerField(blank=True, null=True)
    bill = models.OneToOneField('Bill', related_name='gov_proposal', blank=True, null=True)
