#!/bin/bash

function usage() {
	echo """spotiPy launcher
  run             Run spotiPy CLI.
  credentials     Set credentials.
  install         Install venv with dependencies, connect with github and proccess credentials.
  help            Print this help.
  """
}

function credentials() {
	echo "[!] Provide Spotify cerendetials"

	# Check for existing file.
	if [ -f credentials ]; then
		# Aks user if overwrite file.
		echo "[!] File with credentials already exists"
		read -p "[?] Overwrite? [y/n] " decision

		if [ "$decision" = "y" ]; then
			>credentials
		else
			echo "[!] Aborted"
			exit 1
		fi
	# Create file if doesn't exists.
	else
		touch credentials
	fi

	# Read user id, api key and api secret.
	for value in USERID KEY SECRET; do
		read -p "[>] $value: " temp
		echo "$value=$temp" >>credentials
	done
	echo "[!] Sredentials saved"
}

function install() {
	echo "[!] Creating virtual enviroment"
	cd spotipy_env
	python3 -m venv .

	echo "[!] Installing dependencies"
	source bin/activate
	python -m ensurepip
	pip install -r requirement.txt
	deactivate
	cd ..
}

function run() {
	echo "[!] Checking for updates"
	git pull

	echo "[!] Running virtual enviroment"
	source spotipy_env/bin/activate
	python -m spotipy_env
	echo "[!] Exiting virtual enviroment"
	deactivate
}

if [ "$1" == "run" ]; then
	run
elif [ "$1" == "credentials" ]; then
	credentials
elif [ "$1" == "install" ]; then
	install
	credentials
else
	usage
fi
