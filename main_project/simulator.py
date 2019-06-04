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
from OpenGL import GL, GLU, GLUT
import time
import numpy as np
import math

from main_project.names import Names
from main_project.userint import UserInterface


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
        super().__init__(parent.canvas_panel, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.parent = parent
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        self.play = False

        self.scale_x = 50
        self.scale_y = 50

        self.size = self.GetClientSize()
        self.max_x = self.size.width

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
            for i in range(0, len(self.signals[0][-1])):
                GL.glColor3f(0, 0, 0)
                self.render_text(str(i), 100 + i*self.scale_x,
                                 self.size.height - 30)
                GL.glColor3f(0.8, 0.8, 0.8)
                GL.glLineWidth(1.0)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(100 + i*self.scale_x, self.size.height - 40)
                GL.glVertex2f(100 + i*self.scale_x, 0)
                GL.glEnd()

            # signal
            count = 1
            for sig in self.signals:
                GL.glColor3f(sig[1][0], sig[1][1], sig[1][2])
                GL.glLineWidth(3.0)
                self.draw_signal(
                    sig[-1], (100, self.size.height - count*2*self.scale_y))

                GL.glClearColor(1.0, 1.0, 1.0, 0.0)
                self.render_text(
                    sig[0], 50, self.size.height - count*2*self.scale_y)
                count += 1

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

            self.parent.canvas3d.pan_x -= 20 * event.GetWheelRotation() / event.GetWheelDelta()
            if self.parent.canvas3d.pan_x > 0:
                self.parent.canvas3d.pan_x = 0
            self.parent.canvas3d.init = False
            self.parent.canvas3d.Refresh()

        if event.GetWheelRotation() > 0:
            self.pan_x -= 20 * event.GetWheelRotation() / event.GetWheelDelta()
            if self.pan_x < -self.max_x-100 + self.size.width:
                self.pan_x = -self.max_x-100 + self.size.width
            self.init = False

            self.parent.canvas3d.pan_x -= 20 * event.GetWheelRotation() / event.GetWheelDelta()
            if self.parent.canvas3d.pan_x < -self.parent.canvas3d.max_x-100 + self.parent.canvas3d.size.width/3:
                self.parent.canvas3d.pan_x = -self.parent.canvas3d.max_x - \
                    100 + self.parent.canvas3d.size.width/3
            self.parent.canvas3d.init = False
            self.parent.canvas3d.Refresh()

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

    def draw_signal(self, signal, offset):
        self.max_x = self.scale_x * (len(signal)-1)

        GL.glBegin(GL.GL_LINE_STRIP)
        for i, val in enumerate(signal):
            if val == 1:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1])
            else:
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1]+self.scale_y)

            try:
                next_val = (1-signal[i+1]) * self.scale_y
                GL.glVertex2f(offset[0]+i*self.scale_x, offset[1] + next_val)
            except IndexError:
                pass

        GL.glEnd()
        return


class Canvas3D(wxcanvas.GLCanvas):
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

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent, devices, monitors, network):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent.canvas3d_panel, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.parent = parent

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        self.scale_x = 50
        self.scale_y = 50
        self.scale_z = 30
        self.signals = []

        self.max_x = 0
        self.size = self.GetClientSize()

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 800

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        self.size = self.GetClientSize()

        self.SetCurrent(self.context)

        GL.glViewport(0, 0, self.size.width, self.size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, self.size.width / self.size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)
        # GL.glTranslatef(, 0, 0)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, 0.0, 0.0)
        GL.glMultMatrixf(self.scene_rotate)

        GL.glTranslatef(-100.0, -10.0, self.pan_y)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if len(self.signals) > 0:
            # ruler
            GL.glColor3f(1.0, 1.0, 1.0)
            for i in range(0, len(self.signals[0][-1])):
                self.render_text(str(i), 100 + i*self.scale_x, 0, 0)

                GL.glBegin(GL.GL_LINES)
                GL.glVertex3f(100 + i*self.scale_x, 0, 10)
                GL.glVertex3f(100 + i*self.scale_x, 0, 1000)
                GL.glEnd()

            # signal
            count = 1
            for sig in self.signals:
                GL.glColor3f(sig[1][0], sig[1][1], sig[1][2])
                self.draw_signal(sig[-1], (100, 1.3*count*self.scale_z))
                self.render_text(sig[0], 50, 0, 1.3*count*self.scale_z)
                count += 1

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_signal(self, signal, offset):
        self.max_x = self.scale_x * (len(signal)-1)

        for i, val in enumerate(signal):
            if val == 1:
                self.draw_cuboid(
                    offset[0]+i*self.scale_x, offset[1], self.scale_x/2, self.scale_z/2, self.scale_y)
            else:
                self.draw_cuboid(
                    offset[0]+i*self.scale_x, offset[1], self.scale_x/2, self.scale_z/2, 0)
        return

    def draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y

            if event.LeftIsDown():
                GL.glRotatef(y, 1, 0, 0)
            if event.MiddleIsDown():
                self.pan_y += y

            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.pan_x -= 20*event.GetWheelRotation() / (event.GetWheelDelta())

            if self.pan_x > 0:
                self.pan_x = 0
            self.init = False

            self.parent.canvas.pan_x -= 20*event.GetWheelRotation() / (event.GetWheelDelta())
            if self.parent.canvas.pan_x > 0:
                self.parent.canvas.pan_x = 0
            self.parent.canvas.init = False
            self.parent.canvas.Refresh()

        if event.GetWheelRotation() > 0:
            self.pan_x -= 20*event.GetWheelRotation() / (event.GetWheelDelta())
            if self.pan_x < -self.parent.canvas3d.max_x-100 + self.parent.canvas3d.size.width/3:
                self.pan_x = -self.parent.canvas3d.max_x - \
                    100 + self.parent.canvas3d.size.width/3
            self.init = False

            self.parent.canvas.pan_x -= 20*event.GetWheelRotation() / (event.GetWheelDelta())
            if self.parent.canvas.pan_x < -self.parent.canvas.max_x-100 + self.parent.canvas.size.width:
                self.parent.canvas.pan_x = -self.parent.canvas.max_x - \
                    100 + self.parent.canvas.size.width
            self.parent.canvas.init = False
            self.parent.canvas.Refresh()

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)
