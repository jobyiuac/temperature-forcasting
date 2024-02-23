
# import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import http.client
import string
import time



from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten

import SCAN60_POWER1


host="192.168.1.102"
path="/rpc/pot1/read"
temperatures = [] 

def read_latest_temperature(counter=[0]):

        #temperatures = []  # List to store the temperatures
                counter[0]+=1 

                connection = http.client.HTTPConnection(host)    # Establish an HTTP connection to the host
                connection.request("GET", path)         # Send an HTTP GET request to the specified path
                response = connection.getresponse()     # Get the response from the server

        
                x1 = response.read().decode()         # Read the response and decode it
                x = float(x1)           # Convert the response to a float and format it
                x = float("{:.3f}".format(x))

                T1 = x * 100      # Perform temperature conversion and formatting
                T1 = float("{:.1f}".format(T1))#T1 = float("{:.1f}".format(T1 * 1.030))
                T1=T1+0.7 #T1=T1+0.7
                #c=1
                
                print('reading real temperature one by one  and trying to see mataching with forcasted graph '+str(counter)+ "Tread="+str(T1))
                
                

                time.sleep(1)  # Add a delay 


                # Close the HTTP connection 
                connection.close()
                
        
                # Return the temperature value
                return(T1)



# Read csv file
data_csv = pd.read_csv('MASTER.csv')# load the csv data
timeseries_data = data_csv[['data']].values # assigning the pandas data to a variable
#print('timeseries_data*10: ',timeseries_data*10)





# preparing independent and dependent features
def prepare_data(timeseries_data, n_features): 
	X, y =[],[]
	for i in range(len(timeseries_data)):    # number of loop 'i' ranges between 0 to length of time series data
		# find the end of this pattern
		end_ix = i + n_features
		# check if we are beyond the sequence
		if end_ix > len(timeseries_data)-1:

			break
		
		# gather input and output parts of the pattern
		seq_x, seq_y = timeseries_data[i:end_ix], timeseries_data[end_ix]
		X.append(seq_x)
		y.append(seq_y)
		print('row: ', i,'x: ', seq_x,'y: ', seq_y)	
	return np.array(X), np.array(y)


# choose a number of time steps
n_steps = 9 # windows value

# split into samples
X, y = prepare_data(timeseries_data, n_steps)
#print('\n jobyX: ', X),print('joby y: ', y)

# reshape from [samples, timesteps] into [samples, timesteps, features]
n_features = 1
X = X.reshape((X.shape[0], X.shape[1], n_features)) # Reshape data into 3D for lstm processing
print('\n reshape: ', X)
print('X.shape', X.shape)

# Building LSTM Model________________________________________________________
# define model
model = Sequential()
model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps, n_features)))
model.add(LSTM(50, activation='relu'))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# fit model
model.fit(X, y, epochs=300, verbose=1)


#Using model for prediction_____________________________________________________
# Predicting For the next 10 data

x_input = timeseries_data[-9:]
# x_input will contain last 10  temperature values in x[50]....x[59] 
temp_input = list(x_input.ravel()) # Converting dimesion of numpy array from 2D to 1D using function ravel

lst_output=[] # createing an empty list to store the "predicted output value"

    
i = 0            
while(i<20): #50  # loop for collecting 10 predicted value in the list: "lst_output=[]"
    x_input=np.array(temp_input[-9:])
    # on first iteration x_input will be copied with all temp_input last 10  values
    x_input = x_input.reshape((1, n_steps, n_features))
    # reshaped and sent all last 10 values for for prediction
    yhat = model.predict(x_input, verbose=0)
    #predicts first value in first iteration from a group of 10 samples od x_input            
    temp_input.append(yhat[0][0])
    #inserts predicted value into first element i.e index 0,0 of temp_input
    #temp_input=temp_input[1:]
    # temp_input is copied with last 10 values of temp_input doesnt make sense
    
               
    lst_output.append(yhat[0][0])
    # 1st_output is appended with latest prediction 20 times     
    i=i+1
            
    print('lst_output: ',lst_output)
    # 1st_output conatins 20 predicted values 

 # For plot: Creating a variable to extend the X-Axis to a new value after each loop 
         
"""### Visualizaing The Output"""
plt.figure()
plt.plot(timeseries_data,  color='b', label = 'DATASET') #label='original data',
plt.plot(range(60,80),lst_output,  color = 'r', label='Forecasted 50 temperature in degC') #(18,28)# range(110,210), label='predicted value',
        

    
new_plot_Xaxis_length = 20

for ii in range(len(lst_output)):
    x_coord = ii + new_plot_Xaxis_length  # X-coordinate for plt.text()
    y_coord = lst_output[ii]  # Y-coordinate for plt.text()
    plt.text(x_coord+(ii*10), y_coord, f'{lst_output[ii]:.1f}',fontsize=8, ha='right', va='bottom')
    plt.xlabel('Time in seconds')
    plt.ylabel('Temperature in degC')
    plt.title(label=' Real Time Temperature Forecasting ', fontsize = 25, color='green', loc='center')
                
    plt.legend()
        

        
for iii in range(20): #(len(lst_output)):
    temperatures.append(read_latest_temperature())
    print("predicted Temperature at this point  was.............................................."+str(lst_output[iii]))
    print("\n")
                

plt.figure()
plt.plot(timeseries_data,  color='b', label = 'DATASET') #label='original data',
plt.plot(range(60,80),lst_output,  color = 'r', label='Forecasted 50 temperature in degC') #(18,28)# range(110,210), label='predicted value',
plt.plot(range(60,80),temperatures, color='g', label = 'Real 50 temperature')
plt.title(label='Deep Learning for Real Time Temperature Forecasting -Heater Heat transfer forcasting ', fontsize = 20, color='green', loc='center')
plt.xlabel('Time in seconds')
plt.ylabel('Temperature in degC')
        
plt.legend()
plt.show()
       

   
        
