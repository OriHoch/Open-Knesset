from django.conf import settings
from django.http import HttpResponse
import json
from knesset.video.utils.lock import Lock
from django.contrib.contenttypes.models import ContentType
from knesset.committees.models import Committee
from knesset.video.utils import get_videos_queryset
from knesset.video.models import Video

def _validateReqeustGetProcessIdentifier(request):
    secrets=getattr(settings, 'VIDEO_COMMITTEE_UPDATE_AJAX_SECRETS',{})
    if request.method=='GET':
        return getattr(secrets,request.GET['secret'],False)
    else:
        return False

def _get_video(processId):
    lock=Lock('CommitteeUpdateAjaxView_QueueLock', 10)
    uuid=lock.lock()
    if uuid: 
        object_type=ContentType.objects.get_for_model(Committee)
        videos=Video.objects.filter(content_type__pk=object_type.id,group='mms',is_processing_remotely=False,is_done_processing=False).order_by('id')
        if len(videos)>0:
            video=videos[0]
            video.is_processing_remotely=True
            video.processing_remotely_by=processId
            video.save()
            lock.releaseLock(uuid)
            return {'status':True,'msg':'ok','video':{
                'id': video.id,
                'title': video.title,
                'published': video.published.strftime('%d/%m/%Y'),
                'committee_name': video.content_object.name,
                'embed_link': video.embed_link,
            }}
        else:
            return {'status':False,'msg':'no videos'}
    else:
        return {'status':False,'msg':'locked'}

def _update_video(id,is_done):
    video=Video.objects.get(id=id)
    video.is_processing_remotely=False
    if is_done:
        video.is_done_processing=True
        
    video.save()
    

def CommitteeUpdateAjaxView(request):
    processId=_validateReqeustGetProcessIdentifier(request)
    if processId!=False:
        action=request.GET['action']
        if action=='get_video':
            res=_get_video(processId)
        elif action=='update_video':
            res=_update_video(processId,request.GET['id'],request.GET['is_done'])
    else:
        res={'status':False,'msg':'invalid request'}
    return HttpResponse(json.dumps(res), mimetype="application/json")
