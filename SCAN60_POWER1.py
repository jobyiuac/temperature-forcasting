# univariate lstm example
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten


#____________________________________________________________________________________________________________________

import http.client
import string
import time

# Set the host and path for the HTTP connection
host="192.168.1.102"
path="/rpc/pot1/read"
Q1=0.0

# Define a function to set voltage based on an input value
def fn_to_set_voltage(input):
        connection = http.client.HTTPConnection(host)  # Establish an HTTP connection to the host
        connection.request("GET", path)       # Send an HTTP GET request to the specified path
        response = connection.getresponse()   # Get the response from the server

        # Construct a new path to set the voltage based on the input
        str1="/rpc/anout/write%"
        input=200+input
        str2=str(input)
        path2= str1+str2
        
        # Send another HTTP GET request to set the voltage
        connection.request("GET", path2)
        print(path2)
        x=float(input)     # Convert input to a float for voltage calculation
        x=x-200
        print("The Power written to heater in percentage is =",x*3.3*3*10)

        # Close the HTTP connection
        connection.close()


# Define a function to read the current temperature
def read_latest_temperature_10times_and_write_to_MASTER_csv():

        temperatures = []  # List to store the temperatures
        for i in range (1,60,1): #220
                connection = http.client.HTTPConnection(host)    # Establish an HTTP connection to the host
                connection.request("GET", path)         # Send an HTTP GET request to the specified path
                response = connection.getresponse()     # Get the response from the server

        
                x1 = response.read().decode()         # Read the response and decode it
                x = float(x1)           # Convert the response to a float and format it
                x = float("{:.3f}".format(x))

                T1 = x * 100      # Perform temperature conversion and formatting
                T1 = float("{:.1f}".format(T1 * 1.030))
                T1=T1+0.7
                print('CREATING TIME SERIES DATASET: TIME STAMPLED REAL-TIME SAMPLES OF CURRENT TEMPERATURE READ and ADDING...  T'+ str(i) +'= ', T1)   # Print the temperature

                temperatures.append(T1) # assign last 10

                time.sleep(1)  # Add a delay if needed


                # Close the HTTP connection (this line is unreachable)
                connection.close()

        
        # Return the temperature value
        return temperatures

temperature_list=[]
 
# Main loop
while True:
        # Call the function to set voltage with an input of 0.0
        fn_to_set_voltage(0.7) #0.5
        time.sleep(1)
        print("set the power to heater and started creating a DATASET of 20 temperatures from sensor at 10 secs interval....")
        # Read the latest temperature 10 times
        temperature_list = read_latest_temperature_10times_and_write_to_MASTER_csv()

        # Print the temperatures
        print("Read temperatures:", temperature_list)

        # Write the temperatures to a CSV file
        with open('MASTER.csv', 'w') as csvfile:
                csvfile.write('data'+ "\n")
                for value in temperature_list:
                        
                        csvfile.write(str(value)+ "\n")
                        #csv_writer.writerow(str(value))

        break
