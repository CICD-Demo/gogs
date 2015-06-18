#!/usr/bin/python

import os
import re
import requests
import sys
import urllib

class API(object):
	def __init__(self, url):
		self.url = url
		self.s = requests.Session()

	def _get(self, url, *args, **kwargs):
		return self.s.get(self.url + url, *args, **kwargs)

	def _post(self, url, *args, **kwargs):
		if "_csrf" in self.s.cookies:
			args[0]["_csrf"] = urllib.unquote(self.s.cookies["_csrf"])

		return self.s.post(self.url + url, *args, **kwargs)

	def user_sign_up(self, uname, password, email):
		self._post("/user/sign_up", {"uname": uname, "password": password, "retype": password, "email": email})

	def user_login(self, uname, password):
		self._post("/user/login", {"uname": uname, "password": password})

	def user_logout(self):
		self._get("/user/logout")

	def user_settings_ssh(self, title, content):
		self._post("/user/settings/ssh", {"title": title, "content": content})

	def org_create(self, org_name, email):
		self._post("/org/create", {"org_name": org_name, "email": email})

	def org_invitations_new(self, org_name, uname):
		self._post("/org/%s/invitations/new" % org_name, {"uname": uname})

	def repo_create(self, uid, repo_name, desc=""):
		self._post("/repo/create", {"uid": uid, "repo_name": repo_name, "desc": desc, "gitignore": "Select a .gitignore file", "license": "Select a license file"})

	def repo_delete(self, owner_name, repo_name, password):
		self._post("/%s/%s/settings" % (owner_name, repo_name), {"action": "delete", "repo_name": repo_name, "password": password})


def read_env():
        for l in open(root + "/environment"):
                if l[0] in ["#", "\n"]: continue
                (k, v) = l.strip().split("=", 1)
                if v[0] in ["'", '"'] and v[-1] == v[0]:
                        v = v[1:-1]
                globals()[k] = v

root = os.path.abspath(os.path.dirname(sys.argv[0]) + "/../..")
read_env()
api = API("http://%s" % sys.argv[1])

for user in ["administrator", DEMOUSER]:
	api.user_sign_up(user, DEMOPW, "%s@%s" % (user, DOMAIN))
	api.user_login(user, DEMOPW)
        if user == DEMOUSER:
                api.user_settings_ssh("id_dsa.pub", "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAxc/Ir6cm/PnjDbgseHB1y4SGc5WmgTwb8chz+wiVjnfQGM6AmFHVna7of0P+beYPUMUyCZO4bz+5x8kE+j6tpREHQ8Ng0HmzsaPuLpx9yrspPshL+HAqCRO0v0C31oqJzG6P92pz/tvsgMKypVvyDOcvtATRV3xkHHftyHFtwA1boB0DhAsXxrn5aXzbXXH3Kly4dNpGE5Z4WhMm4byopLCtrNPQGF8PNVyxbr2xRRDNzzdtHnX3OwNCqbvg1jpZ4vSVUOdKjX5vtE9938KGbPdJUfoXkop3VrdVoGXCckOOlEZo8q0jVWQnRFlyHWSaYFHzZfly5UmJpwaoLXMoaw== jminter")
        else:
                api.user_settings_ssh("id_dsa.pub", open("/root/.ssh/authorized_keys").read())
	api.user_logout()

api.user_login("administrator", DEMOPW)
api.org_create(INTEGRATION, "%s@%s" % (INTEGRATION, DOMAIN))
api.org_invitations_new(INTEGRATION, DEMOUSER)

for repo in MONSTER_REPOS.split(" "):
        if os.path.exists(root + "/monster/" + repo + "/build.sh"):
                api.repo_create(3, repo)

api.user_logout()
