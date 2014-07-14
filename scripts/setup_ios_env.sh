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

echo "!!!!!!!!!!WARNING!!!!!!!!!!!!!!"
echo "DONOT run this script with root privilege"
echo "Starting setup ios environment for airtest..."
echo

confirm || exit 1

echo "This may take a long time..."

echo "-------Step 1: installing brew"
ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

echo "-------Step 2: installing a brewed python"
brew tap homebrew/science
brew tap homebrew/python
brew update && brew upgrade
brew install python

echo "-------Step 3: installing appium"
brew install node
npm install -g appium

echo "-------Step 4: installing opencv"
brew install opencv

echo "-------Step 5: installing pillow"
brew install pillow

echo "-------Step 6: adding python environment"
echo 'export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages' >> ~/.bash_profile

echo "-------End: summary"
echo "python: " `which python`
echo "appium: " `appium -h &>/dev/null && echo ok || echo fail`
echo "opencv:" `python -c "import cv2" && echo ok || echo fail`
echo "appium:" `python -c "from PIL import Image" && echo ok || echo fail`