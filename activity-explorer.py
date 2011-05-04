import commands
import gio
import gtk
import os
import pygtk
import sys

pygtk.require('2.0')

import config

class PreferencesMgr(gtk.Window):
    locations = None
    context = None

    def __init__(self, context):
        gtk.Window.__init__(self) 
        self.context = "%s%s/" % (config.CONTEXT_PATH, context)
        self.set_decorated(False) 
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.create_gui()
        self.connect("destroy", self.destroy)
        self.move(100,100)
        self.set_opacity(0.8) 
        self.stick() 
        self.set_resizable(True)
        self.set_property("skip-taskbar-hint", True) 
        self.set_property("type-hint", gtk.gdk.WINDOW_TYPE_HINT_DESKTOP)
        self.show_all() 

    def load_icon(self, filename): 
        file_ = gio.File(filename) 
        icon = file_.query_info("standard::icon").get_icon() 
        if icon is None:
            return

        if isinstance(icon, gio.ThemedIcon): 
            theme = gtk.icon_theme_get_default() 
            icon = theme.choose_icon(icon.get_names(), 16, 0)
            if icon is None:
                return
            return icon.load_icon() 
        elif isinstance(icon, gio.FileIcon): 
            iconpath = icon.get_file().get_path() 
            return gtk.gdk.pixbuf_new_from_file(iconpath) 

        return
    
    def create_gui(self):
        model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        self.locations = os.listdir(self.context)
        for location in self.locations:
            if location is None:
                continue
            pixbuf = self.load_icon(self.context + location)
            model.append([location[:10], pixbuf])

        self.icon_view = gtk.IconView(model)
        self.icon_view.set_text_column(0)
        self.icon_view.set_pixbuf_column(1)
        self.icon_view.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.icon_view.set_selection_mode(gtk.SELECTION_SINGLE)
        self.icon_view.connect('item-activated', self.item_activate, model)
        self.icon_view.set_columns(4)
        self.icon_view.set_item_width(-1)
        self.icon_view.set_size_request(-1, -1)

        self.content_box = gtk.HBox(False)
        self.content_box.pack_start(self.icon_view, fill=True, expand=False)
        self.vbox.pack_start(self.content_box)        
        self.show_all()

    def item_activate(self, icon_view, path, model=None):
        selected = icon_view.get_selected_items()
        if len(selected) == 0: return
        i = selected[0][0]
        commands.getoutput("gnome-open %s%s" % (self.context, self.locations[i]))

    def main(self):
        gtk.main()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <context>" % sys.argv[0]
        sys.exit(1)
    p = PreferencesMgr(sys.argv[1])
    p.main()
    #p.destroy()
