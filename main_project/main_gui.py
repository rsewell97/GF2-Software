#!/usr/bin/env python3
"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.stc
import wx.lib.scrolledpanel
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
from PIL import Image
import numpy as np
import random
import subprocess

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from simulator import Canvas

def scale_bitmap(bitmap, width, height):
    image = bitmap.ConvertToImage()
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(image)




class CircuitDiagram(wx.Panel):

    def __init__(self, parent, devices, network, names):
        """Initialise canvas properties and useful variables."""
        self.icons = {
            "OR": wx.Bitmap('GUI/Gates/OR.png'),
            "XOR": wx.Bitmap('GUI/Gates/XOR.png'),
            "SWITCH": wx.Bitmap('GUI/Gates/SWITCH.png'),
            "CLOCK": wx.Bitmap('GUI/Gates/CLOCK.png'),
            "DTYPE": wx.Bitmap('GUI/Gates/DTYPE.png'),
            "AND": wx.Bitmap('GUI/Gates/AND.png'),
            "NAND": wx.Bitmap('GUI/Gates/NAND.png'),
            "NOT": wx.Bitmap('GUI/Gates/NOT.png'),
            "NOR": wx.Bitmap('GUI/Gates/NOR.png')
        }
        super().__init__(parent)
        self.SetBackgroundColour('white')

        self.devices = devices
        self.network = network
        self.names = names

        self.device_size = (80, 40)
        self.input_range = (self.device_size[1]/4, 3 * self.device_size[1]/4)

        # w, h = self.GetClientSize()

        self.Buffer = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)

    def InitBuffer(self):
        size=self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer=wx.Bitmap(size.width,size.height)
        dc=wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.drawShapes(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.drawShapes(dc)

    def onKey(self, event): 
        keycode = event.GetKeyCode() 

        if keycode == wx.WXK_LEFT: 
            print('You pressed left arrow!')
        elif keycode == wx.WXK_RIGHT: 
            print('You pressed right arrow!')
        elif keycode == wx.WXK_UP: 
            print('You pressed up arrow!')
        elif keycode == wx.WXK_DOWN: 
            print('You pressed down arrow!')
        event.Skip() 

    def onMouse(self, event): 
        eventobj =  event.GetEventObject()

        obj = None
        for device in self.devices.devices_list:
            if device.image == eventobj:
                obj = device

        if obj is None:
            print("oops, can't find obj")
        else:
            print(self.names.get_name_string(obj.device_id))
        obj.location[0] += 10
        # print(obj.location)
        # self.InitBuffer()
        event.Skip()


    def drawShapes(self, dc):

        dc.SetPen(wx.Pen("black", 2))
        dc.Clear()
        for i, device in enumerate(self.devices.devices_list):
            device_type = self.names.get_name_string(device.device_kind)

            if hasattr(device, 'location'):
                device.image.SetPosition((device.location[0], device.location[1]))
            else:
                x, y = random.randint(0, 400), i*50
                device.location = [x, y]

                if device.device_kind in [self.devices.CLOCK, self.devices.D_TYPE]:
                    bitmap = scale_bitmap(
                        self.icons[device_type], self.device_size[0], self.device_size[0])
                else:
                    bitmap = scale_bitmap(
                        self.icons[device_type], self.device_size[0], self.device_size[1])
            
                device.image = wx.StaticBitmap(self, -1, bitmap)
                device.image.SetPosition((x, y))
                device.image.Bind(wx.EVT_LEFT_DOWN, self.onMouse)

        for device in self.devices.devices_list:        # device with inputs
            num_inputs = len(device.inputs)

            for input_ in device.inputs:
                try:
                    input_num = int(self.names.get_name_string(input_)[1:])
                except ValueError:              # must be a DTYPE - deal with that here
                    continue

                try:
                    fract = (input_num-1) / (num_inputs-1)
                except ZeroDivisionError:
                    fract = 0.5             # only 1 input

                out = self.network.get_connected_output(
                    device.device_id, input_)
                if out[1] is None:
                    new_device = self.devices.get_device(
                        out[0])    # get output device

                    dc.DrawLine(device.location[0]+5, device.location[1] + self.input_range[0] + fract*(self.input_range[1] - self.input_range[0]), new_device.location[0] +
                                self.device_size[0]-5, new_device.location[1] + self.device_size[1]/2)




class Gui(wx.Frame):        # main options screen

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title)

        self.SetIcon(wx.Icon('GUI/CUED Software.png'))
        # Canvas for drawing signals
        self.Maximize(True)

        self.SetBackgroundColour((186, 211, 255))
        self.header_font = wx.Font(
            25, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False)
        self.label_font = wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.NORMAL, False)

        self.makeLeftSizer()
        self.makeMiddleSizer()
        self.makeRightSizer()

        outer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.left_panel, 3, wx.ALL | wx.EXPAND, 20)
        self.main_sizer.Add(self.middle_panel, 3, wx.ALL | wx.EXPAND, 20)
        self.main_sizer.Add(self.right_panel, 3, wx.ALL | wx.EXPAND, 20)

        
        helpBtn = wx.Button(self, wx.ID_ANY, "Help")
        helpBtn.Bind(wx.EVT_BUTTON, self.open_help)
        outer.Add(helpBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        outer.Add(self.main_sizer, 0, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(outer)

    def makeLeftSizer(self):
        self.left_panel = wx.Panel(self)
        self.left_panel.SetBackgroundColour((37, 103, 209))
        self.load_btn = wx.Button(self.left_panel, wx.ID_ANY, "Browse Files")
        self.check_btn = wx.Button(self.left_panel, wx.ID_ANY, 'Verify Code')

        left_heading = wx.StaticText(self.left_panel, -1, label="Editor")
        left_heading = self.style(left_heading, self.header_font)

        editor_font = wx.Font(14, wx.MODERN, wx.NORMAL,
                              wx.NORMAL, False, u'Consolas')
        self.input_text = wx.stc.StyledTextCtrl(
            self.left_panel, size=(-1, wx.ALL))
        self.input_text.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.input_text.SetMarginWidth(3, 15)
        self.input_text.SetUseHorizontalScrollBar(False)
        self.input_text.StyleSetFont(0, editor_font)
        self.input_text.AppendText("DEVICES {\n\n}\nCONNECTIONS {\n\n}")

        self.error_text = wx.TextCtrl(self.left_panel, wx.ID_ANY, size=(
            -1, wx.ALL), style=wx.TE_MULTILINE | wx.TE_READONLY, value="Click run to check for errors")
        self.error_text.SetFont(editor_font)
        self.error_text.SetStyle(0, -1, wx.TextAttr(wx.RED))

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)

        self.left_sizer.Add(left_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.load_btn, 1, wx.ALIGN_LEFT, 5)
        row.Add(self.check_btn, 1, wx.ALIGN_RIGHT, 5)
        self.left_sizer.Add(row, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.left_sizer.Add(self.input_text, 6, wx.EXPAND | wx.ALL, 10)
        self.left_sizer.Add(self.error_text, 1, wx.EXPAND | wx.ALL, 10)

        self.left_panel.SetSizer(self.left_sizer)

        self.load_btn.Bind(wx.EVT_BUTTON, self.LoadFile)
        self.check_btn.Bind(wx.EVT_BUTTON, self.CheckText)

    def makeMiddleSizer(self):
        self.middle_panel = wx.lib.scrolledpanel.ScrolledPanel(self)
        self.middle_panel.SetBackgroundColour((37, 103, 209))
        self.middle_panel.SetupScrolling(scroll_x=False)

        self.middle_sizer = wx.BoxSizer(wx.VERTICAL)
        self.middle_panel.SetSizer(self.middle_sizer)

        self.middle_panel.Hide()
        self.Layout()

    def makeRightSizer(self):
        self.right_panel = wx.Panel(self)
        self.right_panel.SetBackgroundColour((37, 103, 209))
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetSizer(self.right_sizer)

        right_heading = wx.StaticText(self.right_panel, -1, label="Output")
        right_heading.SetFont(self.header_font)
        right_heading.SetForegroundColour((255, 255, 255))
        self.right_sizer.Add(right_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.right_panel.Hide()
        self.Layout()

    def CheckText(self, event):
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.scanner = Scanner(self.input_text.GetValue(), self.names, True)
        self.parser = Parser(self.names, self.devices,
                             self.network, self.monitors, self.scanner)
        status = None
        try:
            status = self.parser.parse_network()
        except:
            pass
        print(self.parser.parse_network())

        if self.scanner.total_error_string == "":
            self.error_text.AppendText("No errors found")
        else:
            self.error_text.Clear()
            self.error_text.AppendText(self.scanner.total_error_string)
            self.error_text.SetStyle(0, -1, wx.TextAttr(wx.RED))

            self.middle_panel.Hide()
            self.right_panel.Hide()
            self.Layout()
            return

        if status == True and len(self.devices.devices_list) > 0:

            self.error_text.Clear()
            self.middle_sizer.Clear(True)
            self.middle_panel.Update()
            try:
                self.right_sizer.Remove(1)
            except:
                pass
            self.right_panel.Update()

            middle_heading = wx.StaticText(self.middle_panel, label="Options")
            middle_heading = self.style(middle_heading, self.header_font)
            self.middle_sizer.Add(
                middle_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)

            self.toggle_right_panel = wx.ToggleButton(
                self.middle_panel, label="show circuit (experimental)")
            self.toggle_right_panel.Bind(
                wx.EVT_TOGGLEBUTTON, self.OnRightPanelToggle)
            self.middle_sizer.Add(self.toggle_right_panel,
                                  0, wx.ALL | wx.ALIGN_RIGHT, 5)

            device_info = wx.FlexGridSizer(4, 0, 10)
            # ------------- HEADINGS ------------- #
            label = wx.StaticText(self.middle_panel, label="Name")
            label = self.style(label, self.label_font)
            device_info.Add(label, 0,
                            wx.EXPAND | wx.ALL, 0)

            label = wx.StaticText(self.middle_panel, label="Type")
            label = self.style(label, self.label_font)
            device_info.Add(label, 0,
                            wx.EXPAND | wx.ALL, 0)

            label = wx.StaticText(self.middle_panel, label="Inputs")
            label = self.style(label, self.label_font)
            device_info.Add(label, 0,
                            wx.EXPAND | wx.ALL, 0)

            label = wx.StaticText(self.middle_panel, label="Outputs")
            label = self.style(label, self.label_font)
            device_info.Add(label, 0,
                            wx.EXPAND | wx.ALL, 0)

            # ---------------- TABLE --------------- #
            for device in self.devices.devices_list:

                name = self.devices.names.get_name_string(device.device_id)

                # DEVICE NAME
                label = wx.StaticText(
                    self.middle_panel, label=self.devices.names.get_name_string(device.device_id))
                label = self.style(label, self.label_font)
                device_info.Add(label, 0,
                                wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                # DEVICE TYPE
                label = wx.StaticText(
                    self.middle_panel, label=self.devices.names.get_name_string(device.device_kind))
                label = self.style(label, self.label_font)
                device_info.Add(label, 0,
                                wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                # INPUT NAMES
                s = ""
                for i in device.inputs:
                    s = s + '{}.{}\n'.format(name,
                                             self.names.get_name_string(i))
                s = s[:-1]

                label = wx.StaticText(self.middle_panel, label=s)
                label = self.style(label, self.label_font)
                device_info.Add(label, 0,
                                wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
                # MONITOR OPTIONS
                # TODO: make them do somwthing
                if device.device_kind == self.devices.D_TYPE:
                    device.monitor_btn = wx.ToggleButton(
                        self.middle_panel, label="monitor {}.Q".format(name))
                    device.monitor_btn_bar = wx.ToggleButton(
                        self.middle_panel, label="monitor {}.QBAR".format(name))
                    device.monitor_btn.Bind(
                        wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                    device.monitor_btn.SetForegroundColour('white')
                    device.monitor_btn_bar.Bind(
                        wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                    device.monitor_btn_bar.SetForegroundColour('white')
                    row = wx.BoxSizer(wx.VERTICAL)
                    row.Add(device.monitor_btn, 1,
                            wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 5)
                    row.Add(device.monitor_btn_bar, 1,
                            wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 5)

                    if name+'.Q' in self.monitors.get_signal_names()[0]:
                        device.monitor_btn.SetValue(True)
                        device.monitor_btn.SetBackgroundColour('#3ac10d')
                    else:
                        device.monitor_btn.SetBackgroundColour('#e0473a')

                    if name+'.QBAR' in self.monitors.get_signal_names()[0]:
                        device.monitor_btn_bar.SetValue(True)
                        device.monitor_btn_bar.SetBackgroundColour('#3ac10d')
                    else:
                        device.monitor_btn_bar.SetBackgroundColour('#e0473a')

                    device_info.Add(row, 1,
                                    wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 5)
                else:
                    device.monitor_btn = wx.ToggleButton(
                        self.middle_panel, label="monitor {}".format(name))
                    device.monitor_btn.Bind(
                        wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                    device.monitor_btn.SetForegroundColour('white')

                    if name in self.monitors.get_signal_names()[0]:
                        device.monitor_btn.SetValue(True)
                        device.monitor_btn.SetBackgroundColour('#3ac10d')
                    else:
                        device.monitor_btn.SetBackgroundColour('#e0473a')

                    device_info.Add(device.monitor_btn, 1,
                                    wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL, 5)

            # ----------- SET INITIAL SWITCH STATES ------------ #
            self.switch_options = wx.FlexGridSizer(2, 0, 30)
            for device in self.devices.devices_list:
                if device.device_kind != self.devices.SWITCH:
                    continue
                name = self.devices.names.get_name_string(device.device_id)

                label = wx.StaticText(self.middle_panel, 1, label=name)
                label = self.style(label, self.label_font)
                self.switch_options.Add(label, 1,
                                        wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                device.switch_btn = wx.ToggleButton(
                    self.middle_panel, label="initial switch state")
                device.switch_btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                device.switch_btn.SetForegroundColour('white')
                if device.switch_state:
                    device.switch_btn.SetValue(True)
                    device.switch_btn.SetBackgroundColour('#3ac10d')
                else:
                    device.switch_btn.SetBackgroundColour('#e0473a')

                self.switch_options.Add(device.switch_btn, 1,
                                        wx.ALL, 5)

            self.middle_sizer.Insert(1, self.switch_options, 0,
                                     wx.ALL | wx.ALIGN_CENTER, 30)
            self.middle_sizer.Insert(1, wx.StaticLine(
                self.middle_panel), 0, wx.EXPAND, 5)

            self.middle_sizer.Insert(1, device_info, 0,
                                     wx.ALL | wx.ALIGN_CENTER, 30)

            simulate_btn = wx.Button(self.middle_panel, label="Simulate!")
            simulate_btn.Bind(wx.EVT_BUTTON, self.newSimulate)

        # self.middle_sizer.Add(simulate_btn, 0,
        #                         wx.ALL | wx.EXPAND, 30)
        self.middle_panel.Show()
        self.SimulateWindow = SimulatePage(self)

        self.canvas = CircuitDiagram(
            self.right_panel, self.devices, self.network, self.names)
        self.right_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

        self.Layout()

    def newSimulate(self, event):
        self.SimulateWindow.Show()

    def OnRightPanelToggle(self, event):
        obj = event.GetEventObject()
        if obj.GetValue():
            self.right_panel.Show()
        else:
            self.right_panel.Hide()
        self.Layout()

    def OnToggleClick(self, event):
        obj = event.GetEventObject()
        if obj.GetValue():
            obj.SetBackgroundColour('#3ac10d')
        else:
            obj.SetBackgroundColour('#e0473a')

    def style(self, obj, font, fgcolour='white', bgcolour=None):
        obj.SetForegroundColour(fgcolour)
        obj.SetBackgroundColour(bgcolour)
        obj.SetFont(font)
        return obj

    def LoadFile(self, event):

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open file", wildcard="TXT files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            fileDialog.SetSize((120, 80))

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as f:
                    self.input_text.ClearAll()
                    self.input_text.AppendText(f.read())
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)
    
    def open_help(self, event):
        filepath = 'GUI/helpfile.pdf'
        import subprocess, os, platform

        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
        event.Skip()


class SimulatePage(wx.Frame):       # simulation screen

    def __init__(self, parent):
        """Initialise widgets and layout."""
        super().__init__(parent=parent, title="Simulation")

        self.SetIcon(wx.Icon('GUI/CUED Software.png'))
        self.Maximize(True)
        self.SetBackgroundColour((186, 211, 255))

        # Canvas for drawing signals
        self.canvas = Canvas(self, parent.devices, parent.monitors, parent.network)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)
        
        self.tostart = wx.Button(self, wx.ID_ANY, "START")
        self.back5 = wx.Button(self, wx.ID_ANY, "Step -5")
        self.back1 = wx.Button(self, wx.ID_ANY, "Step -1")
        play_pause = wx.Bitmap('GUI/Glyphicons/playpause.png')
        play_pause = scale_bitmap(play_pause, 20, 20)
        self.pause = wx.BitmapToggleButton(self, wx.ID_ANY, play_pause)
        self.fwd1 = wx.Button(self, wx.ID_ANY, "Step +1")
        self.fwd5 = wx.Button(self, wx.ID_ANY, "Step +5")
        self.toend = wx.Button(self, wx.ID_ANY, "END")


        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = wx.GridSizer(9)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(left_sizer, 5, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(right_sizer, 1, wx.ALL|wx.EXPAND, 5)

        left_sizer.Add(self.canvas, 100, wx.ALL|wx.EXPAND,0)
        left_sizer.Add(toolbar, 0, wx.ALL|wx.EXPAND, 5)

        toolbar.Add(self.tostart, 1, wx.ALL|wx.ALIGN_LEFT, 5)
        toolbar.AddSpacer(70)
        toolbar.Add(self.back5, 1, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 5)
        toolbar.Add(self.back1, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        toolbar.Add(self.pause, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        toolbar.Add(self.fwd1, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 5)
        toolbar.Add(self.fwd5, 1, wx.ALL|wx.EXPAND|wx.ALIGN_LEFT, 5)
        toolbar.AddSpacer(70)
        toolbar.Add(self.toend, 0, wx.ALL|wx.ALIGN_RIGHT, 5)

        helpBtn = wx.Button(self, wx.ID_ANY, "Help")
        helpBtn.Bind(wx.EVT_BUTTON, self.open_help)
        right_sizer.Add(helpBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 0)

        right_sizer.Add(self.text, 1, wx.TOP, 10)
        right_sizer.Add(self.spin, 1, wx.ALL, 5)
        right_sizer.Add(self.run_button, 1, wx.ALL, 5)
        right_sizer.Add(self.text_box, 1, wx.ALL, 5)

        # speed slider
        # change each switch
        # help button

        self.SetSizerAndFit(main_sizer)
    
    def open_help(self, event):
        filepath = 'GUI/helpfile.pdf'
        import subprocess, os, platform

        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
        event.Skip()