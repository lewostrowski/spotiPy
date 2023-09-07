"""Spotify API wrapper"""
import argparse
import json
import requests

class Spotipy:
    def __init__(self, user_id: str, api_key: str, api_secret: str) -> None:
        """Constructor.

        :param user_id: Valid Spotify user ID.
        :type user_id: str
        :param api_key: API key from Spotify developer site.
        :type api_key: str
        :param api_secret: API secret from Spotify developer site.
        :type api_secret: str
        """
        self.user_id = user_id
        self.url = "https://api.spotify.com/v1/"
        self.auth_header = self.get_auth(api_key, api_secret)

    def get_auth(self, api_key: str, api_secret: str) -> dict:
        """Obtain autorization header.

        :return: Autorization header.
        :rtype: dict
        """
        try:
            response = requests.post("https://accounts.spotify.com/api/token", data={
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": api_secret
            })
            if response.status_code == 200:
                header = {"Authorization": "Bearer {}".format(response.json()['access_token'])}
                return header
            else:
                response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise SystemExit(e)

    def list_playlist(self) -> list:
        """List all public user's playlist.

        :return: List of tuples (playlist_id, playlist_name).
        :rtype: list
        """
        response = requests.get(f"{self.url}users/{self.user_id}/playlists", headers=self.auth_header)
        if response.status_code == 200:
            playlist = json.loads(response.text)
            return [(p["id"], p["name"]) for p in playlist["items"]]
        else:
            response.raise_for_status()


    def get_track_details(self, track_id: str) -> list:
        """Get detailed data about track (audio analysis).

        Display: key, bpm, genres

        :param track_id: Id of a track.
        :type track_id: str
        :return: Detailed data about track.
        :rtype: list
        """
        response = requests.get(f"{self.url}audio-analysis/{track_id}", headers=self.auth_header)
        if response.status_code == 200:
            track = json.loads(response.text)
            mode_map = ["minor", "major"]
            key_map = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "???"] 

            return [
                track_id, 
                key_map[track["track"]["key"]], 
                mode_map[track["track"]["mode"]], 
                track["track"]["tempo"]
            ]
        else:
            response.raise_for_status()

    def get_playlist_content(self, playlist_id: str) -> list:
        """Get playlist content.

        Display: song id, artist name, song name, album name, bpm, key

        :param playlist_id: ID of a playlist.
        :type playlist_id: str
        :return: List of tuples with song information.
        :rtype: list
        """
        response = requests.get(f"{self.url}playlists/{playlist_id}/tracks", headers=self.auth_header)
        if response.status_code == 200:
            playlist = json.loads(response.text)
            
            df = []
            for p in playlist["items"]:
                track = {
                    "id": p["track"]["id"],
                    "url": p["track"]["external_urls"]["spotify"],
                    "artist": ", ".join([a["name"] for a in p["track"]["artists"]]),
                    "name": p["track"]["name"],
                    "album": p["track"]["album"]["name"]
                }
                track_details = self.get_track_details(track["id"])
                track.update({
                    "key": track_details[1],
                    "mode": track_details[2],
                    "tempo": track_details[3]
                })
                df.append(tuple(track.values()))
            return df
        else:
            response.raise_for_status()

    def search_song(self, search: dict) -> list:
        """Search for song with given criteria.
        
        Dict construction: {"artist": None/str, "album": None/str, "track": None/str}
        """
        query = ["{}={}".format(k, search[k].replace(" ", "%20")) for k in search if search[k]]
        response = requests.get("{}search?type=track&q={}".format(self.url, "+".join(query)), headers=self.auth_header)
        if response.status_code == 200:
            results = json.loads(response.text)
            df = []
            for t in results["tracks"]["items"]:
                track = {
                    "id": t["id"],
                    "url": t["external_urls"]["spotify"],
                    "artist": ", ".join([a["name"] for a in t["artists"]]),
                    "track": t["name"],
                    "album": t["album"]["name"]
                }
                track_details = self.get_track_details(t["id"])
                track.update({
                    "key": track_details[1],
                    "mode": track_details[2],
                    "tempo": track_details[3]
                })
                df.append(tuple(track.values()))
            return df 
        else:
            response.raise_for_status()

