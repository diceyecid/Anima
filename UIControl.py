import os
import wx
from wx.lib.pubsub import pub
import wx.lib.statbmp as SB

from PIL import Image

PhotoMaxSize = 800
maxSize = 600
pub.sendMessage("state", message = 'input')
# drop module from https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
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
    

#Input frame
class Input(wx.Frame):
    #create input frame and set background color
    def __init__(self):
        self.frame = wx.Frame(None, title='Anima', size = (1200, 600))

        self.panel = wx.Panel(self.frame)
        self.panel.SetBackgroundColour(wx.Colour(233,243,255,255))
        pub.subscribe(self.update_image_on_dnd, 'dnd')
        self.createWidgets()
        self.frame.Show(), 

    # create components for the input frame
    def createWidgets(self):

        instructions = 'Browse for an image or Drag and Drop'
        #create placeholder to let the user drop their image -- https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
        img = wx.Image(800,600)

        self.imageCtrl = SB.GenStaticBitmap(self.panel, wx.ID_ANY, 
                                            wx.Bitmap(img))
        filedroptarget = DropTarget(self)
        self.imageCtrl.SetDropTarget(filedroptarget)

        #Set title and font styles
        title = "Anima" 
        lbl = wx.StaticText(self.panel,-1,style = wx.ALIGN_CENTER) 
        font = wx.Font(48, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        subFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)  
        lbl.SetFont(font) 
        lbl.SetLabel(title) 

        instructLbl = wx.StaticText(self.panel, label=instructions)
        instructLbl.SetFont(subFont)
        self.style = 'shinkai'

        #Create drop-down menu
        choices = ['shinkai', 'hayao', 'hosoda', 'paprika'] 
        self.choice = wx.Choice(self.panel,choices = choices)
        self.choice.Bind(wx.EVT_CHOICE, self.onChoice)

        #Create button to let the user browse images from local disk -- https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
        self.photoTxt = wx.TextCtrl(self.panel, size=(300,-1))
        browseBtn = wx.Button(self.panel, label='Browse')
        browseBtn.Bind(wx.EVT_BUTTON, self.on_browse)

        #create run button
        runButton = wx.Button(self.panel, label='Run')
        runButton.Bind(wx.EVT_BUTTON, self.onRun)
        
        
        #use sizer to organize the layout
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
        # browse image from local disk -- https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy() 
        self.on_view()

    def onRun(self, event):
        # send message through pubsub
        pub.sendMessage("state", message = 'output')
        # run the backend code 
        os.system('python3 driver.py --input ' + self.pathDir + ' --styles ' + self.style + ' --overwrite')
        # send message through pubsub and close current frame 
        pub.sendMessage("path", message = self.pathDir, arg2 = self.style)      
        self.frame.Close()


    def onChoice(self,event): 
        # get the style that choosed by the user
        self.style = self.choice.GetString( self.choice.GetSelection())


    def update_image_on_dnd(self, filepath):
        # pass filepath -- https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
        self.on_view(filepath=filepath)

    def on_view(self, filepath=None):
        # set the image to the bitmap -- https://www.blog.pythonlibrary.org/2017/10/25/wx_drag_and_drop_images/
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


# output frame
class Output(wx.Frame):
    def __init__(self):
        # create output frame
        wx.Frame.__init__(self)
        self.frame = wx.Frame(None, title='Anima', size = (1600, 800))
        self.panel = wx.Panel(self.frame)
        self.panel.SetBackgroundColour(wx.Colour(233,243,255,255))

        self.outputCreateWidgets()
        self.frame.Show()

    def outputCreateWidgets(self):
        # create components for the output frame
        title = "Anima" 
        lbl = wx.StaticText(self.panel,-1,style = wx.ALIGN_CENTER) 
        font = wx.Font(48, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)
        subFont = wx.Font(15, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL)  
        lbl.SetFont(font) 
        lbl.SetLabel(title) 

        # get message from pub
        pub.subscribe(self.getMessage, "path")

        # create the reset button
        reset = wx.Button(self.panel, label = 'Reset')
        reset.Bind(wx.EVT_BUTTON, self.OnReset)

        # set the layout
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.mainSizer.Add(lbl, 0, wx.CENTER, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY),
                           0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(reset, 0, wx.CENTER|wx.TOP, 20)
        self.panel.SetSizer(self.mainSizer)


        self.panel.Layout()


    def OnReset(self, event):
        # the pass the message and close current frame
        pub.sendMessage("state", message = 'input')
        self.frame.Close()

    def getMessage(self, message, arg2=None):
        # get messages from the pub
        self.location = message
        if arg2:
            self.style = arg2
        else:
            self.style = shinkai

        # scale the image, preserving the aspect ratio
        imgbef = wx.Image(self.location, wx.BITMAP_TYPE_ANY)
        W = imgbef.GetWidth()
        H = imgbef.GetHeight()
        if W > H:
            NewW = maxSize
            NewH = maxSize * H / W
        else:
            NewH = maxSize
            NewW = maxSize * W / H

        # open images that import by user and output by this application
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
# controller to control the frame
    def __init__(self):
        # create the application
        wx.App.__init__(self)
        self.frame = Input()
        pub.subscribe(self.getMSG, "state")

	
    def getMSG(self, message):
        # set frame based on the message
        if message == "input":
            self.frame = Input()
        else:
            self.frame = Output()

# create this application and mainloop
if __name__ == "__main__":
    app = controller()
    app.MainLoop()
