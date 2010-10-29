#! /usr/bin/python
# -*- coding: utf-8 -*-

###
# Copyright (c) 2010, Valentin Lorentz     
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import re
import urllib2
import time

import xchat

__module_name__ = "glob2 feed reader by ProgVal" 
__module_version__ = "0.1" 
__module_description__ = "News reader for glob2 channel"

forum_feed_regex = re.compile('<a href="\./(?P<topic_url>[^"]*)&amp;sid=[^"]*" class="topictitle">(?P<topic_title>[^<]*)</a>([^a-zA-Z0-9]*<img src="[^"]*" width="[^"]*" height="[^"]*" alt="[^"]*" title="[^"]*" />)?[^a-zA-Z0-9]*<br />[^a-zA-Z0-9]*by <a href="\./(?P<user_link>[^"]*)&amp;sid=[^"]*">(?P<user_name>[^<]*)</a>')

# The last topic displayed : 
threads_already_displayed = []

def get_threads():
    threads = forum_feed_regex.findall(urllib2.urlopen(
     'http://globulation2.org/forums/search.php?search_id=unanswered').read(),
     re.DOTALL)
    return threads

threads = get_threads()
for thread in threads:
	threads_already_displayed.append(thread)

def fetch_forum(userdata):
    global threads_already_displayed
    threads = get_threads()
    for thread in threads:
        is_found = False
        for thread_already_displayed in threads_already_displayed:
            if thread[0] == thread_already_displayed[0]:
                is_found = True
                break
        if not is_found:
            userdata.command("MSG #glob2 New thread in the forum : `%s` by %s."
                             " http://globulation2.org/forums/%s" % (thread[1],
                             thread[4], thread[0].replace("&amp;", "&")))
            threads_already_displayed.append(thread)
    return 1

xchat.hook_timer(5*60*1000, fetch_forum, xchat.find_context(channel="#glob2"))
