#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import atexit
import threading
import tempfile
import ConfigParser

import cv2

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mainui import Ui_Dialog

import airtest

reload(sys)
sys.setdefaultencoding('utf-8') 

__dir__ = os.path.dirname(os.path.abspath(__file__))

def gobackground(fn):
    ''' decorator for threading '''
    def _wrapper(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
        return t
    return _wrapper

class TestWidget(QWidget, Ui_Dialog):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8")) 
        
        self.app = None
        self.scaleRate = 1.0
        self.rubberBand = None
        self.screenImage = None
        self.cropImage1 = None
        self.cropImage2 = None
        self.MousePressed = False

        clickfile1 = tempfile.mktemp(prefix='', suffix='.png', dir='')
        clickfile2 = tempfile.mktemp(prefix='', suffix='.png', dir='')
        self.leCrop1.setText(clickfile1)
        self.leCrop2.setText(clickfile2)

        # save workspace
        self.cf = ConfigParser.SafeConfigParser()
        cfgpath = os.path.join(__dir__, 'airtest.ini')
        def changeWorkspace(workspace):
            if not workspace:
                return
            print workspace
            self.leWorkspace.setText(workspace)
            self.cf.set('airtest', 'workspace', workspace)
            os.chdir(workspace)
            with open(cfgpath, 'w') as file:
                self.cf.write(file)
        if os.path.exists(cfgpath):
            self.cf.read(cfgpath)
        else:
            self.cf.add_section('airtest')
            self.cf.set('airtest', 'workspace', os.getcwd())
        self.workspace = self.cf.get('airtest', 'workspace')
        changeWorkspace(self.workspace)
        self.changeWorkspace = changeWorkspace

        # redirect stdout to textbox(tbConsole)
        class CConsole(object):
            def __init__(self, parent, level='DEBUG'):
                self.parent = parent
                self.level = level
                self.line = ''
            def write(self, text):
                p = text.find('\n')
                if p != -1:
                    out = self.line + text[:p]
                    self.line = text[p:]
                    timestamp = time.strftime('%H:%M:%S')
                    self.parent.tbConsole.append(self.parent.trUtf8("%1 %2: <b>%3</b>").arg(self.level, timestamp, out))
                else:
                    self.line += text 
        sys.stdout = CConsole(self, level='INFO')
        # sys.stderr = CConsole(self, level='STDERR')

        self.btnRun.clicked.connect(self.airRun)
        self.btnRun.setToolTip("run test code")
        self.btnConnect.clicked.connect(self.airConnect)
        self.btnRefresh.clicked.connect(self.airRefresh)
        self.btnRestart.clicked.connect(self.airRestart)
        self.btnSelectDir.clicked.connect(self.selectDir)
        self.btnClick.clicked.connect(self.airClick)
        self.btnDrag.clicked.connect(self.airDrag)
        # self.btnWait.clicked.connect(self.airWait)
        self.btnFindAll.clicked.connect(self.airFindAll)
        self.btnClear.clicked.connect(self.airClear)
        self.btnSave.clicked.connect(self.airSave)
        self.btnRunScripts.clicked.connect(self.airRunScripts)
        self.cbDevice.activated.connect(self.airDeviceChanged)
        self.cbPhoneno.setAutoCompletion(True)

        # initial
        self.airDeviceChanged()

        self.screenImage = QImage('screen.png')
        if self.screenImage:
            self.imgWidth = self.screenImage.width()
            self.resizeEvent()
        pixmap = QPixmap.fromImage(self.screenImage)
        self.lblScreen.setPixmap(pixmap)

    def airDeviceChanged(self, index=0):
        print 'changed', self.cbDevice.itemText(index)
        item = self.cbDevice.itemText(index)
        self.cbPhoneno.clear()
        if item == 'android':
            for phoneno, type_ in airtest.getDevices():
                if type_ == 'device':
                    self.cbPhoneno.addItem(phoneno)
        elif item == 'windows':
            import utils
            for name in utils.getAllWinProcessName():
                if name.endswith('.exe'):
                    self.cbPhoneno.addItem(name)

    def resizeEvent(self, ev=None):
        if not self.screenImage or self.screenImage.height() == 0:
            return
        rate = float(self.screenImage.width())/self.screenImage.height()
        width = self.widget.height()*rate
        if width > self.widget.width():
            w, h = self.widget.width(), int(self.widget.width()/rate)
        else:
            w, h = width, self.widget.height()
        if hasattr(self, 'imgWidth'):
            self.scaleRate = float(self.imgWidth)/float(w)
        self.lblScreen.resize(w, h)

    def _fixQPoint2(self, p1, p2):
        ''' @return point of leftTop and rightBottom '''
        ltx, lty = min(p1.x(), p2.x()), min(p1.y(), p2.y())
        rbx, rby = max(p1.x(), p2.x()), max(p1.y(), p2.y())
        return QPoint(ltx, lty), QPoint(rbx, rby)

    def _pointScreen2Image(self, p):
        ''' @return (x, y) which real in image file '''
        leftTop = self.widget.pos()
        (sx, sy) = p.x()-leftTop.x(), p.y()-leftTop.y()
        return int(sx*self.scaleRate), int(sy*self.scaleRate)

    def _saveQImage(self, qimage, filename):
        ''' save file to workspace '''
        if not os.path.isabs(filename):
            filename = self._workspace(filename)
        dirname = os.path.dirname(filename) or '.'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        print 'image save to:', str(filename).encode('gb18030')
        return qimage.save(filename)

    def _workspace(self, relative_path = None):
        ws = str(self.leWorkspace.displayText()).strip()
        if relative_path:
            return os.path.join(ws, relative_path)
        return ws
        

    def mousePressEvent(self, event):
        rect = QRect(self.widget.pos(), self.lblScreen.size())
        if not rect.contains(event.pos()):
            return
        self.MousePressed = True
        self.pointOrigin = event.pos()
        if not self.rubberBand:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.rubberBand.setGeometry(QRect(self.pointOrigin, QSize()))
        self.rubberBand.show()


    def mouseMoveEvent(self, event):
        if not self.MousePressed:
            return
        leftTop, rightBottom = self._fixQPoint2(self.pointOrigin, event.pos())
        self.rubberBand.setGeometry(QRect(leftTop, rightBottom))

    def mouseReleaseEvent(self, event):
        if not self.MousePressed:
            return
        self.MousePressed = False
        # only click event
        if event.pos() == self.pointOrigin:
            (x, y) = self._pointScreen2Image(event.pos())
            self.leCode.setText('app.click((%d, %d))' %(x, y))
            return

        # select event
        self.cropSelected(event) # crop image
        # self.airImageLocate(event)

        image = None
        if self.cropImage1 and event.button() == Qt.LeftButton:
            cropname = str(self.leCrop1.displayText())
            image = self.cropImage1
        elif self.cropImage2 and event.button() == Qt.RightButton:
            cropname = str(self.leCrop2.displayText())
            image = self.cropImage2

        if image:
            self.leCode.setText(self.trUtf8("app.click('%1')").arg(cropname))
            savepath = os.path.join(str(self.cbDestdir.currentText()), cropname)
            self._saveQImage(image, savepath)
            

    def airImageLocate(self, event):
        if event.button() == Qt.LeftButton: 
            currImage = self.cropImage1
        else:
            currImage = self.cropImage2
        if not currImage:
            print 'no image croped before'
            return

        queryfile = tempfile.mktemp(prefix='query-', suffix='.png')
        trainfile = tempfile.mktemp(prefix='train-', suffix='.png')
        debugfile = tempfile.mktemp(prefix='debug-', suffix='.png')
        print queryfile
        # print self.cropImage.save(queryfile)
        print self._saveQImage(currImage, queryfile)
        print self._saveQImage(self.screenImage, trainfile)
        atexit.register(os.unlink, queryfile)
        atexit.register(os.unlink, trainfile)

        from airtest import image
        positions = image.locate_one_image(trainfile, queryfile, outfile=debugfile)
        atexit.register(os.unlink, debugfile)

        self.lblScreen.setPixmap(QPixmap.fromImage(QImage(debugfile)))
        self.rubberBand.hide()
        self.resizeEvent(None)
        print 'POSITIONS:', positions

    def airRun(self):
        code = str(self.leCode.displayText())
        code = code.replace("app.", "self.app.")
        print 'RUN CODE:', str(self.leCode.displayText())
        # print 'CWD:', self.trUtf8(os.getcwd())
        print 'RETURN:', eval(code)
        self.textBrowser.append(str(self.leCode.displayText()))
        time.sleep(0.5)
        self.airRefresh()
        self.textBrowser.setFocus()

    def airRestart(self):
        devno = str(self.cbPhoneno.currentText())
        device = str(self.cbDevice.currentText())
        airtest.stop(devno, device)
        airtest.start(devno, device)
        time.sleep(0.5)
        self.airConnect()
      
    def airRefresh(self):
        if self.app != None:
            print 'start takesnapshot'
            self.app.takeSnapshot('screen.png')
            image = QImage()
            print 'load image:', self.trUtf8(os.getcwd()), 'screen.png'
            if not image.load('screen.png'):
                print 'load image failed'
                return
            self.imgWidth = image.width()
            self.imgHeight = image.height()
            self.screenImage = image

            self.lblScreen.setPixmap(QPixmap.fromImage(self.screenImage))
            self.resizeEvent(None)

            self.textBrowser.setFocus()
            self.cropImage1 = None
            self.cropImage2 = None
            self.lblCutImage1.clear()
            self.lblCutImage2.clear()
            tmpname1 = tempfile.mktemp(prefix='', suffix=".png", dir='')
            self.leCrop1.setText(tmpname1)
            tmpname2 = tempfile.mktemp(prefix='', suffix=".png", dir='')
            self.leCrop1.setText(tmpname2)
            #if self.rubberBand:
            #    self.rubberBand.hide()
            
    def airConnect(self):
        device = self.cbDevice.currentText()
        phoneno = self.cbPhoneno.currentText()
        try:
            self.app = airtest.connect(str(phoneno), device=str(device), monitor=False)
            self.app.globalSet(image_match_method='template', threshold=0.7)
        except Exception as e:
            print 'CONNECT FAILED: %s' %(str(e))
        else:
            self.cbDestdir.clear()
            self.cbDestdir.addItem('image-%d_%d'%(self.app.width, self.app.height))
            self.cbDestdir.addItem('image-'+str(device))
            self.cbDestdir.addItem('image')

            suffix = '-%dx%d.png'%(self.app.width, self.app.height)
            tmpname = tempfile.mktemp(prefix='', suffix=suffix, dir='')
            print tmpname
            self.leCrop1.setText(tmpname)
        # self.textBrowser.clear()
        # code = "app=airtest.connect(\""+str(phoneno)+"\",device=\""+str(device)+"\")"
        # self.textBrowser.append(code)
        self.airRefresh()
        self.textBrowser.setFocus()

    def selectDir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Dir')
        directory = str(directory)
        if directory:
            # self.leWorkspace.setText(directory)
            # os.chdir(directory.encode('gb18030')) 
            # print directory, os.getcwd()
            self.changeWorkspace(directory)

    def cropSelected(self,event):            
        if not self.rubberBand:
            print 'no rectangle area selected'
            return False
        if event.pos() == self.pointOrigin:
            return False
        topLeft = self.rubberBand.pos()
        size = self.rubberBand.size()
        width, height = map(int, [size.width()*self.scaleRate, size.height()*self.scaleRate])
        (lrx, lry) = self._pointScreen2Image(topLeft)
        print 'rect:', (lrx, lry), (width, height)
        max_width = self.lblCutImage1.width()
        max_height = self.lblCutImage1.height()
        if event.button() == Qt.LeftButton:
            self.cropImage1 = self.screenImage.copy(lrx, lry, width, height)
            self.lblCutImage1.setPixmap(QPixmap.fromImage(self.cropImage1.scaled(max_width, max_height, 1)))
            # tmpname = tempfile.mktemp(prefix='crop-', suffix='.png', dir='')
            # self.leCrop1.setText(tmpname)
        else:
            self.cropImage2 = self.screenImage.copy(lrx, lry, width, height)
            self.lblCutImage2.setPixmap(QPixmap.fromImage(self.cropImage2.scaled(max_width, max_height, 1)))
        self.rubberBand.hide()

    def airFindAll(self):
        image_path = str(self.cbDestdir.currentText()) + os.path.sep + str(self.leCrop1.displayText())

        from airtest.image import template as tmplsearch
        threshold = self.sbThreshold.value()
        points = tmplsearch.findall(image_path, 'screen.png', threshold)
        # from airtest import devsuit
        # points=devsuit.find_multi_image("screen.png",os.path.basename(clickfile),0.9)
        
        screenImg = cv2.imread("screen.png")
        w, h, s = cv2.imread(image_path).shape
        if not points: 
            print "Obeject can not been found"
            return
        for point in points:
            cv2.rectangle(screenImg,(int(point[0]-h/2),int(point[1])-w/2),(int(point[0])+h/2,int(point[1])+w/2),(0,0,0),2,1)
            print "Obeject has been found, Position:",point
        cv2.imshow("Obeject has been found",screenImg)
        self.textBrowser.setFocus()
    

    def airClick(self):
        if self.cropImage1:
            self.cropImage = self.cropImage1
            clickfile=os.path.join(str(self._workspace()),str(self.leCrop1.text()))
        else:
            self.cropImage = self.cropImage2
            clickfile=os.path.join(str(self._workspace()),str(self.leCrop2.text()))
        print str(clickfile).encode('gb18030')
        self._saveQImage(self.cropImage, clickfile)
        self.leCode.setText('app.click("%s")' %(os.path.basename(clickfile)))
        self.textBrowser.setFocus()
    
    def airWait(self): 
        if self.cropImage1:
            self.cropImage = self.cropImage1
            clickfile=os.path.join(str(self._workspace()),str(self.leCrop1.text()))
        else:
            self.cropImage = self.cropImage2
            clickfile=os.path.join(str(self._workspace()),str(self.leCrop2.text()))
        print str(clickfile).encode('gb18030')
        self._saveQImage(self.cropImage, clickfile)
        self.leCode.setText('app.click(app.wait("%s"))' %(os.path.basename(clickfile)))
        self.textBrowser.setFocus()
        
    def airDrag(self):
        clickfile1 = os.path.join(str(self._workspace()),str(self.leCrop1.text()))
        self._saveQImage(self.cropImage1, clickfile1)
        clickfile2 = os.path.join(str(self._workspace()),str(self.leCrop2.text()))
        self._saveQImage(self.cropImage2, clickfile2)
        self.leCode.setText('app.drag("%s","%s")' %(os.path.basename(clickfile1),os.path.basename(clickfile2)))
        self.textBrowser.setFocus()
    
    def airClear(self):
        self.textBrowser.clear()
        self.textBrowser.setFocus()
        
    def airSave(self):
        device = self.cbDevice.currentText()
        phoneno = self.cbPhoneno.currentText()

        contents="#!/usr/bin/env python\n## -*- coding: utf-8 -*-\n\nimport airtest\n"
        contents += "app = airtest.connect('{phoneno}', device='{device}')\n".format(
            phoneno = str(phoneno), device=str(device)
            )
        contents=contents+self.textBrowser.toPlainText()
        mainfile = os.path.join(str(self._workspace()),'work.py')
        with open(str(mainfile).encode('gb18030'), 'w') as file:
            file.writelines(contents)
        self.textBrowser.setFocus()
    
    def airRunScripts(self):
        commands=self.textBrowser.toPlainText()
        commands = str(commands)
        lines = commands.splitlines()
        app = self.app
        print app # only to skip pylint warning
        for command in lines:
            command = command.strip()
            if not command:
                continue
            try:
                self.tbConsole.append(self.trUtf8("COMMAND: "+command))
                exec command
            except Exception,e:
                self.tbConsole.append(self.trUtf8(command))
                self.tbConsole.append(self.trUtf8(u"Exception："+str(e)+"\n"))
                break
        self.textBrowser.setFocus()

    def sayHello(self):
        yourName, okay = QInputDialog.getText(self, self.trUtf8("Your name?"), self.trUtf8(b'Name'), text="hello")
        if not okay or yourName == u'':
            self.tbConsole.append(self.trUtf8("Hello stranger!"))
        else:
            self.tbConsole.append(self.trUtf8("Hello <b>%1</b>").arg(yourName))

app_ = QApplication(sys.argv)
print 'Program started.'
testWidget = TestWidget()
testWidget.show()
sys.exit(app_.exec_())
