# Temperature Sensor Project
# By: Jacob Soria
# Basic Functions
# -Gets temp from sensor in Celsius then converts to Fahrenheit
# -Stores them to get avg temperature
# -Starts web server on port 5000
# -Opens web page which allows you to type how many seconds to take the avg temp from
# -Shows current and avg temp over the second amount chosen by user

import os    # run system commands and pathing
import glob  # finds similar files
import time
import json  # converts py data to JSON (JavaScript Object Notation)

# HTTPServer allows a web server to run
# BaseHTTPRequestHandler handles web requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Sensor functions

#had problems manually typing the w1 therm out so i did this to make sure it always is in there as well as w1-gpi just in case
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#where 1 wire is on pi
base_dir = '/sys/bus/w1/devices/'

#glob used here to find files that have 28* since the sensor starts like this
device_folders = glob.glob(base_dir + '28*')

if len(device_folders) == 0:
    print("No sensor found in", base_dir)
    device_folder = None
    device_file = None
else:
    # use first folder that is found
    device_folder = device_folders[0]
    #reads the w1 slave file inside the folder it found
    device_file = device_folder + '/w1_slave'


def read_temp_raw():
    
    # if no file  found, then cannot read 
    if device_file is None:
        return None

    # opens in read mode
    with open(device_file, 'r') as f:
        lines = f.readlines()

    return lines


def read_temp():
   
    # take raw lines from sensor
    lines = read_temp_raw()

    #shows again if not found then None, None
    if lines is None:
        return None, None

    # strip takes away anything extra in line [0] at the end of the string while -3 asks for the last 3 characters in the string
    tries = 0
    while not lines[0].strip().endswith("YES"):
        
        #time between reading again to verify CRC
        time.sleep(0.2)
        
        lines = read_temp_raw()
        if lines is None:
            return None, None
        #how many times it checks bfore stopping 
        tries += 1
        if tries > 5:
            return None, None

    # Now we look for "t=" in line[1]
    # t is given at a thousandths of a degree in Celsius
    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        
        #takes found t=
        temp_string = lines[1][equals_pos + 2:]
       
       #accounts for if theres bad data
        try:
            # Divide by 1000 to get regular Celsius
            temp_c = float(temp_string) / 1000.0
        except ValueError:
            return None, None

        #C to F calculations
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        return temp_c, temp_f
    else:
        return None, None


# History and Avg Calculations

#makes list for temp data in (time, F) form
readings = []

#amount of seconds of history to keep
HISTORY_SECONDS = 3600  # 1 hour

#gets one reading from sensor and stores it
def add_reading():
    
    #get current temps 
    temp_c, temp_f = read_temp()

    #gets current time
    now = time.time()

    if temp_f is not None:
        
        #adds time,temp_f to readings list
        readings.append((now, temp_f))

        #removes values older than 3600 secs/1hr
        cutoff_time = now - HISTORY_SECONDS
        new_list = []

        #check old readings
        for ts, value in readings:
            if ts >= cutoff_time:
                new_list.append((ts, value))

        #replaces old list with new one
        readings[:] = new_list

        #rounds to 2 decimals places
        temp_rounded = round(temp_f, 2)

        #converts to text
        temp_txt = str(temp_rounded) + "°F"

        print("sample", time.strftime("%H:%M:%S"), temp_txt)
    else:
        print("Couldn't read temp")


#returns most recent temp in F
def get_latest_temperature_f():
    
    if len(readings) == 0:
        return None

    #gets most recent time/temp reading
    ts, temp_f = readings[-1]
    return temp_f


#gets avg of latest temp values 
def get_average_temperature_f(last_seconds):
    
    if len(readings) == 0:
        return None

    now = time.time()
    cutoff_time = now - last_seconds

    #makes list only for this function
    values = []

    for ts, temp_f in readings:
        if ts >= cutoff_time:
            values.append(temp_f)

    # If there are no recent values, no average to compute
    if len(values) == 0:
        return None

    #adds all values
    total = 0.0
    for v in values:
        total += v

    #number of values we have
    count = len(values)

    average = total / count

    return average


# HTML/java Functions

PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Pi Temperature (Fahrenheit)</title>
</head>

