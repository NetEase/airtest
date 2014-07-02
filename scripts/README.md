airtest recorder
==================

## how to use
### record
```sh
adb shell getevent -l | python airtest_recorder.py > main.py
```

### playback
```sh
python main.py
```

