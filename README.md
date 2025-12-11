Build/Wiring:

![example image](IMG_6353.HEIC)

(command click images to open in other tab)

I was able to mostly follow the posted tutorial for wiring the temp sensor except for the resistor. I just had to replace the 4.7k resistor with a 1k one for a stronger pull up/power connect

Code Installation:
For code installation, you just need to download the file and wire the pi/enable w1.
Important Function Flow Charts

Flowchart 1/2:

![example image](IMG_6350.heic)

The first flowchart on top shows the general functions of the code

First the sensor takes the sends and processes it via python. Then it sends that data to the http server containing the temp handler. Then, it sends that data to the browser where it's
converted to html/java for the browser to show the data. It then loops this forever.

The second flowchart on the bottom shows the temperature sensor overflow

The add reading list gets the raw data from the censor, where it's then checked for w1 slave needing "28..." at the beginning to function. Since data it finds is in milli celcius,  it then is converted to fahrenheit. Then checks and puts new data into reading replacing old data.

Flowchart 3/4

![example iamge](IMG_6349.heic)

The flowchart on top shows the http/api workflow

The third flowchart shows the http/api workflow

The browser calls GET /api/avg, the data is then split by the parse string. This new data is then added to the list. Then it gets the avg/current temp and evaluates it by the dictionary values. It is then sent back to update the browser through javascript 



The flowchart on the bottom shows the html/Javascript workflow

The page first loads the browser, which starts the updateData function. This then evaluates if the data points are valid.If they are, it runs the "/api/avg/..." function that then updates the avg temp.






