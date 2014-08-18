package main

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type DeviceTouchScreen struct {
	InputEvent string `json:"input_event"`
	Width      int    `json:"width"`
	Height     int    `json:"height"`
	RawWidth   int    `json:"raw_width"`
	RawHeight  int    `json:"raw_height"`
}

type InputDevices struct {
	TouchScreen DeviceTouchScreen `json:"touchscreen"`
}

type Event struct {
	_time uint64
	Type  uint16
	Code  uint16
	Value int32
}

func atoi(a string) int {
	var i int
	_, err := fmt.Sscanf(a, "%d", &i)
	if err != nil {
		log.Fatal(err)
	}
	return i
}

func itoa(i int) string {
	return strconv.Itoa(i)
}

var (
	curpwd   string = filepath.Dir(os.Args[0])
	devicefd *os.File
	iptdevs  *InputDevices
)

func sendevent(fd io.Writer, type_, code string, value int32) (err error) {
	event := new(Event)

	fmt.Sscanf(type_, "%x", &event.Type)
	fmt.Sscanf(code, "%x", &event.Code)
	event.Value = value

	buffer := bytes.NewBuffer(nil)
	binary.Write(buffer, binary.LittleEndian, event._time)
	binary.Write(buffer, binary.LittleEndian, event.Type)
	binary.Write(buffer, binary.LittleEndian, event.Code)
	binary.Write(buffer, binary.LittleEndian, event.Value)
	_, err = io.Copy(fd, buffer)
	return err
}

func getShape() (width int, height int, err error) {
	//out, err := exec.Command("cat", "windows.txt").Output()
	out, err := exec.Command("dumpsys", "window").Output()
	if err != nil {
		return
	}
	rsRE := regexp.MustCompile(`\s*mRestrictedScreen=\(\d+,\d+\) (?P<w>\d+)x(?P<h>\d+)`)
	matches := rsRE.FindStringSubmatch(string(out))
	if len(matches) == 0 {
		err = errors.New("get shape(width,height) from device error")
		return
	}
	return atoi(matches[1]), atoi(matches[2]), nil
}

func rawGetDevices() (inputdevs *InputDevices, err error) {
	inputdevs = new(InputDevices)
	width, height, err := getShape()
	if err != nil {
		return
	}
	inputdevs.TouchScreen.Width = width
	inputdevs.TouchScreen.Height = height

	//procDevices, err := ioutil.ReadFile("proc.txt") // /proc/bus/input/devices
	procDevices, err := ioutil.ReadFile("/proc/bus/input/devices") // /proc/bus/input/devices
	if err != nil {
		return
	}
	hpatten := regexp.MustCompile(`Handlers=[\w\d]+`)
	mxptn := regexp.MustCompile(`0035.*max (\d+)`)
	myptn := regexp.MustCompile(`0036.*max (\d+)`)
	devs := hpatten.FindAllString(string(procDevices), -1)
	fmt.Println(devs)
	for _, dev := range devs {
		dev = dev[9:]
		if !strings.HasPrefix(dev, "event") {
			continue
		}
		out, err := exec.Command("getevent", "-p", "/dev/input/"+dev).Output()
		//out, err := exec.Command("echo", "hello-"+dev).Output()
		if err != nil {
			continue
		}
		mxs := mxptn.FindStringSubmatch(string(out))
		if len(mxs) == 0 {
			continue
		}
		mys := myptn.FindStringSubmatch(string(out))
		if len(mys) == 0 {
			continue
		}
		inputdevs.TouchScreen.RawWidth = atoi(mxs[1])
		inputdevs.TouchScreen.RawHeight = atoi(mys[1])
		inputdevs.TouchScreen.InputEvent = "/dev/input/" + dev
		break
	}
	if inputdevs.TouchScreen.InputEvent == "" {
		err = errors.New("no touchscreen event found in /dev/input/")
	}
	return
}

func getinputevent() (inputdevs *InputDevices, err error) {
	jsonfile := filepath.Join(curpwd, "devices.json")
	if _, er := os.Stat(jsonfile); er != nil { // handle devices.json not exists
		inputdevs, err = rawGetDevices()
		if err != nil {
			return
		}
		fd, er := os.OpenFile(jsonfile, os.O_RDWR|os.O_CREATE, 0644)
		if er != nil {
			err = er
			return
		}
		err = json.NewEncoder(fd).Encode(inputdevs)
		return
	} else { // load from jsonfile
		fd, er := os.Open(jsonfile)
		if er != nil {
			err = er
			return
		}
		defer fd.Close()
		inputdevs = new(InputDevices)
		err = json.NewDecoder(fd).Decode(inputdevs)
		return
	}
}

func xy2rawxy(x, y int) (int32, int32) {
	w, h := iptdevs.TouchScreen.Width, iptdevs.TouchScreen.Height
	rw, rh := iptdevs.TouchScreen.RawWidth, iptdevs.TouchScreen.RawHeight
	rx := int32(float32(x) / float32(w) * float32(rw))
	ry := int32(float32(y) / float32(h) * float32(rh))
	return rx, ry
}

