import os
import gettext

import gi


gi.require_version('Gtk', '3.0')


LOCALEDIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'locale'
)
gettext.install('oomox', LOCALEDIR)
