FROM python:3.11

COPY spotipy_env/*.py /opt/spotipy/spotipy_env/
COPY requirement.txt /opt/spotipy/
COPY spotipy /opt/spotipy/ 

WORKDIR /opt/spotipy/

RUN pip install -r requirement.txt
RUN pip install --upgrade spotdl
RUN spotdl --download-ffmpeg
RUN chmod +x spotipy

ENTRYPOINT ["./spotipy", "docker_mode"]
