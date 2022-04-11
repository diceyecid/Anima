import os, output
import wx
from wx.lib.pubsub import pub
import wx.lib.statbmp as SB

from PIL import Image

PhotoMaxSize = 800
pub.sendMessage("state", message = 'input')

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
    


class Input(wx.Frame):
    def __init__(self):
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
        self.style = 'shinkai'
        choices = ['shinkai', 'hayao', 'hosoda', 'paprika'] 
        self.choice = wx.Choice(self.panel,choices = choices)
        self.choice.Bind(wx.EVT_CHOICE, self.onChoice)


        self.photoTxt = wx.TextCtrl(self.panel, size=(300,-1))
        browseBtn = wx.Button(self.panel, label='Browse')
        browseBtn.Bind(wx.EVT_BUTTON, self.on_browse)

        runButton = wx.Button(self.panel, label='Run')
        runButton.Bind(wx.EVT_BUTTON, self.onRun)
        
        

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.output = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(lbl, 0, wx.CENTER, 5)
        self.mainSizer.Add(self.choice, 0, wx.CENTER, 5)
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

    def printMsg(self, message):
        print(message == "output")
        return message

    def onRun(self, event):
        # script name start
        # dirname = os.path.dirname(__file__)
        # file = os.path.join(dirname, 'cartoonize.py')
        # os.system('python3 ' + file)
        pub.sendMessage("state", message = 'output')
        #print(self.pathDir)
        
        os.system('python3 driver.py --input ' + self.pathDir + ' --styles ' + self.style)
        pub.sendMessage("path", message = self.pathDir, arg2 = self.style)
        self.frame.Close()


    def onChoice(self,event): 
        # self.label.SetLabel("selected "+ self.choice.
        # GetString( self.choice.GetSelection() ) +" from Choice")
        self.style = self.choice.GetString( self.choice.GetSelection())
        print(self.style)

    def update_image_on_dnd(self, filepath):
        self.on_view(filepath=filepath)

    def on_view(self, filepath=None):
        if not filepath:
            filepath = self.photoTxt.GetValue()
        
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        self.pathDir = filepath
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



