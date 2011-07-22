#!/usr/bin/python
#
# PINmemory - Personal Information Number storage using AES encryption
# Includes an exception harness for "Python for S60" stand-alone programs
# 
# Copyright (c) 2009 Patrik Sandenvik
# 
# Licensed under the MIT License ( http://www.opensource.org/licenses/mit-license.php ):
#

__exec_path = "E:\\Python\\"

SIS_VERSION = "0.8.1"

try:
    # Actual program goes here.
    import sys
    sys.path.append(__exec_path)
    import PINmemory
    PINmemory.View()
except:
    import sys
    import traceback
    import e32
    import appuifw
    appuifw.app.screen = "normal"               # Restore screen to normal size.
    appuifw.app.focus = None                    # Disable focus callback.
    body = appuifw.Text()
    appuifw.app.body = body                     # Create and use a text control.
    exitlock = e32.Ao_lock()
    def exithandler(): exitlock.signal()
    appuifw.app.exit_key_handler = exithandler  # Override softkey handler.
    appuifw.app.menu = [(u"Exit", exithandler)] # Override application menu.
    body.set(unicode("\n".join(traceback.format_exception(*sys.exc_info()))))
    exitlock.wait()                             # Wait for exit key press.
    appuifw.app.set_exit()
