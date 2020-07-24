# import required packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, SimpleRNN, LSTM, GRU
from sklearn import preprocessing
from keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow as tf
from sklearn.preprocessing import Normalizer

# YOUR IMPLEMENTATION
# Thoroughly comment your code to make it easy to follow
def import_and_clean():
    # I had to inlcude the separation option because of white spaces in the titles
    data = pd.read_csv("data/q2_dataset.csv",sep=r'\s*,\s*')
    
    # extract data from pandas dataframe
    volume = data['Volume'].values
    target = data['Open'].values
    high = data['High'].values
    low = data['Low'].values
    
    # flip data so it's old -> recent
    volume = np.flip(volume, 0)
    target = np.flip(target, 0)
    high = np.flip(high, 0)
    low = np.flip(low, 0)
    
    
    # build dataset
    n_days = 3 # 3 days
    X = []
    y = []
    for i in range(len(target)-n_days):
      temp=[] # temporary array
      for j in range(n_days):    
          # concatenate data row wise
          temp.append([volume[i+j], target[i+j], high[i+j], low[i+j]])
      # add features and labels
      X.append(np.ravel(temp))
      y.append(target[i+ n_days])
    
    # convert to numpy array
    X = np.asarray(X)
    y = np.asarray(y)
    
    
    # split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # save data into csv format
    np.savetxt('data/train_data_RNN.csv', np.column_stack((X_train, y_train)), delimiter=',')
    np.savetxt('data/test_data_RNN.csv', np.column_stack((X_test, y_test.T)), delimiter=',')


# load data from the two files generated by the student
def import_and_preprocess_data():
    # load training data
    temp = np.loadtxt(open("data/train_data_RNN.csv", "rb"), delimiter=',')
    X_train = temp[:,:-1]
    y_train = temp[:,-1]
    
    # perform pre-processing on the data 
    # standardize data to remove "units"
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    
    # reshape data n_days = 3, n_features = 4
    n_days = 3
    n_features = 4
    X_train = np.reshape(X_train,(len(X_train), n_days, n_features))
    
    # normalize labels so the loss is easier to understand
    y_train = y_train.reshape(-1, 1)
    y_train = preprocessing.MinMaxScaler().fit(y_train).transform(y_train)
    
    
    return X_train, y_train


# build the model and return its object as well as early stopping criteria
def build_model():
    # SimpleRNN model
    n_days = 3
    n_features = 4
    
    # build the Sequential() model using the keras api
    # see report for design decisions
    model = Sequential()
    model.add(GRU(units=64, input_shape=(n_days, n_features), activation="relu"))
    model.add(Dense(32, activation="relu")) 
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    print(model.summary())
    
    # save the best model
    checkpoint_path="models/20607230_RNN_model.h5"
    keras_callbacks   = [
          EarlyStopping(monitor='val_loss', patience=50, mode='min', min_delta=0.0001),
          ModelCheckpoint(checkpoint_path, monitor='val_loss', save_best_only=True, mode='min')
    ]
        
    return model, keras_callbacks


# plot model history during training 
def plot_loss(history, img_name):

  loss = history.history['loss']
  val_loss = history.history['val_loss']
  epochs = range(1, len(loss)+1)


  # loss history
  plt.figure()
  plt.plot(epochs, loss, label='Training loss')
  plt.plot(epochs, val_loss, label='Validation loss')
  plt.xlabel('epoch')
  plt.ylabel('loss')
  plt.legend()
  plt.title(img_name)
  plt.savefig('loss_'+img_name+'.png')
  plt.show()


# ran into some memory issues so i had to do this
def gpu_settings():
    
    try:
        physical_devices = tf.config.list_physical_devices('GPU')
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
    except:
        pass

if __name__ == "__main__": 
    # fixes gpu memory issues (if any)
    # please comment if this gives you an issue as Ive used tf2
    # I tried to keep the code flexible so it doesnt fail with tf1
    gpu_settings()
	# 1. load your training data
    # import the original file and build dataset
    # uncomment the line below if you want to load the original csv
    # import_and_clean()
    # import the clean dataset
    X_train, y_train = import_and_preprocess_data()
    
    
	# 2. Train your network
    model, callback = build_model()
    # set early stopping criteria so I can place a very high epoch number without
    # worrying about overfitting
    history = model.fit(X_train, y_train, validation_split = 0.2, epochs=1000,
                        batch_size=256, verbose = 1, callbacks=callback)
    
    # plot history  
    # uncomment if you're interested in viewing loss history
    # plot_loss(history, '64_RNN_units')
    

    print('Final Normalized Training Loss:')
    # please note I save the model with the lowest validation loss
    # This is why I find the training loss of the epoch with the lowest 
    # validation loss
    print(history.history['loss'][np.argmin(history.history['val_loss'])])
    
	# 3. Save your model
    # model is automatically saved through the callback early stopping criteria