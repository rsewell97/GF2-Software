"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

# from names import Names
# from devices import Devices
# from network import Network
# from monitors import Monitors
# from scanner import Scanner
# from parse import Parser

class Controls:
    
    """
    define_max_time(self, t): sets the end time for the simulation

    reset_all(self): resets everything to initial states

    back_x(self, x): moves back x steps

    forward_x(self, x): moves forward x steps

    go_to_end(self): goes to end of program (max time) - default 50

    regular_running(self): runs visualisation

    pause_play(self): either plays or pauses the simulation
    
    set_speed(self, t): sets how long between things happening
    """
    
    def __init__(self, canvas, devices, monitor, network):
        # Initialise start time at 0
        self.time = 0
        self.max_time = 50

        # Make a global variable for whether system is paused or not
        self.paused = 0
        
        # Initialise speed of progression
        self.timing = 1

        # add all the other stuff

        self.devices = devices
        self.network = network
        self.monitors = monitor
        self.glc = canvas

    def define_max_time(self, t):
        self.max_time = t

    def reset_all(self): #resets everything to initial states
        self.glc.all_devices_x_coordinates.clear()
        self.glc.all_devices_y_coordinates.clear()

        self.glc.x_all_time = []
        self.glc.y_all_time = []

        self.time = 0

        list_of_dtypes = self.devices.find_devices(self.devices.D_TYPE)

        for id in list_of_dtypes:
            self.network.execute_d_type(id)

        return

    def back_x(self, x): #goes back x time intervals
        current_time = self.time
        self.reset_all()
        while self.time < (current_time - x):
            self.glc.run_system()

        self.glc.translate_and_draw()

        return self.regular_running()

    def forward_x(self, x): # goes forward x time intervals
        i = 0
        while i < x:
            self.glc.run_system()
            i += 1
        self.glc.translate_and_draw()
        return self.regular_running()

    def go_to_end(self):
        time_dif = self.max_time - self.time
        self.forward_x(time_dif)
        return

    def regular_running(self):
        while self.time < self.max_time:
            if self.paused > 0:
                self.glc.run_system()
                self.glc.translate_and_draw()
            time.sleep(self.timing)
        return self.regular_running()

    def pause_play(self):
        if self.paused == 0:
            self.paused = 1
        else:
            self.paused =  0
        return
    
    def set_speed(self, t):
        self.timing = t
        return


class Canvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    get_new_coordinates(self, device_id, notness=0) uses the signal from the device to create some new coordinates

    run_system(self): executes network, adds all new data

    translate_and_draw(self): draws everything
    """

    def __init__(self, parent, devices, monitors, network):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # add all the other stuff
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.controls = Controls(self, self.devices,self.monitors, self.network)

        self.symbol_type = None
        self.symbol_id = None
        self.error_counter = 0

        # Initialise sizes for signal drawing
        self.width = 10
        self.height = 10

        # Initialise two lists which will contain all x and y coordinates (untranslated) for all devices
        self.all_devices_x_coordinates = [[]]
        self.all_devices_y_coordinates = [[]]

        # Initialise two lists which contain above matrices for all time!
        self.x_all_time = []
        self.y_all_time = []

        # Initialise a list of all devices
        self.list_of_all_devices = self.devices.find_devices(self)
        self.num_devices = len(self.list_of_all_devices)

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def get_new_coordinates(self, device, notness=0): # notness used for DTYPES
        device = self.devices.get_device(device)
        output_port = device

        if device.device_kind == self.devices.D_TYPE:
            if notness == 1:
                output_port = "QBAR"
            elif notness == 0:
                output_port = "Q"
            else:
                print("there's a problem with the notness")

        signal = self.network.get_output_signal(self.devices.names.query(device), output_port)

        x = self.controls.time * self.width
        y = 0
        if signal:
            y = self.height

        return x, y # will all be on origin, will have to be translated

    def run_system(self): # get coordinates for all devices for a new time

        self.network.execute_network()
        self.controls.time += 1
        i = 0
        while i < self.num_devices:
            new_x, new_y = self.get_new_coordinates(self.list_of_all_devices[i])
            self.all_devices_x_coordinates[i].append(new_x)
            self.all_devices_y_coordinates[i].append(new_y)
            i += 1

        self.x_all_time.append(self.all_devices_x_coordinates)
        self.y_all_time.append(self.all_devices_y_coordinates)
        return

    def translate_and_draw(self): # moves y values of all monitored, returns lists of all x and y coordinates of monitored signals

        monitored_signals = self.monitors.monitors_dictionary.keys()
        monitored_signal_ids = []
        monitored_signal_names = []

        for signal in monitored_signals:
            monitored_signal_ids.append(signal[0])
            monitored_signal_names.append(self.devices.get_signal_name(signal[0], signal[1]))

        monitored_signal_names.sort(key=str.lower)
        i = 0
        all_x = []
        all_y = []
        for id in monitored_signal_ids:
            place_in_list = self.list_of_all_devices.index(id)
            y_coordinates = self.all_devices_y_coordinates[place_in_list]
            for coordinate in y_coordinates:
                coordinate += 500 # should be edited
                coordinate -= i * 50 # 50 CAN BE CHANGED
            i += 1
            x_coordinates = self.all_devices_x_coordinates[place_in_list]
            all_x.append(x_coordinates)
            all_y.append(y_coordinates)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        j = 0

        while j < len(monitored_signal_ids): # for each signal
            if j % 2 == 0: # set colours, red and blue alternating
                GL.glColor3f(0.0, 0.0, 1.0)
            else:
                GL.glColor3f(1.0, 0.0, 0.0)
            y = all_y[j][0] + (self.width / 2)
            self.render_text(monitored_signal_names[j], 0, y) # write signal name at beginning of signal trace
            k = 0
            while k < len(all_y[j]): # draw signal trace
                GL.glVertex2f(all_x[j][k], all_y[j][k])
                GL.glVertex2f(all_x[j][k + 1], all_y[j][k + 1])
                k += 1
            j += 1

        # draw a green line at the bottom to show time changed - it does nothing else
        relative_time = self.time / self.max_time
        GL.glColor3f(0.0, 1.0, 0.0)
        Y = 5
        BAR_END = relative_time * self.width * 15 # 15 is the number of traces shown on the screen
        GL.glVertex2f(0, Y)
        GL.glVertex2f(BAR_END, Y)

        GL.glEnd()

        return