func clickDown(x, y int) {
	fd := devicefd
	rx, ry := xy2rawxy(x, y)

	sendevent(fd, "3", "0039", 0x0ffffff4) // tracking id
	sendevent(fd, "1", "014a", 1)          // btn-touch down
	sendevent(fd, "3", "0035", rx)         // abs-mt-position x
	sendevent(fd, "3", "0036", ry)         // abs-mt-position y
	sendevent(fd, "3", "003a", 37)         // pressure
	sendevent(fd, "3", "0032", 4)          // ?
	sendevent(fd, "0", "0000", 0)          // sync-report
}
func clickUp() {
	fd := devicefd
	sendevent(fd, "3", "0039", -1) // tracking id
	sendevent(fd, "1", "014a", 0)  // btn-touch up
	sendevent(fd, "0", "0000", 0)  // sync-report
}

type FlagCommand struct {
	Func  func(args ...string) error
	Usage string
}

var (
	commands = map[string]FlagCommand{
		"tap":     {cmdTap, "<x> <y> [duration]"},
		"tapdown": {cmdTapdown, "<x> <y>"},
		"tapup":   {cmdTapup, ""},
		"swipe":   {cmdSwipe, "<x1> <y1> <x2> <y2> [duration]"},
		"test":    {cmdTest, ""},
		"version": {cmdVersion, ""},
	}
	ErrArguments = errors.New("error arguments parsed")
)

func cmdVersion(args ...string) (err error) {
	fmt.Println("1")
	return nil
}

func cmdTap(args ...string) (err error) {
	if len(args) != 2 && len(args) != 3 {
		return ErrArguments
	}
	duration := time.Millisecond * 300 // 0.3s
	if len(args) == 3 {
		duration, err = time.ParseDuration(args[2])
		if err != nil {
			return
		}
	}
	x, y := atoi(args[0]), atoi(args[1])
	clickDown(x, y)
	time.Sleep(duration)
	clickUp()
	fmt.Printf("xinput tap %d %d\n", x, y)
	return nil
}

func cmdSwipe(args ...string) (err error) {
	if len(args) != 4 && len(args) != 5 {
		return ErrArguments
	}
	duration := time.Millisecond * 500 // 0.5s
	if len(args) == 5 {
		duration, err = time.ParseDuration(args[4])
		if err != nil {
			return
		}
	}
	x1, y1 := atoi(args[0]), atoi(args[1])
	x2, y2 := atoi(args[2]), atoi(args[3])
	fmt.Printf("swipe %d %d   %d %d %s\n", x1, y1, x2, y2, duration)

	fd := devicefd
	move := func(x, y int, duration time.Duration) {
		rx, ry := xy2rawxy(x, y)
		sendevent(fd, "3", "0035", rx) // abs-mt-position x
		sendevent(fd, "3", "0036", ry) // abs-mt-position y
		sendevent(fd, "0", "0000", 0)  // sync-report
		if duration > 0 {
			time.Sleep(duration)
		}
	}
	mx, my := (x1+x2)/2, (y1+y2)/2
	start := time.Now()
	gap := duration / 4
	clickDown(x1, y1)                        // p1
	move((mx+x1)/2, (my+y1)/2, gap)          // p2
	move(mx, my, gap)                        // p3(middle)
	move((mx+x2)/2, (my+y2)/2, gap)          // p4
	move(x2, y2, duration-time.Since(start)) // p5
	clickUp()
	return nil
}

func cmdTapdown(args ...string) (err error) {
	if len(args) != 2 {
		return ErrArguments
	}
	x, y := atoi(args[0]), atoi(args[1])
	clickDown(x, y)
	return nil
}

func cmdTapup(args ...string) error {
	clickUp()
	return nil
}

func cmdTest(args ...string) error {
	w, h := iptdevs.TouchScreen.Width, iptdevs.TouchScreen.Height
	x1, y1 := w/5, h/2
	x2, y2 := w-x1, y1
	//x, y = 500, 500
	return cmdSwipe(itoa(x1), itoa(y2), itoa(x2), itoa(y2))
}

/*
click down

sendevent /dev/input/event1 1 330 1
sendevent /dev/input/event1 3 53 539
sendevent /dev/input/event1 3 54 959
sendevent /dev/input/event1 0 0 0

click up

sendevent /dev/input/event1 3 57 243
sendevent /dev/input/event1 1 330 0
sendevent /dev/input/event1 0 0 0
*/

func initDevice() (*os.File, error) {
	var err error
	iptdevs, err = getinputevent()
	if err != nil {
		log.Fatal(err)
	}
	//fmt.Println(iptdevs)
	tscreen := iptdevs.TouchScreen

	return os.OpenFile(tscreen.InputEvent, os.O_RDWR, 0644)
}

func main() {
	var usage = "Usage:	xinput ..."
	for name, c := range commands {
		usage = usage + "\n\txinput " + name + " " + c.Usage
	}
	flag.Usage = func() {
		fmt.Println(usage)
	}
	flag.Parse()
	if flag.NArg() == 0 {
		flag.Usage()
		return
	}

	var err error
	devicefd, err = initDevice()
	if err != nil {
		log.Fatal(err)
	}
	defer devicefd.Close()

	cmdName := flag.Arg(0)
	cmdArgs := flag.Args()[1:]
	fn, exists := commands[cmdName]
	if !exists {
		log.Fatal("command not found")
	}
	err = fn.Func(cmdArgs...)
	if err != nil {
		log.Fatal(err)
	}
}
