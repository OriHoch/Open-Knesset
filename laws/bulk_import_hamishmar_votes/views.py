from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from forms import BulkImportHamishmarVotesForm
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from knesset_data.non_knesset_data.hamishmar_votes import HamishmarVote
from mks.models import Member
from django.db.models import Q


class OknessetHamishmarVote(HamishmarVote):

    def __init__(self, data):
        super(OknessetHamishmarVote, self).__init__(data)
        self.num_voted_for = len(self.voted_for_member_names)
        self.num_voted_against = len(self.voted_against_member_names)
        self.errors = self.get_errors()

    def get_errors(self):
        errors = []
        # member_ids = self.voted_for_member_ids + self.voted_against_member_ids
        member_ids = [999992234]
        missing_member_ids = []
        for member_id in member_ids:
            qs = Member.objects.filter(id=str(member_id))
            if not qs.count() == 1:
                missing_member_ids.append(str(member_id))
        if len(missing_member_ids) > 0:
            errors.append('could not find member ids: %s'%','.join(missing_member_ids))
        return errors


@csrf_protect
@staff_member_required
def bulk_import_hamishmar_votes(request):
    context = {
        'LANGUAGE_CODE': 'HE',
        'LANGUAGE_BIDI': True,
    }
    if request.method == 'POST':
        file = request.FILES['file']
        hamishmar_votes = OknessetHamishmarVote.get_from_csv(file)
        context.update({
            'msg': 'Please approve the votes' if len(hamishmar_votes) > 0 else 'No votes in file',
            'approve_votes': hamishmar_votes
        })
    else:
        context.update({'form': BulkImportHamishmarVotesForm()})
    context.update(csrf(request))
    return render_to_response('laws/bulk_import_hamishmar_votes/main.html', context)
