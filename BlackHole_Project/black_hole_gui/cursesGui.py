'''
Created on Oct 24, 2012

@author: Nicolas Rebagliati (nicolas.rebagliati@aenima-x.com.ar)
'''
# -*- coding: utf-8 -*-
import os
import urwid
import urwid.raw_display
from datetime import datetime
import language
from secureShellClient import SecureShellClient
from time import time
from loger import Loger
from chatGUI import *
import black_hole

################ Global Functions
# global cache of directory information
global _environments_cache
global _environments_cache_list

_environments_cache = {}
_environments_cache_list = []

def store_initial_environment(initial, end):
    """Store the initial current working directory path components."""
    global _initial_environment, _end_environment
    _initial_environment = initial
    _end_environment = end
   
def get_environment(name):
    """Return the Directory object for a given path.  Create if necessary."""  
    return _environments_cache[name]

def get_next_environment(name):    
    index = _environments_cache_list.index(name)
    if index < len(_environments_cache_list) - 1:
        return _environments_cache[_environments_cache_list[index + 1]]
    return False

def get_prev_environment(name):    
    index = _environments_cache_list.index(name)
    if index > 0:
        return _environments_cache[_environments_cache_list[index - 1]]
    return False

def set_blackHole(blackHole):
    global _blackHole 
    _blackHole= blackHole
    
def get_blackHole():
    return _blackHole

def set_cache(user, environment):
    _environments_cache[environment.name] = EnvironmentStore(user, environment)
    _environments_cache_list.append(_environments_cache[environment.name].environment) 

    
################ Classes
class TreeWidget(urwid.WidgetWrap):
    """A widget representing something in the file tree.
    * environment: string with the name of the environment
    * name: string with the name of the object
    * index: integer with the index of the object
    * display:
    * description: string with the description of the object
    """
    def __init__(self, environment, name, index, display, description):
        self.environment = environment
        self.name = name
        self.index = index
        self.description = description
        w = urwid.AttrWrap(self.widget, None)
        self.__super.__init__(w)
        self.selected = False 
        self.update_w()
       
    def selectable(self):
        return True
    
    def keypress(self, (maxcol,), key):
        """Toggle selected on space, ignore other keys."""
        if key == " ":
            self.selected = not self.selected
            self.update_w()
        else:
            return key

    def update_w(self):
        """
        Update the attributes of wrapped widget based on self.selected.
        """
        if self.error:
            self._w.attr = 'error'
            self._w.focus_attr = 'focus_error'
        else:
            self._w.attr = 'body'
            self._w.focus_attr = 'focus'
        
    def first_child(self):
        """Default to have no children."""
        return None
    
    def last_child(self):
        """Default to have no children."""
        return None
    
    def next_inorder(self):
        """Return the next TreeWidget depth first from this one."""
        return get_environment(self.environment).next_inorder_from(self.index, self.name)
            
    def prev_inorder(self):
        """Return the previous TreeWidget depth first from this one."""
        return get_environment(self.environment).prev_inorder_from(self.index, self.name)

class EnvironmentTree(TreeWidget):
    def __init__(self, environment, index):
        self.error = False
        self.environmentObject = environment
        self.widget = urwid.Text([""])
        self.__super.__init__(self.environmentObject.name, self.environmentObject.name, index, "", self.environmentObject.description)
        self.expanded = False
        self.numberOfHosts = len(get_blackHole().data.user.profile.hosts.filter(host__environment=self.environmentObject))
        self.update_widget()
        
    def next_inorder(self):
        if not self.expanded:
            nextEnvironment = get_next_environment(self.name)
            if nextEnvironment:
                return nextEnvironment.environment_w
            else:
                return None
        else:
            return self.first_child()
        
    def prev_inorder(self):
        prevEnvironment = get_prev_environment(self.name)
        if  prevEnvironment:
            if prevEnvironment.environment_w.expanded == False:
                return prevEnvironment.environment_w
            else:
                return prevEnvironment.environment_w.last_child()
            
    def update_widget(self):
        """Update display widget text."""
        if self.expanded:
            mark = "[-]"
        else:
            mark = "[+]"
        self.widget.set_text(["", ('environmentMark', mark), " ", _("%(description)s Hosts: %(hostsCount)s") % {'description':self.description,'hostsCount': self.numberOfHosts}]) 

    def keypress(self, (maxcol,), key):
        """Handle expand & collapse requests."""   
        if key in [" ", "enter"]  :
            self.expanded = not self.expanded
            self.update_widget()
        else:
            return self.__super.keypress((maxcol,), key)            
    
    def mouse_event(self, (maxcol,), event, button, col, row, focus):
        if event != 'mouse press' or button != 1:
            return False
        if row == 0 and col < 3:
            self.expanded = not self.expanded
            self.update_widget()
            return True      
        return False   
    
    def first_child(self):
        """Return first child if expanded."""
        if self.expanded == False:
            return get_environment(self.environment).environment_w
        return get_environment(self.environment).get_first()
    
    def last_child(self):
        """Return last child if expanded."""      
        if self.expanded == False:
            return get_environment(self.environment).environment_w
        else:
            return get_environment(self.environment).get_last()
            
