import os
import json
import beaupy
from rich.console import Console
from spotipy import Spotipy

wait_animation = beaupy.spinners.Spinner(beaupy.spinners.ARC, refresh_per_second=4)

class Menu(Spotipy):
    def __init__(self, user_id: str, api_key: str, api_secret: str):
        super().__init__(user_id, api_key, api_secret)
        self.next_space = None
        self.playlist_id = None
        self.console = Console()

    def download_music(self, urls: list) -> None:
        status_ok = True
        while True:
            folder_name = beaupy.prompt("[?] FOLDER NAME (OR EXIT)").replace(" ", "_")
            if os.path.isdir(folder_name):
                self.console.print("[ERROR] NAME TAKEN")
                do_append = beaupy.confirm("APPEND TO FOLDER?")
                if do_append:
                    break
            elif folder_name.lower() == "exit":
                status_ok = False
                self.next_space = "MAIN"
                break
            else:
                self.console.print("[!] CREATING FOLDER {}.".format(folder_name))
                os.makedirs(folder_name)
                break    
    
        if status_ok:
            for u in urls:
                os.system("(cd {}; spotdl {})".format(folder_name, u))


    def main(self):
        self.console.print("[?] CHOOSE MODE")
        decision = beaupy.select(["PLAYLISTS", "SEARCH", "EXIT"])
        if decision == "EXIT":
            self.console.print("[!] ABORTED")
            raise SystemExit()
        else:
            self.next_space = decision
            self.console.print("[:] CHOOSE MODE -> {}".format(self.next_space))


    def select_playlist(self) -> None:
        self.console.print("[!] LOADING PLAYLISTS")
        
        wait_animation.start()
        values = self.list_playlist()
        wait_animation.stop()

        self.console.print("[?] SELECT PLAYLIST")
        decision = beaupy.select([v[1] for v in values] + ["EXIT"], return_index=True)
        
        if decision == "EXIT":
            self.next_space = "MAIN"
        else:
            self.next_space = "SONG_LIST"
            self.playlist_id = values[decision][0]
        
        self.console.print("[:] PLAYLISTS -> {}".format(self.next_space.replace("_", " ")))


    def list_tracks(self, custom: dict = None):
        if not custom:
            self.console.print("[!] LOADING ITEMS")
            wait_animation.start()
            tracks = self.get_playlist_content(self.playlist_id)
            wait_animation.stop()

            self.console.print("[?] FOUND {} TRACKS. WHAT TO DO?".format(len(tracks)))
            decision = beaupy.select(["DOWNLOAD ALL", "SELECT TRACKS TO DOWNLOAD", "GO BACK"])
        else:
            tracks = custom["tracks"]
            decision = custom["decision"]

        if decision == "DOWNLOAD ALL":
            self.download_music([t[1] for t in tracks])
            self.console.print("[!] FINISHED")

        elif decision == "SELECT TRACKS TO DOWNLOAD":
            values=[(t[0], "  ".join([str(x )if len(str(x)) <= 30 else str(x)[:30] + " (...)" 
                for x in t[2:]])) for t in tracks]
            decision = beaupy.select_multiple(
                [v[1] for v in values] + ["EXIT"],
                minimal_count=1,
                return_indices=True
            )
            if len(values) not in decision:
                track_to_download = [t[1] for t in tracks if tracks.index(t) in decision]
            
                self.download_music(track_to_download)
                self.console.print("[!] FINISHED")
            else:
                self.console.print("[!] ABORTED")

        else:
            self.playlist_id = None

        self.next_space = "MAIN"

    def search_track(self):
        self.console.print("[!] SEARCH TRACK. LEAVE BLANK FOR None")
        artist = beaupy.prompt("[>] ARTIST: ")
        album = beaupy.prompt("[>] ALBUM: ")
        track = beaupy.prompt("[>] TITLE: ")

        search = {
            "artist": artist,
            "album": album,
            "track": track
        }
        if list(search.values()) != ["", "", ""]:
            wait_animation.start()
            values = self.search_song(search)
            wait_animation.stop()
            self.list_tracks(custom={"tracks": values, "decision": "SELECT TRACKS TO DOWNLOAD"})
        else:
            self.console.print("[ERROR] EMPTY QUERY")
            self.next_space = "MAIN"

if __name__ == "__main__":
    if "credentials.json" in os.listdir():
        with open("credentials.json", "r") as f:
            credentials = json.loads(f.read())
    else:
        print("Provide Spotify user id and API keys.")
        print("Data will be saved in json file in working directory.")
        user_id = input("user_id: ")
        api_key = input("api_key: ")
        api_secret = input("api_secret: ")

        credentials = {
            "user_id": user_id,
            "api_key": api_key,
            "api_secret": api_secret
        }

        with open("credentials.json", "w") as f:
            f.write(json.dumps(credentials))

    menu = Menu(
        credentials["user_id"],
        credentials["api_key"],
        credentials["api_secret"]
    )
    
    os.system("clear")
    menu.console.print("""
                         ___________[green]_______         [/green]
    _______________________  /___(_)[green]__  __ \____  __[/green]
    __  ___/__  __ \  __ \  __/_  /[green]__  /_/ /_  / / /[/green]
    _(__  )__  /_/ / /_/ / /_ _  /[green] _  ____/_  /_/ / [/green]
    /____/ _  .___/\____/\__/ /_/[green]  /_/     _\__, /  [/green]
           /_/                   [green]          /____/   [/green]
    """)


    menu.main()
    while True:
        if menu.next_space == "MAIN":
            menu.main()
        if menu.next_space == "PLAYLISTS":
            menu.select_playlist()
            menu.list_tracks()
        if menu.next_space == "SEARCH":
            menu.search_track()
