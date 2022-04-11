import os
import wx
import wx.lib.statbmp as SB

from PIL import Image
from wx.lib.pubsub import pub 

PhotoMaxSize = 600
state = 1

class DropTarget(wx.FileDropTarget):
    
    def __init__(self, widget):
        wx.FileDropTarget.__init__(self)
        self.widget = widget
        
    def OnDropFiles(self, x, y, filenames):
        image = Image.open(filenames[0])
        image.thumbnail((PhotoMaxSize,PhotoMaxSize))
        image.save('thumbnail.png')
        pub.sendMessage('dnd', filepath='thumbnail.png')
        return True
        

class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Anima', size = (1200, 600))

        self.panel = wx.Panel(self.frame)
        self.panel.SetBackgroundColour(wx.Colour(233,243,255,255))
        pub.subscribe(self.update_image_on_dnd, 'dnd')

        self.createWidgets()
        self.frame.Show()

    def createWidgets(self):
        instructions = 'Browse for an image or Drag and Drop'
        img = wx.Image(800,600)

        self.imageCtrl = SB.GenStaticBitmap(self.panel, wx.ID_ANY, 
                                            wx.Bitmap(img))
        filedroptarget = DropTarget(self)
        self.imageCtrl.SetDropTarget(filedroptarget)

        title = "Anima" 
        lbl = wx.StaticText(self.panel,-1,style = wx.ALIGN_CENTER) 
        font = wx.Font(48, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        subFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)  
        lbl.SetFont(font) 
        lbl.SetLabel(title) 

        instructLbl = wx.StaticText(self.panel, label=instructions)
        instructLbl.SetFont(subFont)

        choices = ['1', '2', '3', '4'] 
        choice = wx.Choice(self.panel,choices = choices)
        choice.Bind(wx.EVT_CHOICE, self.onChoice)


        self.photoTxt = wx.TextCtrl(self.panel, size=(300,-1))
        browseBtn = wx.Button(self.panel, label='Browse')
        browseBtn.Bind(wx.EVT_BUTTON, self.on_browse)

        runButton = wx.Button(self.panel, label='Run')
        runButton.Bind(wx.EVT_BUTTON, self.onRun)
        
        

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.output = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(lbl, 0, wx.CENTER, 5)
        self.mainSizer.Add(choice, 0, wx.CENTER, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.LEFT|wx.RIGHT, 100)
        self.sizer.Add(self.photoTxt, 0, wx.ALL, 5)
        self.sizer.Add(browseBtn, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.CENTER, 5)

        self.mainSizer.Add(runButton, 0, wx.ALL|wx.CENTER, 20)

        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)


        self.panel.Layout()

    def on_browse(self, event):
        """ 
        Browse for file
        """
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy() 
        self.on_view()
    

    def onRun(self, event):
        # script name start
        dirname = os.path.dirname(__file__)
        file = os.path.join(dirname, 'cartoonize.py')
        os.system('python3 ' + file)
        


    def onChoice(self,event): 
        self.label.SetLabel("selected "+ self.choice.
        GetString( self.choice.GetSelection() ) +" from Choice")

    def update_image_on_dnd(self, filepath):
        self.on_view(filepath=filepath)

    def on_view(self, filepath=None):
        if not filepath:
            filepath = self.photoTxt.GetValue()
            
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = PhotoMaxSize
            NewH = PhotoMaxSize * H / W
        else:
            NewH = PhotoMaxSize
            NewW = PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
        print(1)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()

if __name__ == '__main__':
    app = PhotoCtrl()
    app.MainLoop()