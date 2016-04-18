import wx
import threading
import random
from wx.lib.pubsub import pub
import math

BLOCK = 4

def next_line(size=360, block=BLOCK):
    chance = .05
    moving = 0
    right = False

    # convert to block size
    size = size/block

    # block size constants
    side = 0
    diameter = 16

    i = int(size/4) - 8 #random.randint(side, size/2-side-diameter)

    while 1:
        if random.random() < chance:
            if (random.random() < .5 or 2 * diameter > i - side) and 2 * diameter <= size - i - side:
                # right
                width = random.randint(2 * diameter, size - i - side)
                a = i
                b = i + width
                for _ in range(diameter):
                    yield a*block, b*block

                i = i + width - diameter

            else:
                # left
                width = random.randint(2 * diameter, i - side)

                i = i - width + diameter

                a = i
                b = i + width
                for _ in range(diameter):
                    yield a*block, b*block

        else:
            # forward
            a = i
            b = i + diameter

            yield a*block, b*block

class View(wx.Panel):
    def __init__(self, parent):
        super(View, self).__init__(parent)
        self.SetBackgroundColour((255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.x_offset = 0
        self.score = 0
        self.lines = []

        self.line_generator = next_line(size=720)

        w, h = parent.GetClientSize()
        for _ in range(int(h/BLOCK)):
            self.lines.append((int(w/2)-32, int(w/2)+32))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key)

        self.parent = parent

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetClientSize()

        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        num_lines = int(h / BLOCK)

        self.lines = self.lines[-num_lines:]

        for i, (a, b) in enumerate(self.lines[::-1]):
            dc.SetBrush(wx.Brush("black", wx.SOLID))
            dc.DrawRectangle((0, BLOCK*i, a-self.x_offset, BLOCK))
            dc.DrawRectangle((b-self.x_offset, BLOCK*i, w-(b-self.x_offset), BLOCK))
        
        dc.SetPen(wx.Pen("green"))
        dc.SetBrush(wx.Brush("green", wx.SOLID))

        dc.DrawCircle(int(w/2), int(h*2/3), 10)

        self.score += 0.01

        dc.SetTextForeground('green')
        dc.SetFont(wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText(str(int(self.score)), 20, 20)

        if not self.x_bound_check():
            self.pause()

            self.Unbind(wx.EVT_KEY_DOWN)

    def add_line(self, event=None):
        w, h = self.GetClientSize()
        self.lines.append(next(self.line_generator))

        self.Refresh()

    def on_key(self, event):
        if event.GetKeyCode() ==  87:
            self.up()
        elif event.GetKeyCode() == 65:
            self.left()
        elif event.GetKeyCode() == 68:
            self.right()
        elif event.GetKeyCode() == 83:
            self.pause()

    def up(self):
        self.Bind(wx.EVT_TIMER, self.add_line, self.timer)
        self.timer.Start(10)

    def right(self):
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.inc_offset, self.timer)
        self.timer.Start(10)

    def left(self):
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.dec_offset, self.timer)
        self.timer.Start(10)

    def pause(self):
        self.timer.Stop()

    def inc_offset(self, event):
        self.x_offset += BLOCK
        self.Refresh()

        self.score += 0.01

    def dec_offset(self, event):
        self.x_offset -= BLOCK
        self.Refresh()

        self.score += 0.01

    def x_bound_check(self):
        w, h = self.GetClientSize()
        num_lines = int(h / BLOCK)

        y1, y2 = int(h * 2/3) - 10, int(h * 2/3) + 10

        for i in range(int(y1/BLOCK)+1, int(y2/BLOCK)+1):
            x1, x2 = int(w/2) - 10, int(w/2) + 10
            a, b = self.lines[-num_lines:][-i]

            a -= self.x_offset
            b -= self.x_offset

            if x1 < a or x2 > b:
                return False
                
        return True


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetClientSize(360, 640) 
        self.Center()

        self.view = View(self)   

def main():
    app = wx.App()

    frame = Frame()
    frame.Show()

    app.MainLoop()

try:
    main()
except:
    import traceback
    traceback.print_exc()
    input('')