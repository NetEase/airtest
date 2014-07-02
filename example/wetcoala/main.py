from airtest import ios


def main():
    d = ios.IosDevice()
    d.click("start.png")
    width, height = d.shape()
    for i in range(10):
        print "retry:", i
        d.drag((width * 0.5, height * 0.5), (width * 0.9, height * 0.5))
        d.drag((width * 0.9, height * 0.5), (width * 0.5, height * 0.5))
        d.drag((width * 0.5, height * 0.5), (width * 0.1, height * 0.5))
        d.wait("gameover.png", interval=2)
        if d.exists("retry.png"):
            d.click("retry.png")


if __name__ == '__main__':
    main()
