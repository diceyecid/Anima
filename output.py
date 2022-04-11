import os
import wx
import wx.lib.statbmp as SB

from PIL import Image
from wx.lib.pubsub import pub 

PhotoMaxSize = 600



class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Anima', size = (1200, 800))

        direname = dirname = os.path.dirname(__file__)
        imgLoc = os.path.join(dirname, 'input/default.jpg')

        self.panel = wx.Panel(self.frame)
        self.panel.SetBackgroundColour(wx.Colour(233,243,255,255))

        self.createWidgets()
        self.frame.Show()

    def createWidgets(self):

        title = "Anima" 
        lbl = wx.StaticText(self.panel,-1,style = wx.ALIGN_CENTER) 
        font = wx.Font(48, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        subFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)  
        lbl.SetFont(font) 
        lbl.SetLabel(title) 

        
        dirname = os.path.dirname(__file__)
        self.imgLoc = os.path.join(dirname, 'input/default.jpg')
        self.img = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)

        self.slider = wx.Slider(self.panel, -1, 99, 1, 99, size = (self.img.GetWidth(), 40))
        self.Bind(wx.EVT_SLIDER, self.sliderUpdate)

        self.perc = 0.99

        self.w = self.img.GetWidth()
        self.h = self.img.GetHeight()

        imgBefore = self.img.Resize(size = (int(self.w * self.perc), self.h), pos = (0,0))
        self.before = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgBefore), pos = ((1200 - self.w)/2, 200))
        self.before.SetBitmap(wx.Bitmap(imgBefore))
        #self.before.SetPosition(100, 100)

        imgAfter = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)
        imgAfter = imgAfter.Mirror(horizontally=True)
        imgAfter = imgAfter.Resize(size = (int(self.w * (1 - self.perc)), self.h), pos = (0,0))
        imgAfter = imgAfter.Mirror(horizontally=True)
        self.after = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgAfter), pos = ((1200 - self.w)/2 + int(self.w * self.perc), 200))

        self.after.SetBitmap(wx.Bitmap(imgAfter))

        reset = wx.Button(self.panel, label = 'Reset')
        reset.Bind(wx.EVT_BUTTON, self.OnReset)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizer.Add(lbl, 0, wx.CENTER, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)

        # self.sizer.Add(self.before, 0, wx.LEFT|wx.RIGHT, 0)
        # self.sizer.Add(self.after, 0, wx.LEFT|wx.RIGHT, 0)
        self.mainSizer.Add(self.sizer, 0, wx.CENTER, 5)
        self.mainSizer.Add(self.slider, 0, wx.CENTER|wx.TOP, 20)


        self.panel.SetSizer(self.mainSizer)
        #self.mainSizer.Fit(self.frame)


        self.panel.Layout()

    def sliderUpdate(self, event):
        pos = self.slider.GetValue()
        self.perc = pos /100
        print(self.perc)
        imgBefore = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)
        imgBefore = imgBefore.Resize(size = (int(self.w * self.perc), self.h), pos = (0,0))
        self.before = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgBefore), pos = ((1200 - self.w)/2, 200))
        self.before.SetBitmap(wx.Bitmap(imgBefore))

        imgAfter = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)
        imgAfter = imgAfter.Mirror(horizontally=True)
        imgAfter = imgAfter.Resize(size = (int(self.w * (1 - self.perc)), self.h), pos = (0,0))
        imgAfter = imgAfter.Mirror(horizontally=True)
        self.after = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgAfter), pos = ((1200 - self.w)/2 + int(self.w * self.perc), 200))
        # afterImg = afterImg.Mirror(horizontally=True)
        self.after.SetBitmap(wx.Bitmap(imgAfter))
        # self.sizer.Clear()
        # self.sizer.Add(self.before, 0, wx.CENTER, 0)
        # self.sizer.Add(self.after, 0, wx.CENTER, 0)

        self.panel.Refresh()

    def OnReset(self, event):
        self.frame.Hide()
        # dirname = os.path.dirname(__file__)
        # file = os.path.join(dirname, 'UI.py')
        # os.system('python3 ' + file)



        


if __name__ == '__main__':
    app = PhotoCtrl()
    app.MainLoop()