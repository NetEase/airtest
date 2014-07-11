API Reference
========================

after installed successfully. you can import like
```
# import python lib
import airtest
```

step1 connect device
```
# get serialno by call: adb devices
serialno = 'xxxxx888882111'
deviceType = 'android' # can be windows or ios

# connect to your android devices
app = airtest.connect(serialno, device=deviceType)
```

click(...) # click by image file
```
app.click(P)
# P can be
# - filename: 'start.png'
# - position: (100, 200)
```

clickOnAppear(...)
```
app.clickOnAppear(filename, [seconds])
# eg: app.clickOnAppear('image1.png', 10)
```

find(...) # find a image position located in screen
```
(x, y) = app.find(filename)
```

wait(...) # wait until image shows
```
app.wait(filename, [seconds])
# filename is the image name
# seconds is the longest time waited.
# @return position images find, or Raise RuntimeError
# this is called find(..) to get images position
```

exists(...) # judge if image exists
```
app.exists('apple.png')
# @return (True|False)
# just exactly call wait
