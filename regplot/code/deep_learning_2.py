
# coding: utf-8

# ## Review
# 
# 

# In[5]:


# keeps warnings from printing for nicer blog output
import warnings 
warnings.filterwarnings('ignore') 

import os

import numpy as np

from keras.models import Sequential, load_model
from keras.layers import Permute, Reshape, LSTM, Dropout, TimeDistributed, Dense, Activation, Flatten
from keras import optimizers

from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import CSVLogger, EarlyStopping, TensorBoard


# In[6]:


# keras callbacks
csv_logger = CSVLogger('epoch-log2.csv', append=True, separator=';')
early_stopper = EarlyStopping(monitor='val_loss',
                              min_delta=0,
                              patience=2,
                              verbose=0, mode='auto')
tensor_board = TensorBoard(log_dir='./tf-log', histogram_freq=0,
                          write_graph=True, write_images=False)


# In[3]:


os.chdir(os.path.expanduser('~/share/rkingdc-blog/regplot'))


# ## Building the Model
# 
# 

# In[4]:


input_dim1 = 256
lstm_size = 150
hidden_layer_size = 100
adam_parms = {'lr': 1e-4, 'beta_1': 0.9, 'beta_2': 0.999}

mod = Sequential()

mod.add(Permute((2,1,3), input_shape=(input_dim1,input_dim1,3)))
mod.add(Reshape(target_shape = (input_dim1,input_dim1*3)))

# our hidden layers
mod.add(LSTM(lstm_size, return_sequences=True))
mod.add(LSTM(lstm_size, return_sequences=True))

# dropout 
mod.add(Dropout(0.5))

mod.add(TimeDistributed(Dense(hidden_layer_size), input_shape=(input_dim1, lstm_size) ))

mod.add(Flatten())

mod.add(Dense(4, activation='softmax'))

mod.compile(optimizer=optimizers.Adam(**adam_parms), loss='categorical_crossentropy', metrics=['accuracy'])
mod.summary()


# ## Pre-procesing Data
# 
# In image processing we'll want to pre-proccess our images before we train a model on them, by adding some random stretching, blurring, rotating, etc. Keras has utilities included to make this easier. 

# In[7]:


train_gen = ImageDataGenerator(rescale = 1/255)
test_gen = ImageDataGenerator(rescale = 1/255)


# In[8]:


train = train_gen.flow_from_directory('data/imgs/train2',
                                      shuffle=True,
                                      batch_size=50,
                                      class_mode='categorical')
test = test_gen.flow_from_directory('data/imgs/test2',
                                    shuffle=True,
                                    batch_size=50,
                                    class_mode='categorical')


# In[15]:


mod.fit_generator(train,
       epochs=15,
       verbose=1,
       validation_data=test,
       callbacks=[csv_logger, early_stopper, tensor_board])


# In[9]:


from datetime import date
mod.save(f'trained_model_2_{str(date.today())}.h5')


# In[11]:


model_eval = mod.evaluate_generator(test, use_multiprocessing=True, workers=3)
print(mod.metrics_names)
print(model_eval)

