from keras.layers import Input, Dense
import numpy as np
import scipy.io
from keras.models import Sequential
from keras.callbacks import EarlyStopping
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# fix random seed for reproducibility
np.random.seed(1)

dataset1 = scipy.io.loadmat('D:\ALL5.mat')
dataset = dataset1['ALL']

X = np.array(dataset[:,0:10],"float32")
T = np.array(dataset[:,10],"float32")

scalerX = MinMaxScaler(feature_range=(0, 1))
X=scalerX.fit_transform(X)
scalerT = MinMaxScaler(feature_range=(0, 1))
T=scalerT.fit_transform(T)





model = Sequential()
model.add(Dense(40, input_dim=10, activation='relu')) #logistic layer

model.add(Dense(20, activation='relu')) #logistic layer

model.add(Dense(1, activation='linear')) #output layer

model.compile(loss='mean_squared_error', optimizer='Adamax') # compile the network

# define early stopping to avoid overfitting
estop = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')


# Fit the model
model.fit(X, T, validation_split=0.1, epochs=5000, batch_size=8760,callbacks=[estop])
#model.fit(X, T, epochs=5000, batch_size=8760)

# predict ourputs
Y = model.predict(X)
Y1 = scalerT.inverse_transform(Y)
Y2=Y1[:,0]
logic=np.array(dataset[:,8])

real_Y=np.multiply(Y2, logic)
my_y = pd.DataFrame(real_Y)
my_y.to_csv('netout.csv', index=False, header=False, float_format='%.3f', decimal='.')