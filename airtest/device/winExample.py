#decoding:utf-8
import windows
import wx

winname = "Example"
operation = windows.IDevice(winname)

def snapshot_test(evt):
    pic=operation.snapshot("target.png")
    pic.show()
def drag_test(evt):
    (x1,y1,x2,y2)=operation.windowposition()
    (width,height)=operation.shape()
    operation.drag((x1+width/2, y1+10), (x2, y2))

def cut_test(evt):
    operation.cutimage(filename="test.png")
    
def position_test(evt):   
    print "The current position of mouse is"+str(operation.mouseposition())
    print "The  position of target window is"+str(operation.windowposition())
    print "The shape of target window is"+str(operation.shape())
    
def type_test(evt):
    (x1,y1,x2,y2)=operation.windowposition()
    (width,height)=operation.shape()
    operation.touch(x1+width/2,y1+height/2)
    test="123sadasdfzx+_;;;asdad"
    operation.type(test)#在当前窗口下输入test中的文字
    



'''生成一个窗口'''
app = wx.App()#生成一个窗口
win = wx.Frame(None,title = "Example",size=(400,160))
bkg = wx.Panel(win)

dragbtn = wx.Button(bkg,label=u'拖动测试')
dragbtn.Bind(wx.EVT_BUTTON,drag_test)

snapbtn = wx.Button(bkg,label=u'snapshot测试')
snapbtn.Bind(wx.EVT_BUTTON,snapshot_test)

cutbtn = wx.Button(bkg,label=u'cut测试')
cutbtn.Bind(wx.EVT_BUTTON,cut_test)

typebtn = wx.Button(bkg,label=u'type测试')
typebtn.Bind(wx.EVT_BUTTON,type_test)

positionbtn = wx.Button(bkg,label=u'位置测试')
positionbtn.Bind(wx.EVT_BUTTON,position_test)

vbox = wx.BoxSizer(wx.VERTICAL)
vbox.Add(dragbtn,proportion=0,flag = wx.LEFT,border=5) 
vbox.Add(snapbtn,proportion=0,flag = wx.LEFT,border=5)
vbox.Add(cutbtn,proportion=0,flag = wx.LEFT,border=5)
vbox.Add(typebtn,proportion=0,flag = wx.LEFT,border=5)
vbox.Add(positionbtn,proportion=0,flag = wx.LEFT,border=5)


static_text = wx.StaticText(bkg,-1,u"测试")   
filename = wx.TextCtrl(bkg)
hbox = wx.BoxSizer()
hbox.Add(static_text,proportion=0,flag = wx.RIGHT,border=5)
hbox.Add(filename,proportion=1,flag = wx.EXPAND) 
hbox.Add(vbox,proportion=0,flag = wx.LEFT,border=5) 
bkg.SetSizer(hbox) 
win.Show()
app.MainLoop()

