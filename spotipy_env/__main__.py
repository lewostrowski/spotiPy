"""spotiPy - CLI app 

Main module of spotiPy CLI. Run menu and orchestrate actions.
"""
import os
import json
import beaupy
from rich.console import Console
from spotipy import Spotipy

# Display spinner while loading.
wait_animation = beaupy.spinners.Spinner(beaupy.spinners.ARC, refresh_per_second=4)
# TODO(): sh launcher with updater and installer (venv) + credentials
# TODO(): module and change names to __init__ and wrapper
# TODO(): utils module
# TODO(): args for wrapper
# TODO(): dev branch
# TODO(): docs

class Menu(Spotipy):
    def __init__(self, user_id: str, api_key: str, api_secret: str):
        """Constructor.

        :param user_id: Spotify user ID.
        :type user_id: str
        :param api_key: Spotify API key.
        :type api_key: str
        :param api_secret: Spotify API secret.
        :type api_secret: str
        """
        super().__init__(user_id, api_key, api_secret)
        self.next_space = None
        self.playlist_id = None
        self.console = Console()

    def download_music(self, urls: list) -> None:
        """Download tracks.

        :param urls: Valid Spotify URL for a track (aka share link).
        :type urls: list
        """
        status_ok = True
        self.console.print("""[italic]
        Provide folder name for download. If folder already exists, ask if append.
        Type EXIT to go back main menu.
        [italic]""")

        while True:
            folder_name = beaupy.prompt("[bold][?] FOLDER NAME[/bold]").replace(" ", "_")
            if os.path.isdir(folder_name):
                self.console.print("[red][E] NAME TAKEN[/red]")
                do_append = beaupy.confirm("[bold][?] APPEND TO FOLDER?[/bold]", cursor_style="green")
                if do_append:
                    break

            elif folder_name.lower() == "exit":
                status_ok = False
                self.next_space = "MAIN"
                break
            else:
                self.console.print("[!] CREATING FOLDER [green]{}[/green].".format(folder_name))
                os.makedirs(folder_name)
                break    
    
        if status_ok:
            for u in urls:
                os.system("(cd {}; spotdl --scan-for-songs --overwrite skip {})".format(folder_name, u))


    def main(self):
        """Print main menu."""
        self.console.print("[bold][?] CHOOSE MODE[/bold]")
        self.console.print("""[italic]
        Select playlist mode to download all or selected tracks from user's playlist.
        Search mode allow to find track by artist, album or title across Spotify.
        Both will show track analysis.
        [/italic]""")

        decision = beaupy.select(["PLAYLISTS", "SEARCH", "EXIT"], cursor_style="green")

        if decision == "EXIT":
            self.console.print("[!] ABORTED")
            raise SystemExit()
        else:
            self.next_space = decision 
            self.console.print("[:] {}".format(self.next_space))


    def select_playlist(self) -> None:
        """Print playlist selection."""
        wait_animation.start()
        values = self.list_playlist() + [("0", "EXIT")]
        wait_animation.stop()

        self.console.print("[bold][?] SELECT PLAYLIST[/bold]")
        self.console.print("""[italic]
        In the next step you will be asked if all tracks should be downloaded or only selected.
        Select exit to go back to main menu.
        [/italic]""")

        decision = beaupy.select(
            [v[1].upper() for v in values], 
            return_index=True, 
            cursor_style="green")
        
        if decision == len(values) - 1:
            self.next_space = "MAIN"
        else:
            self.next_space = "SONG_LIST"
            self.playlist_id = values[decision][0]
        
        self.console.print("[:] {}".format(self.next_space.replace("_", " ")))


    def list_tracks(self, custom: dict = None):
        """List tracks and run download.

        :param custom: Overwrite tracks list and user decision.
        :type custom: dict
        """
        self.console.print("""[italic]
        In next step you will be asked for download directory and which tracks to download if relevant.
        Select EXIT to go back to playlist selection. 
        [/italic]""")

        if not custom:
            wait_animation.start()
            tracks = self.get_playlist_content(self.playlist_id)
            wait_animation.stop()

            self.console.print("[!] FOUND [green]{}[/green] TRACKS".format(str(len(tracks))))
            self.console.print("[bold][?] SELECT ACTION[/bold]")
            decision = beaupy.select(
                ["DOWNLOAD ALL", "SELECT TRACKS TO DOWNLOAD", "EXIT"],
                return_index=True,
                cursor_style="green"
            )
        else:
            tracks = custom["tracks"]
            decision = custom["decision"]

        if decision == 0:
            self.console.print("[:] DOWNLOAD ALL")
            self.download_music([t[1] for t in tracks])
            self.console.print("[green bold][!] FINISHED[/green bold]")

        elif decision == 1:
            values=[
                (t[0], " | ".join(
                [
                    str(x).replace("[", "(").replace("]", ")") 
                    if "[" in str(x) or "]" in str(x) 
                    else str(x) for x in t[2:]
                    ]
                )) for t in tracks
            ]

            decision = beaupy.select_multiple(
                [v[1] for v in values] + ["EXIT"],
                minimal_count=1,
                return_indices=True,
                tick_style="green",
                cursor_style="green",
            )

            if len(values) not in decision:
                track_to_download = [t[1] for t in tracks if tracks.index(t) in decision]
                
                self.console.print("[:] DOWNLOAD SELECTED")
                self.download_music(track_to_download)
                self.console.print("[green][!] FINISHED[/green]")
            else:
                self.console.print("[!] ABORTED")

        else:
            self.playlist_id = None

        self.next_space = "MAIN"

    def search_track(self):
        """Print search menu."""
        self.console.print("[bold][?] SEARCH TRACK[/bold]")
        self.console.print("""[italic]
        Provide sequence of artist name, album title and track title.
        Only one artist name can be provide. However, search results include multiple artists.
        Leave blank for None. Provide at least one value to search. Leave all blank to EXIT.
        [/italic]""")
        artist = beaupy.prompt("[!] ARTIST")
        album = beaupy.prompt("[!] ALBUM")
        track = beaupy.prompt("[!] TITLE")

        search = {
            "artist": artist,
            "album": album,
            "track": track
        }

        if list(search.values()) != ["", "", ""]:
            wait_animation.start()
            values = self.search_song(search)
            wait_animation.stop()
            self.list_tracks(custom={"tracks": values, "decision": 1})
        else:
            self.console.print("[red][E] EMPTY QUERY[/red]")
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
    menu.console.print("""[bold]
                         ___________[green]_______         [/green]
    _______________________  /___(_)[green]__  __ \____  __[/green]
    __  ___/__  __ \  __ \  __/_  /[green]__  /_/ /_  / / /[/green]
    _(__  )__  /_/ / /_/ / /_ _  /[green] _  ____/_  /_/ / [/green]
    /____/ _  .___/\____/\__/ /_/[green]  /_/     _\__, /  [/green]
           /_/                   [green]          /____/   [/green]
    [/bold]""", highlight=False)
    menu.console.print("[!] USER ID SET TO: [green]{}[/green]".format(menu.user_id))

    menu.main()
    while True:
        if menu.next_space == "MAIN":
            menu.main()
        if menu.next_space == "PLAYLISTS":
            menu.select_playlist()
        if menu.next_space == "SONG_LIST":
            menu.list_tracks()
        if menu.next_space == "SEARCH":
            menu.search_track()
