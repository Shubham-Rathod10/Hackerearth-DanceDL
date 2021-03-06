# -*- coding: utf-8 -*-
"""dance_DL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cOOpQHQKTySF5rW4DbTLqxMjBvAzVxoM

#Link to download the Dataset 
https://www.kaggle.com/raoofnaushad/indian-dance-forms-1000/download

#Importing essential Libraries.
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import zipfile
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img

from tensorflow.keras.layers import Dense,Layer,Lambda,Add,Multiply,Input,Conv2D,MaxPool2D,Flatten,Conv2DTranspose,Reshape,Dropout,GlobalAveragePooling2D
from tensorflow.keras.models import Sequential,Model
import pandas as pd
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input

# %matplotlib inline

"""#Unzipping dataset.(comment this cell once unzipped)"""

dataset_path = "/content/drive/My Drive/Colab Notebooks/danceDS.zip"
zip_object = zipfile.ZipFile(file=dataset_path, mode="r")
zip_object.extractall("./")
zip_object.close()

"""#defining paths to directories."""

dataset_path_new = "/content/dataset"
train_dir = os.path.join(dataset_path_new, "train/")
test_dir = os.path.join(dataset_path_new, "test/")

"""# assigning respective labels."""

train_label = pd.read_csv('/content/dataset/train.csv')
test_label = pd.read_csv('/content/dataset/test.csv')

"""#Mapping the Image with its respective label."""

train_dict = {str(x):y for x,y in zip(train_label['Image'],train_label['target'])}

"""#Loading the Train images in X_train Tensor and creating train labels list y_train."""

names = os.listdir(train_dir)
X_train = np.zeros((1,224,224,3))
y_train = []
for i,x in enumerate(names):
    #print(i)
    im = load_img(train_dir + x,target_size=(224,224))
    arr = np.asarray(im)
    arr = arr.reshape(1,224,224,3)
    X_train = np.concatenate((X_train,arr),axis=0)
    y_train.append(train_dict[x])
    
X_train = preprocess_input(X_train[1:])

"""#Loading the Test Images in X_test Tensor."""

X_test = np.zeros((1,224,224,3))
for i,x in enumerate(test_label['Image']):
    #print(i)
    im = load_img(test_dir + x,target_size=(224,224))
    arr = np.asarray(im)
    arr = arr.reshape(1,224,224,3)
    X_test = np.concatenate((X_test,arr),axis=0)
X_test = preprocess_input(X_test[1:])

"""#Label encoding the dance form names
```
e.g
Manipuri - 0,
Bharatanatyam - 1,
Odissi - 2,
Kathakali - 3,
Kathak - 4,
Sattriya - 5,
Kuchipudi - 6,
Mohiniyattam - 7
```
"""

from sklearn.preprocessing import LabelEncoder
LE = LabelEncoder()
y_tr = LE.fit_transform(y_train)

"""#Fine Tuning with 5 fold cross-validation"""

def create_model():
    IMG_SHAPE = (224, 224, 3)
    fine_tune_at = 160
    base_model = ResNet50(include_top=False,weights='imagenet',input_shape=IMG_SHAPE)
    base_model.trainable = True
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False
    glob_layer = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
    d1 = tf.keras.layers.Dense(units=256,activation='relu')(glob_layer)
    t1 = tf.keras.layers.Dropout(0.3)(d1)
    d2 = tf.keras.layers.Dense(units=128,activation='relu')(t1)
    t2 = tf.keras.layers.Dropout(0.3)(d2)
    prediction_layer = tf.keras.layers.Dense(units=8, activation='softmax')(t2)
    model = tf.keras.models.Model(inputs=base_model.input, outputs=prediction_layer)
    model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.0001), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

"""###Building the Model"""

model = KerasClassifier(build_fn=create_model,epochs=20,batch_size=64,validation_split=0.2)
from sklearn.model_selection import cross_val_score
kfold = cross_val_score(model,X_train,y_tr,cv=5,verbose=1)
print(f'scores list is  = {kfold}')
print(f'mean of the scores is = {kfold.mean()}')
print(f'std dev of score is = {kfold.std()}')

model = create_model()
model.fit(X_train,y_tr,batch_size=128,epochs=50)

"""###Model Summary"""

model.summary()

"""#Model prediction and to_csv writing cell"""

y_pred = model.predict(X_test)
y_pred = np.argmax(y_pred,axis=1)
y_test_lab = LE.inverse_transform(y_pred)

frame = [[x,y] for x,y in zip(test_label['Image'],y_test_lab)]
df = pd.DataFrame(frame,columns=["Image","target"])
letgo = df.to_csv('./pred12.csv',index=False)