class HostTree(TreeWidget):
    def __init__(self, environment, hostConnection, index):
        self.error = False
        self.hostObject = hostConnection.host
        self.hostConnectionObject = hostConnection
        self.__lastClick = 0
        self.__doubleClick = False  
        self.pk = False 
        self.widget = urwid.Text(["  "*1, "%s - %s" % (self.hostObject.name, self.hostObject.description)])
        self.__super.__init__(environment.name, self.hostObject.name, index, self.hostObject.name, self.hostObject.description)
    
    def setError(self, message=False):
        if message:
            messageString = message
        else:
            messageString = "ERROR"
        self.widget = urwid.Text(["  "*1, "%s - %s [%s]" % (self.hostObject.name, self.hostObject.description, messageString)])
        self.error = True
        self._w = w = urwid.AttrWrap(self.widget, None)
        self.update_w()
        
    def mouse_event(self, (maxcol,), event, button, col, row, focus):
        if event != 'mouse press' or button != 1:
            return False
        else:
            if row == 0 and col < len(self.widget.get_text()[0]):
                clickTime = time()
                if self.__lastClick != 0:
                    if clickTime - self.__lastClick < 1:
                        self.__doubleClick = True
                    else:
                        self.__doubleClick = False
                self.__lastClick = clickTime
                return True
            else:
                self.__doubleClick = False
            return False 

    def lastWasDoubleClick(self):
        if self.__doubleClick:
            return True
        else:
            return False
        
