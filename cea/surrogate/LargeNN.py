from keras.layers import Input, Dense
from keras.models import Model
import numpy as np
import scipy.io
from keras.models import Sequential
from keras.callbacks import EarlyStopping
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
# fix random seed for reproducibility
np.random.seed(1)

dataset1 = scipy.io.loadmat('D:\ALL7.mat')
dataset = dataset1['ALL']

X = np.array(dataset[:,0:98],"float32")
T = np.array(dataset[:,98],"float32")

#scaling and normalizing inputs
scalerX = MinMaxScaler(feature_range=(0, 1))
X=scalerX.fit_transform(X)
scalerT = MinMaxScaler(feature_range=(0, 1))
T=scalerT.fit_transform(T)

#sparsing inputs
input_AEI = Input(shape=(29,))
encoded = Dense(29, activation='relu')(input_AEI)
encoded = Dense(10, activation='softplus')(encoded)

decoded = Dense(29, activation='softplus')(encoded)
decoded = Dense(29, activation='linear')(decoded)

autoencoder = Model(input_AEI, decoded)
autoencoder.compile(optimizer='Adamax', loss='mse')


# multi-layer perceptron
model = Sequential()
model.add(Dense(80, input_dim=98, activation='relu')) #logistic layer

model.add(Dense(40, activation='relu')) #logistic layer

model.add(Dense(1, activation='linear')) #output layer

model.compile(loss='mean_squared_error', optimizer='Adamax') # compile the network

# define early stopping to avoid overfitting
estop = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')


# Fit the model
model.fit(X, T, validation_split=0.3, epochs=1500, batch_size=1465380,callbacks=[estop])
#model.fit(X, T, epochs=5000, batch_size=8760)

# predict ourputs
Y = model.predict(X)
Y1 = scalerT.inverse_transform(Y)
Y2=Y1[:,0]

dataset2 = scipy.io.loadmat('D:\ALL7a.mat')
dataset3 = dataset2['ALL']

logic=np.array(dataset3)

real_Y=np.multiply(Y2, logic)
my_y = pd.DataFrame(real_Y)
my_y.to_csv('netout.csv', index=False, header=False, float_format='%.3f', decimal='.')