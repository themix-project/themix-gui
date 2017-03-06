import os
import gettext


_localedir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          '..', 'locale')
gettext.install('oomox', _localedir)
