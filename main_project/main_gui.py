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

# from simulator import Canvas
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
        self.SetOwnBackgroundColour('white')

        self.devices = devices
        self.network = network
        self.names = names

        self.device_size = (80, 40)
        self.input_range = (self.device_size[1]/4, 3 * self.device_size[1]/4)
        self.dtype_posns = {
            "CLK": (5, self.device_size[0]*2/3),
            "DATA": (5, self.device_size[0]/3),
            "SET": (self.device_size[0]/2, 5),
            "CLEAR": (self.device_size[0]/2, self.device_size[0]-5),
            "Q": (self.device_size[0] - 5, self.device_size[0]/3),
            "QBAR": (self.device_size[0] - 5, self.device_size[0]*2/3)
        }

        self.Buffer = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)

    def InitBuffer(self):
        size = self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer = wx.Bitmap(size.width, size.height)
        dc = wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        dc.Clear()
        self.drawShapes(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def OnEraseBack(self, event):
        pass  # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh()  # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.drawShapes(dc)

    def drawShapes(self, dc):

        dc.SetPen(wx.Pen("black", 2))
        dc.Clear()
        # --------- DRAW BITMAPS --------- #
        tmp = self.devices.devices_list
        random.shuffle(tmp)
        for i, device in enumerate(tmp):
            device_type = self.names.get_name_string(device.device_kind)

            if hasattr(device, 'location'):
                device.image.SetPosition(
                    (device.location[0], device.location[1]))
            else:
                if device_type in ['SWITCH', 'CLOCK']:
                    x, y = 50, i*50
                else:
                    x, y = random.randint(150, 400), i*50
                device.location = [x, y]

                if device.device_kind == self.devices.D_TYPE:
                    bitmap = scale_bitmap(
                        self.icons[device_type], self.device_size[0], self.device_size[0])
                elif device.device_kind == self.devices.CLOCK:
                    bitmap = scale_bitmap(
                        self.icons[device_type], self.device_size[1], self.device_size[1])
                else:
                    bitmap = scale_bitmap(
                        self.icons[device_type], self.device_size[0], self.device_size[1])

                device.image = wx.StaticBitmap(self, -1, bitmap)
                device.image.SetPosition((x, y))

        # ----------- DRAW LINES ----------- #
        for device in self.devices.devices_list:        # device with inputs
            num_inputs = len(device.inputs)

            for input_ in device.inputs:
                if device.device_kind == self.devices.D_TYPE:
                    (xo, yo) = self.dtype_posns[self.names.get_name_string(
                        input_)]
                # elif device.device_kind == self.devices.CLOCK:
                #     (xo, yo) = (self.device_size[0], self.device_size[0]/2)
                else:
                    input_num = int(self.names.get_name_string(input_)[1:])
                    try:
                        fract = (input_num-1) / (num_inputs-1)
                    except ZeroDivisionError:
                        fract = 0.5             # only 1 input
                    (xo, yo) = (
                        5, self.input_range[0]+fract*(self.input_range[1]-self.input_range[0]))

                out = self.network.get_connected_output(
                    device.device_id, input_)
                new_device = self.devices.get_device(
                    out[0])
                if out[1] is None:
                    if new_device.device_kind == self.devices.CLOCK:
                        dc.DrawLine(device.location[0]+xo, device.location[1] + yo, new_device.location[0] +
                                self.device_size[1]-5, new_device.location[1] + self.device_size[1]/2)
                    else:
                        dc.DrawLine(device.location[0]+xo, device.location[1] + yo, new_device.location[0] +
                                self.device_size[0]-5, new_device.location[1] + self.device_size[1]/2)
                else:  # it's a dtype output
                    (x1, y1) = self.dtype_posns[self.names.get_name_string(
                        out[1])]
                    dc.DrawLine(device.location[0]+xo, device.location[1] + yo, new_device.location[0] +
                                x1, new_device.location[1] + y1)

class Gui(wx.Frame):        # main options screen

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title)

        self.SetIcon(wx.Icon('GUI/CUED Software.png'))
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
        outer.Add(helpBtn, 0, wx.ALL | wx.ALIGN_RIGHT, 0)
        outer.Add(self.main_sizer, 0, wx.EXPAND | wx.ALL, 0)
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
        self.right_panel.SetBackgroundColour('white')
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetSizer(self.right_sizer)

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
        # try:
        status = self.parser.parse_network()
        # except:
        #     pass

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

            self.middle_sizer.Add(simulate_btn, 0,
                                wx.ALL | wx.EXPAND, 30)

        self.middle_panel.Show()
        self.SimulateWindow = SimulatePage(self)


        self.canvas = CircuitDiagram(
            self.right_panel, self.devices, self.network, self.names)
        self.right_sizer.Clear()
        self.right_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

        self.Layout()

    def newSimulate(self, event):
        self.SimulateWindow.Show()

        self.monitors.reset_monitors()

        for device in self.devices.devices_list:
            if hasattr(device, 'monitor_btn'):
                if device.monitor_btn.GetValue():
                    if device.device_kind == self.devices.D_TYPE:
                        self.monitors.make_monitor(device.device_id,self.names.query("Q"))
                    else:
                        self.monitors.make_monitor(device.device_id,None)

            if hasattr(device, 'monitor_btn_bar'):
                if device.monitor_btn_bar.GetValue():
                    self.monitors.make_monitor(device.device_id,self.names.query("QBAR"))
            
            if hasattr(device, 'switch_btn'):
                if device.switch_btn.GetValue():
                    self.devices.set_switch(device.device_id, self.devices.HIGH)
                else:
                    self.devices.set_switch(device.device_id, self.devices.LOW)
        
        self.SimulateWindow.run(5)

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
        import subprocess
        import os
        import platform

        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            filepath = filepath.replace('/','\\')
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
        self.parent = parent

        # Canvas for drawing signals
        self.canvas = Canvas(self, parent.devices,
                             parent.monitors, parent.network)
        
        # Configure the widgets
        self.tostart = wx.Button(self, wx.ID_ANY, "GOTO START")
        self.tostart.name = 'start'
        self.tostart.Bind(wx.EVT_BUTTON, self.on_btn, self.tostart)
        self.back5 = wx.Button(self, wx.ID_ANY, "Step -5")
        self.back1 = wx.Button(self, wx.ID_ANY, "Step -1")
        play_pause = wx.Bitmap('GUI/Glyphicons/playpause.png')
        play_pause = scale_bitmap(play_pause, 25, 25)
        self.pause = wx.BitmapToggleButton(self, wx.ID_ANY, play_pause)
        self.fwd1 = wx.Button(self, wx.ID_ANY, "Step +1")
        self.fwd5 = wx.Button(self, wx.ID_ANY, "Step +5")
        self.toend = wx.Button(self, wx.ID_ANY, "GOTO END")
        self.toend.name = 'end'
        self.toend.Bind(wx.EVT_BUTTON, self.on_btn, self.toend)

        self.reset = wx.Button(self, wx.ID_ANY, "Reset Scene")
        self.reset.name = 'reset'
        self.reset.Bind(wx.EVT_BUTTON, self.on_btn, self.reset)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = wx.GridSizer(9)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(left_sizer, 5, wx.ALL | wx.EXPAND, 0)
        main_sizer.Add(right_sizer, 1, wx.ALL | wx.EXPAND, 5)

        left_sizer.Add(self.canvas, 100, wx.ALL | wx.EXPAND, 0)
        left_sizer.Add(toolbar, 0, wx.ALL | wx.EXPAND, 5)

        toolbar.Add(self.tostart, 1, wx.ALL | wx.ALIGN_LEFT|wx.EXPAND, 5)
        toolbar.AddSpacer(70)
        toolbar.Add(self.back5, 1, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT, 5)
        toolbar.Add(self.back1, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 5)
        toolbar.Add(self.pause, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 5)
        toolbar.Add(self.fwd1, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 5)
        toolbar.Add(self.fwd5, 1, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, 5)
        toolbar.AddSpacer(70)
        toolbar.Add(self.toend, 0, wx.ALL | wx.ALIGN_RIGHT|wx.EXPAND, 5)

        helpBtn = wx.Button(self, wx.ID_ANY, "Help")
        helpBtn.Bind(wx.EVT_BUTTON, self.open_help)
        right_sizer.Add(helpBtn, 0, wx.ALL | wx.ALIGN_RIGHT, 0)

        self.speedSizer = wx.Slider(self, value=30, minValue=5, maxValue=60)
        right_sizer.Add(self.speedSizer, 0, wx.ALL|wx.GROW, 10)

        row = wx.BoxSizer(wx.HORIZONTAL)
        self.continueSpin = wx.SpinCtrl(self, wx.ID_ANY, "5")
        self.continueBtn = wx.Button(self, wx.ID_ANY, "Continue")
        self.continueBtn.name = "continue"
        self.continueBtn.Bind(wx.EVT_BUTTON, self.on_btn, self.continueBtn)

        right_sizer.AddSpacer(30)
        row.Add(self.continueSpin, 0, wx.ALL, 10)
        right_sizer.AddSpacer(30)
        row.Add(self.continueBtn, 0, wx.ALL, 10)
        right_sizer.Add(row, 0, wx.EXPAND, 10)
        right_sizer.AddSpacer(30)

        for device in self.parent.devices.devices_list:
            if device.device_kind == self.parent.devices.SWITCH:
                row = wx.BoxSizer(wx.HORIZONTAL)
                device.switch_btn = wx.ToggleButton(self, label="On/Off")
                device.switch_btn.name = 'switch '+str(device.device_id)
                device.switch_btn.Bind(wx.EVT_TOGGLEBUTTON, self.on_btn, device.switch_btn)

                row.Add(wx.StaticText(self, 0, label=self.parent.names.get_name_string(device.device_id)), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
                row.AddSpacer(30)
                row.Add(device.switch_btn, 0, wx.ALL | wx.EXPAND)

                right_sizer.Add(row, 0, wx.ALIGN_CENTER)
        
        right_sizer.AddSpacer(30)
        right_sizer.Add(self.reset, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.BOTTOM, 5)
        self.SetSizerAndFit(main_sizer)

        

    def on_btn(self, event):
        obj = event.GetEventObject()
        name = obj.name

        if name == 'start':
            self.canvas.pan_x = 0
            self.canvas.init = False
            self.canvas.Refresh()

        elif name == 'end':
            self.canvas.pan_x = -self.canvas.max_x-100 + self.canvas.size.width
            self.canvas.init = False
            self.canvas.Refresh()

        elif name == 'continue':
            self.run(int(self.continueSpin.GetValue()))
            if self.canvas.max_x > self.canvas.size.width:
                self.canvas.pan_x = -self.canvas.max_x-100 + self.canvas.size.width
                self.canvas.init = False
                self.canvas.Refresh()

        elif name == 'reset':
            self.parent.monitors.reset_monitors()
            self.canvas.signals = []
            self.canvas.init = False
            self.canvas.Refresh()

        elif name.split(' ')[0] == 'switch':
            if obj.GetValue():
                self.parent.devices.set_switch(int(name.split(' ')[-1]), 1)
            else:
                self.parent.devices.set_switch(int(name.split(' ')[-1]), 0)
        


    def run(self, num, reset=False):
        if reset:
            self.parent.monitors.reset_monitors()
        
        for _ in range(num):
            if self.parent.network.execute_network():
                self.parent.monitors.record_signals()
            else:
                print("Error! Network oscillating.")

        self.canvas.signals = []

        count = 0
        for (device_id, output_id), value in self.parent.monitors.monitors_dictionary.items():
            monitor_name = self.parent.devices.get_signal_name(device_id, output_id)
            self.canvas.signals.append([monitor_name, value])
            count += 1
        self.canvas.render()

    def open_help(self, event):
        filepath = 'GUI/helpfile.pdf'
        import subprocess
        import os
        import platform

        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            filepath = filepath.replace('/','\\')
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))
        event.Skip()