class BlackHoleBrowser(object):   
    def __init__(self, blackHole):
        #Define global access for other classes, ugly!!
        set_blackHole(blackHole)
        self.blackHole = blackHole
        self.user = blackHole.data.user
        self.palette = [
        ('body', 'black', 'light gray'), # Normal Text
        ('focus', 'light green', 'black', 'standout'), # Focus
        ('head', 'yellow', 'dark gray', 'standout'), # Header
        ('foot', 'light gray', 'dark gray'), # Footer Separator
        ('key', 'light green', 'dark gray', 'underline'),
        ('title', 'white', 'black', 'bold'),
        ('environmentMark', 'dark blue', 'light gray', 'bold'),
        ('focus_error', 'dark red', 'black'),
        ('error', 'dark red', 'light gray', 'bold'),
        ('footer_msg', 'yellow', 'dark gray'),
        ]
        self.footer_text = [
        ('footer_msg', _("Move:")), " ",
        ('key', _("up")), ",", ('key', _("down")), ",",
        ('key', _("home")), ",",
        ('key', _("end")), ",",
        ('key', _("left")), ",",
        ('key', _("w/Mouse")), " ",
        ('footer_msg', _("Expand:")), " ",
        ('key', "space"), ",", ('key', "click"), " ",
        ('footer_msg', _("Select:")), " ",
        ('key', "enter"), ",",
        ('key', _("DoubleClick")), "  ",
        ('footer_msg', _("Quit:")), " ",
        ('key', "q"), "  ",
        ('footer_msg', "\nChat:"), " ",
        ('key', "c" if self.blackHole.settings.chat_enabled else _("Disabled")  ), "  ",
        ('footer_msg', "By:"), " ",
        ('key', "%s [%s]" % (black_hole.get_author(),
                             black_hole.get_author_email())), ]               
        self.quit = False
        try:
            self.listbox = urwid.ListBox(EnvironmentWalker(self.user))
        except Exception as e:
            raise Exception("[!] %s" % e.message)
        self.listbox.offset_rows = 1
        self.header = urwid.AttrWrap(urwid.Text(self.footer_text), 'foot')
        self.header.set_align_mode('center')
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text), 'foot')
        self.footer.set_align_mode('center')
        self.view = urwid.Frame(
                urwid.AttrWrap(self.listbox, 'body'),
                header=urwid.AttrWrap(self.header, 'head'),
                footer=self.footer)        
            
    def main(self):
        """
        Run the browser.
        """
        try:
            while not self.quit:
                self.ui = urwid.raw_display.Screen()            
                self.ui.register_palette(self.palette)
                self.ui.run_wrapper(self.run)
                os.system('clear')
        except Exception as e:
            raise Exception(e.message)
    
    def run(self):
        """Handle user input and display updating."""
        try:
            self.ui.tty_signal_keys('undefined', 'undefined', 'undefined', 'undefined', 'undefined')
            self.ui.set_mouse_tracking()
            self.size = self.ui.get_cols_rows()
            while 1:          
                focus, _ign = self.listbox.body.get_focus()
                self.header_text = [
            ('footer_msg', "BlackHole (v%s)" % black_hole.get_version()) , " ",
            ('footer_msg', _("User:")) , " ",
            ('key', "%s" % self.user.getFullName()), " ",
            ('footer_msg', _("- Selected:")) , " ",
            ('key', "%s" % focus.description),
            ]
                self.header.set_text(self.header_text)
                canvas = self.view.render(self.size, focus=1)
                self.ui.draw_screen(self.size, canvas)
                keys = None
                while not keys:
                    keys = self.ui.get_input()
                for k in keys:
                    if urwid.is_mouse_event(k):
                        event, button, col, row = k
                        self.view.mouse_event(self.size, event, button, col, row, focus=True)
                        _widget, _tupla = self.listbox.get_focus()
                        if isinstance(_widget, HostTree):
                            if _widget.lastWasDoubleClick() and event == 'mouse press':
                                self.validate(_widget)
                    else:
                        if k == 'window resize':
                            self.size = self.ui.get_cols_rows()
                        elif k in ('q', 'Q'):
                            self.quit = True
                            self.stopUI()
                            return
                        elif k in ('c', 'C'):
                            if self.blackHole.settings.chat_enabled:
                                self.stopUI()
                                self.startChat()
                                self.startUI()
                            Loger.write(_("Chat not Enabled"))
                        elif k == 'right':
                            # right can behave like +
                            k = "+"
                        k = self.view.keypress(self.size, k)
                        if k == "enter":
                            _widget, _tupla = self.listbox.get_focus()
                            if isinstance(_widget, HostTree):
                                self.validate(_widget)
                            else:
                                continue
                        elif k == 'left':
                            self.move_focus_to_parent(self.size)
                        elif k == '-':
                            self.collapse_focus_parent(self.size)
                        elif k == 'home':
                            self.focus_home(self.size)
                        elif k == 'end':
                            self.focus_end(self.size)
        except Exception as e:
                raise Exception(e.message)
    
    def validate(self, widget):
        if not widget.error:
            if self.blackHole.data.user.timeEnabled:
                    now = datetime.now().time().replace(second=0)
                    if not (self.blackHole.data.user.timeFrom < now < self.blackHole.data.user.timeTo):
                        widget.setError(_("Login is not allowed"))
                        return
            proceedSession = False
            message = None 
            environment = widget.hostObject.environment         
            proceedSession, message = self.isEnvironmentAllowed(environment)
            if proceedSession:
                user = widget.hostConnectionObject.getConnectionUser(self.blackHole.data.user)
                pk = self.blackHole.getPrivateKey(user, environment)
                if pk:
                    widget.pk = pk
                    self.startSSH(widget)
                else:
                    widget.setError(_("Private Key Missing or Invalid Format"))
            else:
                widget.setError(message)    
                    
    def isEnvironmentAllowed(self, environment):
        if self.blackHole.data.user.allowedByEnvironments.all():
            if environment not in self.blackHole.data.user.allowedByEnvironments.all():
                return False, _("Login to this host is not allowed")
            else:
                return True, None
        else:
            return True, None
                
    def startSSH(self, widget):
        self.stopUI()
        os.system('clear')
        print(_("Login to %(host)s [%(user)s] Date: %(date)s ........\n") % {'host':widget.hostObject.name,
                                                                             'user':widget.hostObject.description,
                                                                             'date':datetime.now().strftime("%Y-%m-%d %H:%M")})
        try:
            newClient = SecureShellClient(self.blackHole, widget, self.size)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            widget.setError(e.message)
        finally:
            self.startUI()
            
    def startUI(self):
        self.ui.start()
        self.ui.set_mouse_tracking()
        self.ui.tty_signal_keys('undefined', 'undefined', 'undefined', 'undefined', 'undefined')
        self.size = self.ui.get_cols_rows()

    def stopUI(self):
        self.ui.stop()
    
    def startChat(self):
        try:
            chatGui = chatGUI(self.user)
            chatGui.main()
        except Exception as e:
            CursesMessage.msgBox(e)

            
    def collapse_focus_parent(self, size):
        """Collapse parent directory."""      
        widget, pos = self.listbox.body.get_focus()
        self.move_focus_to_parent(size)    
        pwidget, ppos = self.listbox.body.get_focus()
        if widget.name != pwidget.name:
            self.view.keypress(size, "-")

    def move_focus_to_parent(self, size):
        """Move focus to parent of widget in focus."""        
        middle, top, bottom = self.listbox.calculate_visible(size)
        row_offset, focus_widget, focus_pos, focus_rows, cursor = middle
        trim_top, fill_above = top
        parent = focus_widget.environment
        name = focus_widget.name
        if parent == focus_widget.name:
            self.focus_home(size)
            return
        self.listbox.change_focus(size, (parent, parent))
        return 
        
    def focus_home(self, size):
        """Move focus to very top."""       
        amb = get_environment(_initial_environment)
        widget = amb.get_first()
        parent, name = widget.environment, widget.name
        self.listbox.change_focus(size, (parent, name))

    def focus_end(self, size):
        """Move focus to far bottom."""     
        maxrow, maxcol = size
        amb = get_environment(_end_environment)
        widget = amb.get_last()
        parent, name = widget.environment, widget.name
        self.listbox.change_focus(size, (parent, name), maxrow - 1)

