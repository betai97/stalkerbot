##Stalkerbot

This project was done for an ECE 101 class. It uses a Scribbler 2 robot and an MS Kinect along
with myro, pyOpenNI, OpenNI, and NITE APIs in order to track a person and follow them. In order to 
avoid blocking in the main thread which retrieves the visual data, it encapsulates movements such as 
turning to follow the user into separate threads.The computer used connects to the Scribbler 2 robot
via bluetooth. In order to run the code, it is necessary to install the myro, pyOpenNI, OpenNI, and NITE
APIs.