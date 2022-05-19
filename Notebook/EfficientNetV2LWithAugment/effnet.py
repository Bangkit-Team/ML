# -*- coding: utf-8 -*-
"""EffNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MwL3OMOZK9AGyJEcAoHXSgJSrrs8FT1G
"""

from google.colab import drive
drive.mount('/content/drive',force_remount=True)

!unzip "/content/drive/MyDrive/datasetFoodImage/images.zip" -d "/content/sample_data/data"

import json
import os
import tensorflow as tf
from google.colab import files
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras import Sequential, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, Callback
from tensorflow_hub import KerasLayer
from tensorflow.keras.metrics import Precision,Recall
import math

EfficientV2LPath = 'https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_l/feature_vector/2'

modelCNN = KerasLayer(EfficientV2LPath , trainable = False, input_shape = (250,250,3), name = 'EfficientNet')

def build_model(modelCNN):
  model = Sequential([
    Input(shape=(250,250,3)),
    modelCNN,   
    Dense(108, activation="softmax")
  ])
  model.compile(optimizer='Adam', loss="categorical_crossentropy", metrics=["accuracy", Precision(), Recall()])
  return model

model = build_model(modelCNN)

model.summary()

datagen = ImageDataGenerator(
    rotation_range=90,
    zoom_range=0.3,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1,
    rescale = 1./255,
    validation_split=0.1)

valdatagen = ImageDataGenerator(
    rescale = 1./255,
    validation_split=0.1)

train_data_generator = datagen.flow_from_directory(
    "/content/sample_data/data/images",
    target_size=(250,250),
    seed=123,
    subset='training'
)

valid_data_generator = valdatagen.flow_from_directory(
    "/content/sample_data/data/images",
    seed = 123,
    target_size=(250,250),
    subset='validation'
)

freq = 91064/32

checkpoint = ModelCheckpoint("/content/drive/MyDrive/models/EffnetWithAugment_{epoch:02d}_{accuracy:.2f}.h5", verbose=1, mode='auto', save_freq=2846)

class myCallback(Callback):
  def on_epoch_end(self, epoch, logs={}):
    path = '/content/drive/MyDrive/models/trainingHistoryEfficientNet.json'
    with open(path) as f:
      data = json.load(f)
    os.remove(path)
    dictLogs = {
        'loss': logs.get('loss'),
        'accuracy': logs.get('accuracy'),
        'val_loss': logs.get('val_loss'),
        'val_accuracy': logs.get('val_accuracy'),
        'val_precision': logs.get('val_precision_3'),
        'val_recall': logs.get('val_recall_3'),
        'recall': logs.get('recall_3'),
        'precision': logs.get('precision_3')
    }
    data.append(dictLogs)
    json_object = json.dumps(data, indent = 4)
    with open(path, "w") as outJson:
      outJson.write(json_object)

callbacks = myCallback()

model.fit(train_data_generator, validation_data=valid_data_generator, epochs=3,callbacks=[checkpoint, callbacks])

model.evaluate(valid_data_generator)