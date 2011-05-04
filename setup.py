import commands

import config

commands.getoutput("cat GNOME_Activities.server-dist | sed 's/%s/%s/g' > GNOME_Activities.server" % ('%{APPLICATION_COMMAND_PATH}', config.APPLICATION_COMMAND_PATH.replace("/", "\/")))
commands.getoutput("sudo ln -s %sGNOME_Activities.server /usr/lib/bonobo/servers/GNOME_Activities.server" % config.APPLICATION_COMMAND_PATH)
commands.getoutput("ln -s %snautilus_activities_menu.py %s.local/share/nautilus-python/extensions/nautilus_activities_menu.py" % (config.APPLICATION_COMMAND_PATH, config.HOME_DIR))
commands.getoutput("ln -s %smodel.py %s.local/share/nautilus-python/extensions/model.py" % (config.APPLICATION_COMMAND_PATH, config.HOME_DIR))

