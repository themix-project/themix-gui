import os
import gettext


LOCALEDIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'locale'
)
gettext.install('oomox', LOCALEDIR)