class Output(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self)
        self.frame = wx.Frame(None, title='Anima', size = (1600, 800))



        self.panel = wx.Panel(self.frame)
        self.panel.SetBackgroundColour(wx.Colour(233,243,255,255))

        self.outputCreateWidgets()
        self.frame.Show()

    def outputCreateWidgets(self):

        title = "Anima" 
        lbl = wx.StaticText(self.panel,-1,style = wx.ALIGN_CENTER) 
        font = wx.Font(48, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        subFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)  
        lbl.SetFont(font) 
        lbl.SetLabel(title) 

    

        # self.slider = wx.Slider(self.panel, -1, 99, 1, 99, size = (self.img.GetWidth(), 40))
        # self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        pub.subscribe(self.getMessage, "path")
        # self.location = 'input/place.jpg'
        # self.style = 'shinkai'



        # imgbef = wx.Image(self.location, wx.BITMAP_TYPE_ANY)
        # W = imgbef.GetWidth()
        # H = imgbef.GetHeight()
        # if W > H:
        #     NewW = PhotoMaxSize
        #     NewH = PhotoMaxSize * H / W
        # else:
        #     NewH = PhotoMaxSize
        #     NewW = PhotoMaxSize * W / H
        # imgbef = imgbef.Scale(NewW,NewH)
        # self.before = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgbef), pos = ((1600 - imgbef.GetWidth() * 2)/2, 200))
        # self.before.SetBitmap(wx.Bitmap(imgbef))
        # #self.before.SetPosition(100, 100)

        # filename = self.location.split(os.path.sep)[-1]
        # print(filename)
        # afterLocation = 'output/'+ self.style + '/adaptive/' + filename
        # imgAfter = wx.Image(afterLocation, wx.BITMAP_TYPE_ANY)
        # imgAfter = imgAfter.Scale(NewW, NewH)
        # self.after = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgAfter), pos = ((1600 - imgbef.GetWidth() * 2)/2 + imgbef.GetWidth() + 20, 200))
        # self.after.SetBitmap(wx.Bitmap(imgAfter))

        reset = wx.Button(self.panel, label = 'Reset')
        reset.Bind(wx.EVT_BUTTON, self.OnReset)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizer.Add(lbl, 0, wx.CENTER, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)

        #self.sizer.Add(self.before, 0, wx.LEFT|wx.RIGHT, 0)
        #self.sizer.Add(self.after, 0, wx.LEFT|wx.RIGHT, 0)
        self.mainSizer.Add(self.sizer, 0, wx.CENTER, 5)
        self.mainSizer.Add(reset, 0, wx.CENTER|wx.TOP, 20)
        # self.mainSizer.Add(self.slider, 0, wx.CENTER|wx.TOP, 20)


        self.panel.SetSizer(self.mainSizer)
        #self.mainSizer.Fit(self.frame)


        self.panel.Layout()

    # def sliderUpdate(self, event):
        # pos = self.slider.GetValue()
        # pub.sendMessage("state", message = 'output')
        # self.perc = pos /100
        # print(1)
        # imgBefore = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)
        # imgBefore = imgBefore.Resize(size = (int(self.w * self.perc), self.h), pos = (0,0))
        # self.before = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgBefore), pos = ((1200 - self.w)/2, 200))
        # self.before.SetBitmap(wx.Bitmap(imgBefore))

        # imgAfter = wx.Image(self.imgLoc, wx.BITMAP_TYPE_ANY)
        # imgAfter = imgAfter.Mirror(horizontally=True)
        # imgAfter = imgAfter.Resize(size = (int(self.w * (1 - self.perc)), self.h), pos = (0,0))
        # imgAfter = imgAfter.Mirror(horizontally=True)
        # self.after = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgAfter), pos = ((1200 - self.w)/2 + int(self.w * self.perc) + 100, 200))
        # # afterImg = afterImg.Mirror(horizontally=True)
        # self.after.SetBitmap(wx.Bitmap(imgAfter))
        # self.sizer.Clear()
        # self.sizer.Add(self.before, 0, wx.CENTER, 0)
        # self.sizer.Add(self.after, 0, wx.CENTER, 0)
        # self.panel.Refresh()

    def OnReset(self, event):
        pub.sendMessage("state", message = 'input')
        self.frame.Close()

    def getMessage(self, message, arg2=None):
        self.location = message
        if arg2:
            self.style = arg2
        else:
            self.style = shinkai

        imgbef = wx.Image(self.location, wx.BITMAP_TYPE_ANY)
        W = imgbef.GetWidth()
        H = imgbef.GetHeight()
        if W > H:
            NewW = PhotoMaxSize
            NewH = PhotoMaxSize * H / W
        else:
            NewH = PhotoMaxSize
            NewW = PhotoMaxSize * W / H
        imgbef = imgbef.Scale(NewW,NewH)
        self.before = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgbef), pos = ((1600 - imgbef.GetWidth() * 2)/2, 150))
        self.before.SetBitmap(wx.Bitmap(imgbef))

        filename = self.location.split(os.path.sep)[-1]
        afterLocation = 'output/'+ self.style + '/adaptive/' + filename
        imgAfter = wx.Image(afterLocation, wx.BITMAP_TYPE_ANY)
        imgAfter = imgAfter.Scale(NewW, NewH)
        self.after = SB.GenStaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(imgAfter), pos = ((1600 - imgbef.GetWidth() * 2)/2 + imgbef.GetWidth() + 20, 150))
        self.after.SetBitmap(wx.Bitmap(imgAfter))
        self.panel.Refresh()
        




class controller(wx.App):

    def __init__(self):
        wx.App.__init__(self)
        self.frame = Input()
        pub.subscribe(self.getMSG, "state")

        #self.frame
        # if pub.subscribe(Input().printMsg, 'state') == "input":
        #     #frame = Input()
        #     print(pub.subscribe(Input().printMsg, 'state'))
        # if pub.subscribe(Input().printMsg, 'state') == "output":
        #     print(pub.subscribe(Input().printMsg, 'state'))
	
    def getMSG(self, message):
        if message == "input":
            self.frame = Input()
        else:
            self.frame = Output()


if __name__ == "__main__":
    app = controller()

    app.MainLoop()