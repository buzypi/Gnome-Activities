import gtk
import json
import sys
import time
import wnck

import model

class ApplicationSwitcher:
    def switch_application(self, screen, window):
        am = model.ActivitiesModel()
        db = model.ActivitiesDB()
        current = am.getCurrentContext()
        application_map_of_current_context = db.get_application_map_for_activity(current)
        for w in screen.get_windows():
            if application_map_of_current_context is not None and self.pid_in_application_maps_of_activity(w.get_pid(), application_map_of_current_context):
                w.set_skip_pager(False)
                w.set_skip_tasklist(False)
                w.unminimize(int(time.time()))
            else:
                w.set_skip_pager(True)
                w.set_skip_tasklist(True)
                w.minimize()
        sys.exit(0)

    def save_application_map(self, screen, window):
        am = model.ActivitiesModel()
        current = am.getCurrentContext()
        db = model.ActivitiesDB()
        application_map = []
        application_maps_for_all_activities = db.get_all_application_maps()
        for w in screen.get_windows():
            cmdline = (" ".join(open("/proc/%s/cmdline" % w.get_pid(), "r").
                    readlines()[0].split("\x00"))).strip()
            if cmdline == 'gnome-panel' or w.get_name() == 'x-nautilus-desktop':
                continue
            associated = False
            for activity_name, application_maps in application_maps_for_all_activities.items():
                if self.pid_in_application_maps_of_activity(w.get_pid(), application_maps):
                    # This application has been mapped to some activity, if it is the current
                    # activity, retain it or else, break
                    if activity_name == current:
                        associated = False
                    else:
                        associated = True
                    break
            # New unmapped application found - this was never seen before - so we are associating
            # this with the current activity
            if not associated:
                application_map.append({'name': w.get_name(), 'pid': w.get_pid(), 
                    'cmdline': cmdline})
        db.put_application_map_for_activity(current, json.JSONEncoder().encode(application_map))
        sys.exit(0)

    def pid_in_application_maps_of_activity(self, pid, application_maps):
        for application_map in application_maps:
            if application_map['pid'] == pid:
                return True
        return False

    def print_windows(self, screen, window):
        for w in screen.get_windows():
            print w.get_name()
        sys.exit(0)

    def __init__(self, action):
        screen = wnck.screen_get_default()
        if action == 'save':
            screen.connect('window-opened', self.save_application_map)
        elif action == 'switch':
            screen.connect('window-opened', self.switch_application)
        else:
            screen.connect('window-opened', self.print_windows)
        try:
            gtk.main()
        except (KeyboardInterrupt, SystemExit):
            pass

if len(sys.argv) != 2:
    print "Usage: %s <save|switch|print>" % sys.argv[0]
    sys.exit(1)

ApplicationSwitcher(sys.argv[1])
