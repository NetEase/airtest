#!/bin/bash

confirm () {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case $response in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}


is_in_brew() {
    brew ls --versions $1 &>/dev/null && true || false
}

echo "!!!!!!!!!!WARNING!!!!!!!!!!!!!!"
echo "DONOT run this script with root privilege"
echo "Starting setup ios environment for airtest..."
echo

confirm || exit 1

echo "This may take a long time..."

echo "-------Step 1: installing brew"
brew -v &>/dev/null && echo "brew already installed...skiping..." || ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo "-------Step 2: installing a brewed python"
brew tap homebrew/science
brew tap homebrew/python
brew update && brew upgrade
is_in_brew python && echo "brewed python already installed...skiping..." ||  brew install python

echo "-------Step 3: installing appium"
is_in_brew node && echo "node already installed...skiping..."  || brew install node
appium -v &>/dev/null && echo "appium already installed...skiping..."  ||  npm install -g appium

echo "-------Step 4: installing opencv"
is_in_brew opencv && echo "opencv already installed...skiping..." || brew install opencv

echo "-------Step 5: installing pillow"
is_in_brew pillow && echo "pillow already installed...skiping..." ||brew install pillow

echo "-------End: summary"
echo "python: " `which python`
echo "appium: " `appium -h &>/dev/null && echo ok || echo fail`
echo "opencv:" `python -c "import cv2" && echo ok || echo fail`
echo "appium:" `python -c "from PIL import Image" && echo ok || echo fail`