<body>

  <!-- Main Title -->
  
  <h1>Raspberry Pi Temperature (°F)</h1>

  <!-- user input section -->
  
  <p>
  
    <!-- where user plugs in desired number -->
    Time window (seconds):

    <!-- type="text" removes arrows that increase/decrease input by one -->
    <!-- gives input a unique id (secondsInput) that is able to be called  -->
    
    <input id="secondsInput" type="text" value="60" />

    <!-- updates user input so that it knows to change paramaters to said input -->
    <button onclick="updateData()">Update</button>
  
  </p>

  <!-- Avg temp section -->
  
  <p>
    <!-- displays this -->
    Average Temperature Over Last
     
    <!-- Shows chosen number of seconds after last -->
    <!-- gives span a unique id (secondsLabel) that is able to be called  -->
    <span id="secondsLabel">60</span>

    <!-- displays this after chosen number of seconds -->
    seconds:

    <!-- holds avg temp value from server -->
    <!-- <strong>.../<strong> makes whatever inside it bold -->
    <!-- gives span a unique id (avgValue) that is able to be called  -->
    <strong><span id="avgValue">--</span> °F</strong>
    
  </p>

  <!-- Current temp section -->
  <p>
    
    Current Temperature right now:
    <!-- span has unique id (currentValue) so JS can update it -->
    
    <strong><span id="currentValue">--</span> °F</strong>
  </p>

  <!-- Javascript for/in the broswer -->
  
  <script>
  
    // reads user input
    // gets avg/current from pi and updates page
    
    function updateData() {
      
      // gets raw text from user input and removes extra spaces
      var raw = document.getElementById("secondsInput").value.trim();

      // makes raw text into number (decimals also work too)
      var seconds = parseFloat(raw);

      // if input is less than <= 0 it will show 60 instead
      if (!isFinite(seconds) || seconds <= 0) {
        seconds = 60;
        
      // resets the input box to show 60
        document.getElementById("secondsInput").value = "60";
      }

      // gets the secondsLabel id var (from the document) and replaces the text with time values from seconds
      document.getElementById("secondsLabel").textContent = seconds;
      

      // url section
      
      // makes variable named url that has the seconds data
      // encodeURIComponent(seconds) covers/includes spaces and sybmols that can be used in the input
      var url = "/api/average?seconds=" + encodeURIComponent(seconds);
      
      //asks pi at for data at /api/average?seconds=
      //then pi sends data back (avg/current temp) in JSON
      fetch(url)
      
        // gets json data and turns it into js
        .then(function(response) {
          return response.json();
        })
        
        // takes values to update page
        .then(function(data) {
          
          // update average temp on page
          
          // defines avg Span
          var avgSpan = document.getElementById("avgValue");
          if (data.average === null) {
            avgSpan.textContent = "no data yet";
          } else {
            avgSpan.textContent = data.average;
          }

          // update current temp
          
          var currentSpan = document.getElementById("currentValue");
          if (data.current === null) {
            currentSpan.textContent = "no data yet";
          } else {
            currentSpan.textContent = data.current;
          }
        });
    }

    // calls updateData() when page loads
    updateData();

    // updateData then runs every 5 seconds (5000 milli secs)
    setInterval(updateData, 5000);
  </script>
</body>
</html>
"""


# HTTP Server functions

# Handles HTTP GET requests from the browser
class TempHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        
        # checks if either of the two are present
        if self.path == "/" or self.path == "/index.html":
            
            # if it does, it will send 200 meaning working, ex: 404 means not found
            self.send_response(200)

            #sends webpage via text/html
            #utf-8 handles special characters
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            #sends to final webpage to the browser
            #utf-8 turns strings to bites
            self.wfile.write(PAGE_HTML.encode("utf-8"))
            
            return

        #sends back JSON data if received
        if self.path.startswith("/api/average"):

            #default if input doesnt work
            seconds = 60.0

            #handles parameters when /api/average?seconds=60
            if "?" in self.path:
                path_part, query_part = self.path.split("?", 1)

                #splits qurey part and defines it as pair 
                pairs = query_part.split("&")

                #checks content of pair
                for piece in pairs:
                    if piece.startswith("seconds="):
                        
                        #value str becomes a string 
                        value_str = piece.split("=", 1)[1]

                        #since value str is still text, this turns it into a number
                        try:
                            seconds = float(value_str)
                            
                            if seconds <= 0:
                                seconds = 60.0
                        except ValueError:
                            seconds = 60.0

            #takes a new reading when browser asks for data          
            add_reading()

            avg_temp = get_average_temperature_f(seconds)
            cur_temp = get_latest_temperature_f()

            #dictionary and its results
            if avg_temp is None and cur_temp is None:
                data = {
                    "average": None,
                    "seconds": seconds,
                    "current": None,
                    "message": "no data yet"
                }
            else:
                avg_value = round(avg_temp, 2) if avg_temp is not None else None
                cur_value = round(cur_temp, 2) if cur_temp is not None else None
               
                # another dictionary and its results
                data = {
                    "average": avg_value,
                    "seconds": seconds,
                    "current": cur_value
                }

            #turns dict values in json text string    
            body = json.dumps(data)

            #sends respones from HTTP back browser in json
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            #sends json text as bytes
            self.wfile.write(body.encode("utf-8"))
            return

        #incase path not found
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found for everyone but Leon")


#Web Server Starting Functions
def run_server():
    
    #makes it visible for other devices on the same network
    host = "0.0.0.0"

    #number for web server
    port = 5000

    server_address = (host, port)

    #makes http server for temphandler
    httpd = HTTPServer(server_address, TempHandler)

    print("Serving on http://{}:{}/".format(host, port))

    #loops forever
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
