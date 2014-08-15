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
	"strings"
	"time"
)

type DeviceTouchScreen struct {
	ProcDevice string `json:"proc_device"`
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
	fmt.Sscanf(a, "%d", &i)
	return i
}

func sendevent(fd io.Writer, args ...string) (err error) {
	if len(args) != 3 {
		return errors.New("use: sendevent device type code value")
	}
	event := new(Event)

	fmt.Sscanf(args[0], "%d", &event.Type)
	fmt.Sscanf(args[1], "%d", &event.Code)
	fmt.Sscanf(args[2], "%d", &event.Value)

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
		inputdevs.TouchScreen.ProcDevice = "/dev/input/" + dev
		break
		//fmt.Println(dev, mxs[1], mys[1], string(out))
	}
	if inputdevs.TouchScreen.ProcDevice == "" {
		err = errors.New("no touchscreen event found in /dev/input/")
	}
	return
	//return nil, errors.New("fk")
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

var curpwd string = filepath.Dir(os.Args[0])

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
func main() {
	flag.Parse()
	iptdevs, err := getinputevent()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(iptdevs)
	tscreen := iptdevs.TouchScreen

	fd, err := os.OpenFile(tscreen.ProcDevice, os.O_RDWR, 0644)
	if err != nil {
		return
	}
	defer fd.Close()

	clickDown := func(x, y int) {
		sendevent(fd, "3", "57", "0")   // tracking id
		sendevent(fd, "1", "330", "1")  // btn-touch down
		sendevent(fd, "3", "53", "539") // abs-mt-position x
		sendevent(fd, "3", "54", "959") // abs-mt-position y
		sendevent(fd, "3", "58", "37")  // pressure
		sendevent(fd, "3", "50", "4")   // ?
		sendevent(fd, "0", "0", "0")    // sync-report
	}
	clickUp := func() {
		sendevent(fd, "3", "57", "0")  // tracking id
		sendevent(fd, "1", "330", "0") // btn-touch up
		sendevent(fd, "0", "0", "0")   // sync-report
	}
	switch flag.Arg(0) {
	case "down":
		clickDown(0, 0)
	case "up":
		clickUp()
	case "click":
		duration, err := time.ParseDuration(flag.Arg(1))
		if err != nil {
			log.Fatal(err)
		}
		clickDown(0, 0)
		time.Sleep(duration)
		clickUp()
	}
}
