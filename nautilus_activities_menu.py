import commands
import nautilus
import os
import shutil
import sys
import urllib

import config
import model

sys.path.append(config.APPLICATION_COMMAND_PATH)

class ActivitiesMenuProvider(nautilus.MenuProvider):
    
    def __init__(self):
        pass

    def menu_activate_cb(self, menu, fileitem, key):
        filename = urllib.unquote(fileitem.get_uri()[7:])
        #FIXME: For some weird reason, calling the model from here does not seem to work
        shutil.move(filename, config.CONTEXT_PATH + key)
        
    def get_file_items(self, window, files):
        if len(files) != 1:
            return

        fileitem = files[0]

        top_menuitem = nautilus.MenuItem('ActivitiesMenuProvider::MoveToActivity', 'Move to Activity', 'Move directory to %s' % fileitem.get_name())

        submenu = nautilus.Menu()
        top_menuitem.set_submenu(submenu)

        self.acModel = model.ActivitiesModel()
        activities = self.acModel.getActivities()
        for key, value in activities.items():
            sub_menuitem = nautilus.MenuItem('ActivitiesMenuProvider::Activity%s' % key, key, key)
            sub_menuitem.connect('activate', self.menu_activate_cb, fileitem, key)
            submenu.append_item(sub_menuitem)

        return top_menuitem,
