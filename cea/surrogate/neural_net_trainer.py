from keras.layers import Input, Dense
from keras.models import Model
import numpy as np
import scipy.io
from keras.models import Sequential
from keras.callbacks import EarlyStopping
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
# fix random seed for reproducibility

file_path1='C:\CEAforArcGIS\cea\surrogate\in_ht.csv'
file_path2='C:\CEAforArcGIS\cea\surrogate\Tar_ht.csv'
call_inputs=pd.read_csv(file_path1)
inputs_x=np.array(call_inputs)
call_targets=pd.read_csv(file_path2)
target_t=np.array(call_targets)



def neural_trainer(inputs_x,targets_t):
    np.random.seed(7)


    #scaling and normalizing inputs
    scalerX = MinMaxScaler(feature_range=(0, 1))
    inputs_x=scalerX.fit_transform(inputs_x)
    scalerT = MinMaxScaler(feature_range=(0, 1))
    targets_t=scalerT.fit_transform(targets_t)

    #sparsing inputs
    #input_AEI = Input(shape=(29,))
    #encoded = Dense(29, activation='relu')(input_AEI)
    #encoded = Dense(10, activation='softplus')(encoded)

    #decoded = Dense(29, activation='softplus')(encoded)
    #decoded = Dense(29, activation='linear')(decoded)

    #autoencoder = Model(input_AEI, decoded)
    #autoencoder.compile(optimizer='Adamax', loss='mse')

    inputs_x_rows, inputs_x_cols = inputs_x.shape
    targets_t_rows, targets_t_cols = targets_t.shape
    hidden_units_L1=inputs_x_cols*2
    hidden_units_L2=inputs_x_cols+1
    validation_split = 0.5
    batch_size=(inputs_x_rows*(1-validation_split))+1
    e_stop_limit=10

    # multi-layer perceptron
    model = Sequential()
    model.add(Dense(hidden_units_L1, input_dim=inputs_x_cols, activation='relu')) #logistic layer

    model.add(Dense(hidden_units_L2, activation='relu')) #logistic layer

    model.add(Dense(targets_t_cols, activation='linear')) #output layer

    model.compile(loss='mean_squared_error', optimizer='Adamax') # compile the network

    # define early stopping to avoid overfitting
    estop = EarlyStopping(monitor='val_loss', min_delta=0, patience=e_stop_limit, verbose=1, mode='auto')


    # Fit the model
    model.fit(inputs_x, targets_t, validation_split=validation_split, epochs=1500, shuffle=True, batch_size=100000,callbacks=[estop])


    # predict ourputs
    outputs_t = model.predict(inputs_x)
    resized_outputs_t = scalerT.inverse_transform(outputs_t)
    targets_t

    filter_logic=np.isin(targets_t, 0)
    target_anomalies=np.where(filter_logic)
    anomalies_replacements=np.zeros(len(target_anomalies))
    filtered_outputs_t=np.put(resized_outputs_t,target_anomalies,anomalies_replacements)

    #filtered_outputs_t=np.multiply(resized_outputs_t[:,0], logic)
    out_NN = pd.DataFrame(filtered_outputs_t)
    out_NN.to_csv('netout.csv', index=False, header=False, float_format='%.3f', decimal='.')

neural_trainer(inputs_x,target_t)