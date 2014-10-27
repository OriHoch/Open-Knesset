# encoding: utf-8

import re
from django.utils.translation import ugettext as _
from knesset.browser_test_case import BrowserTestCase, on_platforms
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import By

from mks.models import Member
from committees.models import CommitteeMeeting
from actstream import action, actor_stream

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
        mkId = d.execute_script(
            "return $('.party-member-photo a[href]').first().attr('href').match(/\/member\/(\d+)\//)[1];"
        )
        mk = Member.objects.get(id=mkId)
        # add some fake committee and plenum attendance data
        for t in ['committee', 'plenum']:
            i = 0
            for cm in CommitteeMeeting.objects.filter(committee__type=t):
                action.send(mk, verb='attended', target=cm, description='committee meeting', timestamp=cm.date)
                i = i + 1
                if i > 10:
                    break
            if i == 0:
                self.fail('!!!')
        d.get(self.live_server_url+'/member/'+mkId)
        self._waitFor(EC.presence_of_element_located(By.CLASS_NAME))
        Element
