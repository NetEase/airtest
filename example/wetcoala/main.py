from airtest import ios


def main():
    d = ios.IosDevice()
    d.click("start.png")
    for i in range(10):
        print "retry:", i
        d.drag((160, 300), (290, 300))
        print d.exists("retry.png")
        d.drag((290, 300), (160, 300))
        d.drag((160, 300), (30, 300))
        d.wait("retry.png", interval=2)
        if d.exists("retry.png"):
            d.click("retry.png")


if __name__ == '__main__':
    main()
