#!/usr/bin/env python

from operator import itemgetter

import commands
import gnomeapplet
import gobject
import gtk
import logging
import pygtk
import sys

import config
import model

pygtk.require('2.0')

class ActivitiesApplet(gnomeapplet.Applet):
    button = gtk.Button()

    def __init__(self, applet, iid):
        self.button.set_relief(gtk.RELIEF_NONE)
        self.button.set_label("A: (unset)")
        self.button.connect("button_press_event", self.showMenu, applet)
        applet.add(self.button)
        applet.show_all()
    
    def showMenu(self, widget, event, applet):
        if event.button == 1:
            activities = model.ActivitiesModel().getActivities()
            activities = sorted(activities.iteritems(), key=itemgetter(1), reverse=True)
            menu = []
            for activity in activities:
                menu.append([activity[0], self.switchContext, activity[0]])
            self.createAndShowMenu(event, menu)
            widget.emit_stop_by_name("button_press_event")
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.emit_stop_by_name("button_press_event")
            self.create_menu(applet)
    
    def switchContext(self, widget, context):
        commands.getoutput("python %sapplicationswitcher.py save" % config.APPLICATION_COMMAND_PATH)
        model.ActivitiesModel().switchContext(context)
        commands.getoutput("python %sapplicationswitcher.py switch" % config.APPLICATION_COMMAND_PATH)
        self.button.set_label("A: %s" % context)
    
    def createAndShowMenu(self, event, menuItems):
        menu = gtk.Menu()
        for menuItem in menuItems:
            item = gtk.ImageMenuItem(menuItem[0], True)
            item.show()
            item.connect("activate", *menuItem[1:])
            menu.add(item)
        menu.popup( None, None, None, event.button, event.time )
    
    def create_menu(self, applet):
        propxml="""
            <popup name="button3">
            <menuitem name="Item 1" verb="About" label="_About" pixtype="stock" pixname="gtk-about"/>
            <separator />
            <menuitem name="prefs"      verb="prefs"        label="Preferences"         pixtype="stock" pixname="gtk-properties" />
            </popup>"""
        verbs = [("About", self.showAboutDialog)]
        applet.setup_menu(propxml, verbs, None)
    
    def showAboutDialog(*arguments, **keywords):
        pass

def ActivitiesFactory(applet, iid):
    ActivitiesApplet(applet, iid)
    return gtk.TRUE

if __name__ == '__main__':
    gobject.type_register(ActivitiesApplet)
    if len(sys.argv) == 2:
        if sys.argv[1] == "run-in-window":
            mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
            mainWindow.set_title("Ubuntu System Panel")
            mainWindow.connect("destroy", gtk.main_quit)
            applet = gnomeapplet.Applet()
            ActivitiesApplet(applet, None)
            applet.reparent(mainWindow)
            mainWindow.show_all()
            gtk.main()
            sys.exit()
    else:
        gnomeapplet.bonobo_factory("OAFIID:GNOME_Activities_Factory", gnomeapplet.Applet.__gtype__, "Activities", "1.0", ActivitiesFactory)
