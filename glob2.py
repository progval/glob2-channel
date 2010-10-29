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
import threading

import xchat

__module_name__ = "Misc feature for glob2 by ProgVal" 
__module_version__ = "0.1" 
__module_description__ = "Misceallenous features for #glob2 @ OFTC"

# To avoid spamming
last_alert = 0

# Load the configuration :
config_file = open("/home/progval/.xchat2/glob2.cfg", 'r+')
config = SafeConfigParser()
config_file.seek(0)
config.readfp(config_file)

def write_conf():
    '''Call this function to save the SafeConfigParser into the configuration file'''
    config_file.seek(0)
    config.write(config_file)

# Add sections and options in the config file if they are not yet created.
config_map = {"subscriptions": ["ask4game", "ask4help"], "misc": ["stop_welcome"], "login_count": []}
for section in config_map:
    if not config.has_section(section):
        config.add_section(section)
    for option in config_map[section]:
        if not config.has_option(section, option):
            config.set(section, option, "")
write_conf()

# Deactived function
def greet_user(nick):
    time.sleep(2)
    print "greet !"
    for user in xchat.get_list("users"):
        print user.nick
        if user.nick == nick:
            print user.host
            print user.realname
            xchat.command("MSG #glob2 Welcome to %s, running version %s" % (nick, user.realname))
            break

def catch_whois_name_line(words, words_eol, userdata):
    if xchat.get_info("network") != "OFTC":
        return
    xchat.command("MSG #glob2 Welcome to %s, running version %s" % (words[0], words[3]))

def catch_join(words, words_eol, userdata):
    nick = words[0]
    channel = words[1]
    
    if nick.startswith("[YOG]") and not nick in config.get("misc", "stop_welcome").split(" "):
        xchat.command("MSG %s Hi %s, welcome to the globulation online game. Some people are connected from IRC, if you say there name, they may answer you or start playing. For more help, type `!help`." % (nick, nick))
    if nick.startswith("[YOG]"):
        truncated_nick = nick[len("[YOG]"):]
        if not config.has_option("login_count", truncated_nick):
            config.set("login_count", truncated_nick, "0")
        config.set("login_count", truncated_nick, str(config.getint("login_count", truncated_nick)+1))
        write_conf()
        #threading.Thread(target=greet_user, args=(nick,), name="Waiting to greet %s" % nick).start()
        xchat.command("whois %s" % nick)
        

