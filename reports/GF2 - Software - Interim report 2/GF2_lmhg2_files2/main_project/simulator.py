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
import time

from names import Names
from userint import UserInterface


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

        self.scale_x = 50
        self.scale_y = 50

        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.signals = []

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        self.size = self.GetClientSize()
        self.max_x = -self.size.width
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, self.size.width, self.size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, self.size.width, 0, self.size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        # GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text=""):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        
        if len(self.signals) > 0:
            # ruler
            for i in range(0, len(self.signals[0][1])):
                self.render_text(str(i), 100 + i*self.scale_x, self.size.height - 30)

            # signal
            count = 1
            for sig in self.signals:
                self.draw_signal(sig[1], (100,self.size.height - count*2*self.scale_y))
                self.render_text(sig[0], 50, self.size.height - count*2*self.scale_y)
                count += 1

        # self.auto_scroll()
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

        self.size = self.GetClientSize()
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""

        if event.ButtonDown():
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.pan_x -= 20 * event.GetWheelRotation() / event.GetWheelDelta()
            if self.pan_x > 0:
                self.pan_x = 0
            self.init = False
            
        if event.GetWheelRotation() > 0:
            self.pan_x -= 20 * event.GetWheelRotation() / event.GetWheelDelta()
            self.init = False

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

    def draw_signal(self, signal, offset,):
        self.max_x = self.scale_x *(len(signal)-1)

        GL.glBegin(GL.GL_LINE_STRIP)
        for i, val in enumerate(signal):
            if val == 1:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1]+self.scale_y)
            else:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1])

            try:
                next_val = signal[i+1] * self.scale_y
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1] + next_val)
            except IndexError:
                pass

        GL.glEnd()
        return
    
    # def loop(self):
    #     while True:
    #         self.pan_x += 2
    #         self.render()
    #         time.sleep(0.2)
    #         self.Refresh()
    #         print("move")
