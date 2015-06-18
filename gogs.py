#!/usr/bin/python

import os
import requests
import shutil
import subprocess
import sys
import tempfile
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


def git_move(local, remote):
	os.environ["GIT_SSH"] = "%s/issh" % os.path.abspath(os.path.dirname(sys.argv[0]))
	d = tempfile.mkdtemp()
	subprocess.call(["git", "clone", "--mirror", local, "."], cwd=d)
	subprocess.call(["git", "push", "--mirror", remote], cwd=d)
	shutil.rmtree(d)


HOSTNAME = sys.argv[1]
USERNAME = "administrator"
PASSWORD = "redhat"
ORG = "monster-integration"

api = API("http://%s" % HOSTNAME)

for user in [USERNAME, "jim"]:
	api.user_sign_up(user, PASSWORD, "%s@example.com" % user)
	api.user_login(user, PASSWORD)
        if user == "jim":
                api.user_settings_ssh("id_dsa.pub", "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAxc/Ir6cm/PnjDbgseHB1y4SGc5WmgTwb8chz+wiVjnfQGM6AmFHVna7of0P+beYPUMUyCZO4bz+5x8kE+j6tpREHQ8Ng0HmzsaPuLpx9yrspPshL+HAqCRO0v0C31oqJzG6P92pz/tvsgMKypVvyDOcvtATRV3xkHHftyHFtwA1boB0DhAsXxrn5aXzbXXH3Kly4dNpGE5Z4WhMm4byopLCtrNPQGF8PNVyxbr2xRRDNzzdtHnX3OwNCqbvg1jpZ4vSVUOdKjX5vtE9938KGbPdJUfoXkop3VrdVoGXCckOOlEZo8q0jVWQnRFlyHWSaYFHzZfly5UmJpwaoLXMoaw== jminter")
        else:
                api.user_settings_ssh("id_dsa.pub", open("/root/.ssh/authorized_keys").read())
	api.user_logout()

api.user_login(USERNAME, PASSWORD)
api.org_create(ORG, "%s@example.com" % ORG)
api.org_invitations_new(ORG, "jim")

for repo in ["apiserver", "camel", "frontend", "webserver"]:
	api.repo_create(3, repo)
	# git_move("git://192.168.0.254/%s" % repo, "ssh://git@localhost:2222/%s/%s.git" % (ORG, repo))
	# api.repo_delete(ORG, repo, PASSWORD)

api.user_logout()
