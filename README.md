Build/Wiring
![example image](IMG_6353.HEIC)
I was able to mostly follow the posted tutorial for wiring the temp sensor except for the resistor. I had to replace the 4.7k resistor with a 1k one for a stronger pull up/power connect

Code Installation
For code installation, you just need to dowloand the file, wire the pi/enable w1 and thats all.
Important Function Flow Charts

![example image](IMG_6350.heic)
The first flowchart on top shows the general functions of the code

First the sensor takes the sends and processes it via python. Then it sends that data to the http server containing the temp handler. Then, it sends that data to the browser where it's
converted to html/java for the browser to show the data. It then loops this forever.

The second flowchart on the bottom shows the temperature sensor overflow

The add reading list gets the raw data from the censor, where it's then checked for w1 slave needing "28..." at the beginning to function. Since data it finds is in milli celcius,  it then is converted to fahrenheit. Then checks and puts new data into reading replacing old data.

![example iamge](IMG_6349.heic)

The flowchart on top shows the http/api workflow




