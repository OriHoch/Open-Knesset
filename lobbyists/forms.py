from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext_lazy as _

class AddLinkForm(forms.Form):

    content = forms.CharField(label=_('Content'),
                              widget=forms.Textarea(attrs={'rows': 3}))
    url = forms.CharField(widget=forms.HiddenInput, max_length=400)

    def __init__(self, *args, **kwargs):
        super(AddLinkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = 'main'
        self.helper.html5_required = True