class EnvironmentWalker(urwid.ListWalker):
    def __init__(self, user):
        userEnvironments = user.profile.getEnvironments()
        if len(userEnvironments) > 0:
            initialEnvironmentName = userEnvironments[0].name
            lastEnvironmentName = userEnvironments[-1].name
            store_initial_environment(initialEnvironmentName, lastEnvironmentName)
            for environment in userEnvironments:
                set_cache(user, environment)
            widget = get_environment(initialEnvironmentName).environment_w
            self.focus = initialEnvironmentName, widget.name
        else:
            raise Exception(_("The Profile has no hosts."))

    def get_focus(self):
        """
        get the widget in focus
        """
        parent, name = self.focus
        widget = get_environment(parent).get_widget(name)
        return widget, self.focus
        
    def set_focus(self, focus):
        """
        set focus in especific widget
        """
        parent, name = focus
        self.focus = parent, name
        self._modified()
    
    def get_next(self, start_from): 
        """
        get next widget
        """
        parent, name = start_from
        widget = get_environment(parent).get_widget(name)
        target = widget.next_inorder()  
        if target is None:
            return None, None
        return target, (target.environment, target.name)

    def get_prev(self, start_from):
        """
        get previous widget
        """
        parent, name = start_from
        widget = get_environment(parent).get_widget(name)
        target = widget.prev_inorder()
        if target is None:
            return None, None
        return target, (target.environment, target.name)
    
