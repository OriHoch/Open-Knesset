from committees.views import *
from committees.models import *
from django.db.models import Max, Min

class PlenumView(CommitteeDetailView):    
    
    def get_object(self, *args, **kwargs):
        return Committee.objects.get(type='plenum')
    
class PlenumMeetingsListView(MeetingsListView):
    
    def get_queryset (self):
        c_id = Committee.objects.get(type='plenum').id
        if c_id:
            return CommitteeMeeting.objects.filter(committee__id=c_id)
        else:
            return CommitteeMeeting.objects.all()
        
    def get_context(self):
        context = super(PlenumMeetingsListView, self).get_context()
        context['committee_type'] = 'plenum'
        return context
    
class PlenumMeetingDetailView(MeetingDetailView):

    def get_context_protocol_parts(self, context, *args, **kwargs):
        if kwargs.has_key('sectionid'):
            sectionid=int(kwargs['sectionid'])
            cm = context['object']
            next_sectionid=cm.parts.filter(type='title',order__gt=sectionid).aggregate(Min('order'))['order__min']
            context['next_title_sectionid']=next_sectionid
            context['has_next_title_sectionid']=True
            if next_sectionid is None:
                next_sectionid=cm.parts.aggregate(Max('order'))['order__max']+1
                context['has_next_title_sectionid']=False
            context['prev_title_sectionid']=cm.parts.filter(type='title',order__lt=sectionid).aggregate(Max('order'))['order__max']
            context['has_prev_title_sectionid']=True
            if context['prev_title_sectionid'] is None:
                context['has_prev_title_sectionid']=False
            #parts=cm.parts.all().filter(order__gt=sectionid-1,order__lt=next_sectionid)
            parts_lengths = {}
            for part in cm.parts.all().filter(order__gt=sectionid-1,order__lt=next_sectionid).order_by('order'):
                parts_lengths[part.id] = len(part.body)
            context['parts_lengths'] = json.dumps(parts_lengths)
            context['parts']=cm.parts.all().filter(order__gt=sectionid-1,order__lt=next_sectionid).order_by('order')
            context['title_sectionid']=sectionid
        else:
            context=super(PlenumMeetingDetailView, self).get_context_protocol_parts(context, *args, **kwargs)
        return context

    def get_context_data(self, *args, **kwargs):
        context=super(PlenumMeetingDetailView, self).get_context_data(*args, **kwargs)
        cm=context['object']
        tparts=[]
        for tpart in cm.parts.filter(type='title'):
            header=tpart.header
            if len(header.strip())==0:
                header=tpart.body.split('\n')[0]
            tparts.append({'id':tpart.id,'header':header,'order':tpart.order})
        context['titleparts']=tparts
        return context