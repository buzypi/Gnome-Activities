import config

import commands
import json
import os
import sqlite3
import shutil
import sys

class ActivitiesDB:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB)

    def commit(self):
        self.conn.commit()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''
        create table activity_count (activity text, count int)
        ''')
        c.execute('''
        create table activity_application_map (activity text, application_map text)
        ''')
        self.commit()

    def get_activity_count(self, activity_name):
        c = self.conn.cursor()
        c.execute('''select * from activity_count where activity = ?''', (activity_name,))
        value_to_return = 0
        for row in c:
            value_to_return = int(row[1])
            break
        c.close()
        return value_to_return

    def increment_activity_count(self, activity_name):
        count = self.get_activity_count(activity_name)
        c = self.conn.cursor()
        if count == 0:
            c.execute('''insert into activity_count values (?, ?)''', (activity_name, count + 1))
        else:
            c.execute('''update activity_count set count = ? where activity = ?''', (count+1, activity_name))
        self.commit()
        c.close()

    def get_all_application_maps(self):
        c = self.conn.cursor()
        c.execute('''select activity, application_map from activity_application_map''')
        value_to_return = {}
        for row in c:
            value_to_return[row[0]] = json.JSONDecoder().decode(row[1])
        c.close()
        return value_to_return

    def get_application_map_for_activity(self, activity_name):
        c = self.conn.cursor()
        c.execute('''select application_map from activity_application_map where activity = ?''', (activity_name,))
        value_to_return = None
        for row in c:
            value_to_return = json.JSONDecoder().decode(row[0])
            break
        c.close()
        return value_to_return

    def put_application_map_for_activity(self, activity_name, application_map):
        c = self.conn.cursor()
        if self.get_application_map_for_activity(activity_name) is None:
            c.execute('''insert into activity_application_map values (?, ?)''', (activity_name, application_map))
        else:
            c.execute('''update activity_application_map set application_map = ? where activity = ?''', (application_map, activity_name))
        self.commit()
        c.close()

class ActivitiesModel:
    def __init__(self):
        self.CONTEXT_FILE = config.CONTEXT_PATH + "current"

    def getActivities(self):
        activities = {}
        for path in os.listdir(config.CONTEXT_PATH):
            full_path = os.path.join(config.CONTEXT_PATH, path)
            if os.path.isdir(full_path):
                activities[path] = ActivitiesDB().get_activity_count(path)
        return activities

    def startContext(self, context):
        if self.currentContextExists():
            print "Stop current context first"
            sys.exit(1)
        if not self.contextExists(context):
            print "Context not found - create it first"
            sys.exit(2)
        commands.getstatusoutput("ln -s %s ~/Desktop" % (config.CONTEXT_PATH + context))
        self.setCurrentContext(context)

    def contextExists(self, context):
        return os.path.exists(config.CONTEXT_PATH + context)

    def stopContext(self):
        if self.currentContextExists():
            current = self.getCurrentContext()
            commands.getstatusoutput("unlink %sDesktop" % config.HOME_DIR)
            os.remove(self.CONTEXT_FILE)

    def switchContext(self, context):
        self.stopContext()
        self.startContext(context)
        ActivitiesDB().increment_activity_count(context)
        self.restartNautilus()

    def moveToContext(self, fileitem, context):
        shutil.move(fileitem, config.CONTEXT_PATH + context)

    def getCurrentContext(self):
        if not self.currentContextExists():
            return None
        current = open(self.CONTEXT_FILE, "r").read()
        if current is not None or current != "":
            return current.strip()

    def setCurrentContext(self, context):
        f = open(self.CONTEXT_FILE, "w")
        f.write(context)
        f.close()

    def currentContextExists(self):
        return os.path.exists(self.CONTEXT_FILE)

    def restartNautilus(self):
        commands.getoutput("nautilus -q")

    def createNewContext(self, context):
        os.mkdir(config.CONTEXT_PATH + context)

    def deleteContext(self, context):
        if len(os.listdir(config.CONTEXT_PATH + context)) != 0:
            print "Context not empty"
            sys.exit(1)
        os.rmdir(config.CONTEXT_PATH + context)
