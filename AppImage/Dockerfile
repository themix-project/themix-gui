# older ubuntu versions have too old (unsupported) GTK+ 3 version:
FROM ubuntu:xenial

# oomox deps:
#RUN apt-get update && apt-get install -y libgdk-pixbuf2.0-dev libxml2-utils python3-gi gtk2-engines-murrine bc sed zip inkscape imagemagick optipng parallel
#RUN apt-get update && \
    #apt-get install -y software-properties-common && \
    #add-apt-repository ppa:tista/build && \
    #apt-get update && \
    #apt-get install -y sassc

# appimage deps:
RUN apt-get update && apt-get install -y --no-install-recommends wget git gettext make
# add ppa with sassc (oomox dep)
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:tista/build

# collect appimage deps:
COPY ./AppImage/Recipe.deps ./AppImage/functions.sh /src/
RUN bash /src/Recipe.deps

# build appimage:
COPY . /src/
RUN bash /src/Recipe