def catch_msg(words, words_eol, userdata):    
    global last_alert
    nick = words[0]
    message = words[1]
    
    if not message.startswith("!") or xchat.get_info("network") != "OFTC":
        return
    
    if (message == "!help" and nick.startswith("[YOG]")) or message == "!help yog":
        xchat.command("MSG %s (help for YOG users:) If you are feed up with getting a welcome message each time you log in, type `!stop`. If you want to send an automatically alert to every people who wants to play but who is not reading the chat, type `!ask4game`. For more information, ask for help, with typing `!ask4help`. You can get a list of people who connects most often to YOG with `!top`." % nick)
    elif (message == "!help" and not nick.startswith("[YOG]")) or message == "!help irc":
        xchat.command("MSG %s (help for IRC users:) If you want to be notified each time someone uses `!ask4game` (game query) or `!ask4help` (help query), type `!subscribe ask4game` or `!subscribe ask4help` (depending on what you want). The inverse of `!subscribe` is `!unsubscribe`. You can get a list of people who connects most often to YOG with `!top`." % nick)
    elif message == "!stop" and not nick in config.get("misc", "stop_welcome").split(" "):
        config.set("misc", "stop_welcome", config.get("misc", "stop_welcome") + " " + nick)
        xchat.command("MSG %s %s ~> I'll never send you again the welcome message" % (xchat.get_info("channel"), nick))
        write_conf()
    elif (message == "!ask4game" or message == "!ask4help") and last_alert + 60 < time.time():
        last_alert = time.time()
        query_type = message[1:]
        nicklist = []
        for alert_nick in config.get("subscriptions", query_type).split(" "):
            for user in xchat.get_list("users"):
                if alert_nick == user.nick:
                    nicklist.append(alert_nick)
        
        if query_type == "ask4game" and xchat.get_info("network") == "OFTC":
            if len(nicklist) == 0:
                xchat.command("MSG %s %s ~> Sorry, nobody has subscribed to the alert list :s" % (xchat.get_info("channel"), nick))
            else:
                xchat.command("MSG %s %s ~> Someone is asking for a game !" % (xchat.get_info("channel"), ' & '.join(nicklist)))
        else:
            if len(nicklist) == 0:
                xchat.command("MSG %s %s ~> Sorry, no helper is available for help :s" % (xchat.get_info("channel"), nick))
            else:
                xchat.command("MSG %s %s ~> Someone is asking for help !" % (xchat.get_info("channel"), ' & '.join(nicklist)))
    elif message == "!ask4game" or message == "!ask4help":
        xchat.command("MSG %s %s ~> No more than one ask4game/ask4help each minute is allowed (please wait)" % (xchat.get_info("channel"), nick))
    elif message.startswith("!subscribe") and message.split(" ")[-1] in config_map["subscriptions"]:
        subscription_type = message.split(" ")[-1]
        if nick in config.get("subscriptions", subscription_type).split(" "):
            xchat.command("MSG %s %s ~> You are already notified each time someone use `!%s`." % (xchat.get_info("channel"), nick, subscription_type))
        else:
            config.set("subscriptions", subscription_type, config.get("subscriptions", subscription_type) + " " + nick)
            xchat.command("MSG %s %s ~> You will be notified each time someone use `!%s`." % (xchat.get_info("channel"), nick, subscription_type))
        write_conf()
    elif message.startswith("!unsubscribe") and message.split(" ")[-1] in config_map["subscriptions"]:
        subscription_type = message.split(" ")[-1]
        if not nick in config.get("subscriptions", subscription_type).split(" "):
            xchat.command("MSG %s %s ~> You are not notified each time someone use `!%s`, so, you cannot unsubscribe..." % (xchat.get_info("channel"), nick, subscription_type))
        else:
            alert_list = config.get("subscriptions", subscription_type).split(" ")
            alert_list.remove(nick)
            config.set("subscriptions", subscription_type, " ".join(alert_list))
            xchat.command("MSG %s %s ~> I'll not continue to notify you each time someone use `!%s`." % (xchat.get_info("channel"), nick, subscription_type))
        write_conf()
    elif  message.startswith("!list"):
        if len(message.split(" ")) == 1:
            xchat.command("MSG %s %s ~> Please add the subscription type after the command." % (xchat.get_info("channel"), nick))
        elif not message.split(" ")[1] in config_map["subscriptions"]:
            xchat.command("MSG %s %s ~> Sorry, this kind of subscription does not exist." % (xchat.get_info("channel"), nick))
        else:
            xchat.command("MSG %s Here are the users who subscribed to `%s` : %s" % (nick, message.split(" ")[1], config.get("subscriptions", message.split(" ")[1])))
    elif message == "!top":
        top = {}
        for logged_nick in config.options("login_count"):
            top.update({logged_nick: config.getint("login_count", logged_nick)})
        top_string = ""
        sorted_list = sorted(top.items(), key=lambda x: x[1])
        sorted_list.reverse()
        for logged_nick, count in sorted_list:
            if len(top_string) > 200:
                break
            top_string = top_string + " %s(%i)" % (logged_nick, count)
        xchat.command("MSG %s Here is the top of the people who connects most : %s" % (nick, top_string))

# Hook the functions to XChat
xchat.hook_print(name="Private Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Channel Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Your Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Join", callback=catch_join, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Whois Name Line", callback=catch_whois_name_line, userdata=None, priority=xchat.PRI_NORM)
