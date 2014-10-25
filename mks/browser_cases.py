# encoding: utf-8

import re
from django.utils.translation import ugettext as _
from knesset.browser_test_case import BrowserTestCase, on_platforms
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from mks.models import Member
from committees.models import CommitteeMeeting
from actstream import action

@on_platforms()
class MkCommitteePlenumTestCase(BrowserTestCase):

    def testMk(self):
        d = self.driver
        """:type : WebDriver"""
        d.get(self.live_server_url+'/')
        elt = d.find_element_by_id('nav-parties')
        """:type : WebElement"""
        elt.click()
        self._waitForTitleContains(_('Members and Parties').replace("&quot;", '"'))
        elts = d.find_elements_by_class_name('party-member-name')
        elts[0].click()
        WebDriverWait(d, 10).until(lambda d: d.current_url.find("/member/") > -1)
        match = re.search(r"/member/(\d+)/", d.current_url)
        mkId = match.group(1) if match else False
        self.assertTrue(mkId != False)
        mk = Member.objects.get(id=mkId)
        # add some committee and plenum attendance
        for t in ['committee', 'plenum']:
            i = 0
            for cm in CommitteeMeeting.objects.filter(committee__type=t):
                action.send(mk, verb='attended', target=cm, description='committee meeting', timestamp=cm.date)
                i = i + 1
                if i > 10:
                    break
        d.refresh()
        