class EnvironmentStore(object):
    """Stores the environment and its hosts as Tree widgets
    * environments: environment object"""    
    def __init__(self, user, environment):
        self.environment = environment.name
        self.environmentObject = environment
        self.environment_w = EnvironmentTree(self.environmentObject, 0)       
        self.widgets = {}   
        self.items = []
        self.setHosts(user)
    
    def getHostsCount(self):
        return len(self.items)

    def setHosts(self, user):
        """Crea los objetos equipos.
        Tengo que pasar una lista, que contenga una lista con los equipos de cada ambiente.
        y en el index 0 el ambiente"""
        j = 0
        for hostConnection in user.profile.hosts.filter(host__environment=self.environmentObject).order_by('host__name'):
            self.widgets[hostConnection.host.name] = HostTree(self.environmentObject, hostConnection, j)
            self.items.append(hostConnection.host.name)
            j += 1    
            
    def get_widget(self, name):
        """Return the widget for a given file.  Create if necessary."""
        if name == self.environment:
            return self.environment_w
        else:
            return self.widgets[name]       
      
    def next_inorder_from(self, index, name):
        """Return the TreeWidget following index depth first."""       
        if index < len(self.items) - 1:
                index += 1
                return self.get_widget(self.items[index])                
        else:
            nextEnvironment = get_next_environment(self.environment)
            if nextEnvironment:
                return nextEnvironment.environment_w
            else:
                return None        
                  
    def prev_inorder_from(self, index, name):
        """Return the TreeWidget preceeding index depth first."""         
        if index > 0:
            index -= 1
            return   self.get_widget(self.items[index]) 
        else:
            return self.environment_w

    def get_first(self):
        """Return the first TreeWidget in the directory."""   
        if self.environment_w.expanded == True:
            return self.get_widget(self.items[0])
        else:
            return self.environment_w
    
    def get_last(self):
        """Return the last TreeWIdget in the directory."""     
        if self.environment_w.expanded == True:  
            return self.get_widget(self.items[-1])
        else:
            return self.environment_w
        
class CursesMessage(object):
    palette = [
        ('body', 'black', 'light gray'), # Normal text
        ('focus', 'light green', 'black', 'standout'), # Focus
        ('head', 'yellow', 'dark gray', 'standout'), # Header
        ('foot', 'light gray', 'dark gray'), # Footer separator
        ('key', 'light green', 'dark gray', 'underline'), # keys posibles
        ('title', 'white', 'black', 'bold'), #Footer Tittle
        ('environmentMark', 'black', 'light gray', 'bold'), # environment
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'), # Missing Key
        ('footer_msg', 'yellow', 'dark gray', 'bold'),
        ]    
    @staticmethod
    def msgBox(message):
        width = ('relative', 50)
        height = ('relative', 20)
        body = urwid.Filler(urwid.Divider(), 'top')
        frame = urwid.Frame(body, focus_part='footer')
        frame.header = urwid.Pile([urwid.Text(message), urwid.Divider()])
        w = frame
        w = urwid.Padding(w, ('fixed left', 2), ('fixed right', 2))
        w = urwid.Filler(w, ('fixed top', 1), ('fixed bottom', 1))
        w = urwid.AttrWrap(w, 'body')
        w = urwid.Columns([w, ('fixed', 2, urwid.AttrWrap(
            urwid.Filler(urwid.Text(('border', '  ')), "top"), 'shadow'))])
        w = urwid.Frame(w, footer=urwid.AttrWrap(urwid.Text(('border', '  ')), 'shadow'))
        w = urwid.Padding(w, 'center', width)
        w = urwid.Filler(w, 'middle', height)
        w = urwid.AttrWrap(w, 'border')
        l = []
        for name, exitcode in [("OK", 0)]:
            b = urwid.Button(name, CursesMessage.button_press)
            b.exitcode = exitcode
            b = urwid.AttrWrap(b, 'selectable', 'focus')
            l.append(b)
            buttons = urwid.GridFlow(l, 10, 3, 1, 'center')
            frame.footer = urwid.Pile([ urwid.Divider(),
            buttons ], focus_item=1)  
        loop = urwid.MainLoop(w, CursesMessage.palette)
        try:
            loop.run()
        except DialogExit, e:
            return CursesMessage.on_exit(e.args[0])
    @staticmethod
    def on_exit(exitcode):
        return exitcode, ""
    @staticmethod
    def button_press(button):
        raise DialogExit(button.exitcode) 
    
class DialogExit(Exception):
    pass
