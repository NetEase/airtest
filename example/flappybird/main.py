import os
import airtest

serialno = os.getenv('SERIALNO')
w, h = 1920, 1080
app = airtest.connect(serialno)
#app.touch(143, 968)
#app.touch(968, h-143) #143, 968)
#if app.exists('confirm.png'):
#    app.click('confirm.png')
app.click('quickenter.png')
app.click('checkbox.png')
app.type('blue\n')
app.click('boy.png')
app.click('enter.png')
app.click('tianxia.png')
#app.touch(1805, 942)
