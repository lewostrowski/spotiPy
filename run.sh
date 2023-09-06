#!/bin/bash

function usage() {
	echo """spotiPy launcher
  --credentials     Set credentials.
  --install         Install venv with dependencies, connect with github and proccess credentials.
  --help            Print this help.
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

credentials
