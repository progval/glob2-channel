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

__module_name__ = "Tournois glob2 by ProgVal" 
__module_version__ = "0.1" 
__module_description__ = "Tournaments managment for #glob2 @ OFTC"

# Load the configuration :
config_file = open("/home/progval/.xchat2/glob2-tournament.cfg", 'r+')
config = SafeConfigParser()
config_file.seek(0)
config.readfp(config_file)

if not config.has_section("config"):
	config.add_section("config")
if not config.has_option("config", "number_of_games"):
	config.set("config", "number_of_games", "0")

# Define constants :
MATCH_NOT_INITIALIZED = 0
MATCH_INITIALIZED = 1
MATCH_IN_PROGRESS = 2

current_match = {"state": MATCH_NOT_INITIALIZED}

def write_conf():
	'''Call this function to save the SafeConfigParser into the configuration file'''
	config_file.seek(0)
	config.write(config_file)

def catch_msg(words, words_eol, userdata):	
	global current_match
	nick = words[0]
	message = words[1]
	
	splitted_message = message.split(" ")
	
	if splitted_message[0] != "!tournament" or xchat.get_info("network") != "OFTC":
		return
	
	if len(splitted_message) == 1:
		xchat.command("MSG %s The command `!tournament` manages the tournament. The fellowing parameters show you informations : `now?` (what is the current state and what you can do), `top?` (the top of the players)" % xchat.get_info("channel"))
	elif splitted_message[1] == "initgame":
		if current_match["state"] != MATCH_NOT_INITIALIZED:
			xchat.command("MSG %s A game is already initialized/in progress. Please subscribe to it or wait." % xchat.get_info("channel"))
		else:
			current_match.update({"state": MATCH_INITIALIZED, "owner": nick, "players": []})
			xchat.command("MSG %s The match has been initialized by %s. Ask the players to type `!tournament joingame` to join the game. Once every player has joined the game, type `!tournament startgame`." % (xchat.get_info("channel"), nick))
	elif splitted_message[1] == "joingame":
		if current_match["state"] == MATCH_NOT_INITIALIZED:
			xchat.command("MSG %s The game is not initialized ; please use `!tournament initgame`." % xchat.get_info("channel"))
		elif current_match["state"] == MATCH_IN_PROGRESS:
			xchat.command("MSG %s A game is in progress ; please wait it to finish." % xchat.get_info("channel"))
		elif nick in current_match["players"]:
			xchat.command("MSG %s You already joined the game." % xchat.get_info("channel"))
		elif not nick.startswith("[YOG]"):
			xchat.command("MSG %s You need to be connected through YOG to join a game." % xchat.get_info("channel"))
		else:
			current_match["players"].append(nick)
			xchat.command("MSG #glob2 %s joined the game." % nick[len("[YOG]"):])
	elif splitted_message[1] == "startgame":
		if current_match["state"] != MATCH_INITIALIZED:
			xchat.command("MSG %s No game is initialized. Type `!tournament initgame`." % xchat.get_info("channel"))
		elif nick != current_match["owner"]:
			xchat.command("MSG %s You are not allowed to start the game. Please ask %s to start it." % (xchat.get_info("channel"), current_match["owner"]))
		else:
			current_match.update({"state": MATCH_IN_PROGRESS})
			xchat.command("MSG #glob2 A tournament game has just been started ! Here are the players : %s. Once the game is finished, %s will report the winners with `!tournament results <FIRST_WINNER> <SECOND_WINNER>` and so on." % (" ".join(current_match["players"]), current_match["owner"]))
	elif splitted_message[1] == "results":
		if current_match["state"] != MATCH_IN_PROGRESS:
			xchat.command("MSG %s Error : no game is in progress." % xchat.get_info("channel"))
		elif nick != current_match["owner"]:
			xchat.command("MSG %s You are not allowed to start the game. Please ask %s to report the results." % (xchat.get_info("channel"), current_match["owner"]))
		elif len(splitted_message) == 2: # No player name
			xchat.command("MSG %s Please add a list of the winners after this command." % xchat.get_info("channel"))
		else:
			number_of_games = config.getint("config", "number_of_games") + 1
			config.set("config", "number_of_game", str(number_of_games))
			section = "game_%i" % number_of_games
			config.add_section(section)
			for player in current_match["players"]:
				if player in splitted_message[2:]:
					config.set(section, player, "")
				else:
					config.set(section, player, "0")
			write_conf()
			current_match = {"state": MATCH_NOT_INITIALIZED}
			xchat.command("MSG #glob2 The tournament game has been finished. You can start a new one with `!tournament initgame`.")
	elif splitted_message[1] == "now?":
		if current_match["state"] == MATCH_NOT_INITIALIZED:
			xchat.command("MSG %s No match is initialized. Use `!tournament initgame` to start it." % xchat.get_info("channel"))
		elif current_match["state"] == MATCH_INITIALIZED:
			xchat.command("MSG %s A match owned by %s is waiting for players. Use `!tournament joingame` or `!tournament startgame`." % (xchat.get_info("channel"), current_match["owner"]))
		elif current_match["state"] == MATCH_IN_PROGRESS:
			xchat.command("MSG %s A match owned by %s is in progress. Please wait while it is running." % (xchat.get_info("channel"), current_match["owner"]))
	elif splitted_message[1] == "top?":
		players = {}
		for game_name in config.sections():
			print game_name
			if not game_name.startswith("game_"):
				continue
			for player in config.options(game_name):
				if not players.has_key(player):
					players.update({player: 0})
				if config.getboolean(game_name, player):
					players.update({player: players[player] + 1})
				else:
					players.update({player: players[player] - 1})
					
		top_string = ""
		sorted_list = sorted(players.items(), key=lambda x: x[1])
		sorted_list.reverse()
		for player, count in sorted_list:
			if len(top_string) > 200:
				break
			top_string = top_string + " %s(%i)" % (player, count)
		xchat.command("MSG %s Here is the top of the players at the tournament : %s" % (nick, top_string))
			
			
		
			
	
# Hook the functions to XChat
xchat.hook_print(name="Private Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Channel Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
xchat.hook_print(name="Your Message", callback=catch_msg, userdata=None, priority=xchat.PRI_NORM)
