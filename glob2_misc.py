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

from ConfigParser import SafeConfigParser
import time

import xchat

__module_name__ = "glob2 divers by ProgVal" 
__module_version__ = "0.1" 
__module_description__ = "Misceallenous features for #glob2 @ OFTC"

def catch_join(words, words_eol, userdata):
    nick = words[0]
    channel = words[1]
    
    if channel == "#glob2" and xchat.get_info("network") == "OFTC" and \
        not nick.lower().startswith("zenfur") and \
        not nick.lower().endswith("zenfur"):
        for user in xchat.get_list("users"):
            if user.nick.startswith("zenfur"):
                xchat.command("MSG %s %s ~> %s has just joined %s." % 
                              (user.nick, user.nick, nick, channel))
        
        

xchat.hook_print(name="Join", callback=catch_join, userdata=None,
                 priority=xchat.PRI_NORM)
