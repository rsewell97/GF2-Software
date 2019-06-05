#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
from wx.lib.mixins.inspection import InspectionMixin
import builtins
import getopt
import sys
import os

import wx

from main_project.names import Names
from main_project.devices import Devices
from main_project.network import Network
from main_project.monitors import Monitors
from main_project.scanner import Scanner
from main_project.parse import Parser
from main_project.main_gui import Gui
from main_project.error import Error

#_________________IMPORTANT: CHANGE GUI MODULE________________#


# language domain
langDomain = "LOGIC SIM APP"
# languages you want to support
supLang = {u"en": wx.LANGUAGE_ENGLISH,
           u"fr": wx.LANGUAGE_FRENCH
           }


def _displayHook(obj):
    if obj is not None:
        print(repr(obj))


# add translation macro to builtin similar to what gettext does
builtins.__dict__['_'] = wx.GetTranslation


class BaseApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init()  # InspectionMixin
        # work around for Python stealing "_"
        sys.displayhook = _displayHook

        self.appName = "Logic Simulator"

        return True


    def updateLanguage(self, lang):
        """
        Update the language to the requested one.

        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes

        """
        # if an unsupported language is requested default to English
        print(lang)
        if lang in supLang:
            selLang = supLang[lang]
        else:
            selLang = wx.LANGUAGE_ENGLISH
        print(selLang)

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(langDomain)
        else:
            self.locale = None


app = BaseApp()

# I18n
builtins._ = wx.GetTranslation
locale = wx.Locale()
locale.Init(wx.LANGUAGE_DEFAULT)
locale.AddCatalogLookupPathPrefix('./main_project/.locale')
locale.AddCatalog('po_file')

gui = Gui("Logic Simulator")
gui.Show(True)
app.MainLoop()
