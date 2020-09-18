# -*- coding: utf-8 -*-
"""Covid_Chest_Xray_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mHSNVyLAiO7BAQkHc5PKlYBSt-ibSuw8
"""

from google.colab import drive
drive.mount('/content/drive')

"""Unzip the zip file containing your dataset and metadata"""

!unzip "/content/drive/My Drive/548681_1157383_bundle_archive.zip"

"""Importing the Libraries"""

import pandas as pd
import os
import shutil
import matplotlib.pyplot as plt
import imutils
from imutils import paths
import random

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# rm -rf dataset/train/covid/
# rm -rf dataset/train/normal/
# rm -rf dataset/test/covid
# rm -rf dataset/test/normal
# rm -rf dataset
# mkdir -p dataset/train/covid
# mkdir -p dataset/train/normal
# mkdir -p dataset/test/covid
# mkdir -p dataset/test/normal

dataset_path = './dataset'

covid_dataset_path = './images'

df = pd.read_csv('metadata.csv')
print(df['finding'].value_counts())
print(df['view'].value_counts())
print(df.columns)

# loop over the rows of the COVID-19 data frame to set the training data
count = 0
for (i, row) in df.iterrows():
    # As the dataset is imbalanced sample the data to prevent over fitting.
    #if count > 70:
    #  break
    if row["finding"] == "COVID-19" and row['view'] == 'PA':
        # build the path to the input image file
        imagePath = os.path.sep.join([f"{covid_dataset_path}", row["filename"]])
        print(imagePath)

        if not os.path.exists(imagePath):
            continue
        outputPath = os.path.sep.join([f"{dataset_path}/train/covid", row["filename"]])
        print(outputPath)
        # copy the image
        shutil.copy2(imagePath, outputPath)
     #   count+=1

# loop over the rows of the Normal data frame for setting the training dataset

for (i, row) in df.iterrows():

    if row["finding"] != "COVID-19" and row['view'] == 'PA':
        # build the path to the input image file
        imagePath = os.path.sep.join([f"{covid_dataset_path}", row["filename"]])
        print(imagePath)

        if not os.path.exists(imagePath):
            continue
        outputPath = os.path.sep.join([f"{dataset_path}/train/normal", row["filename"]])
        print(outputPath)
        # copy the image
        shutil.copy2(imagePath, outputPath)

"""Moving a part of the training dataset to the validation dataset"""

basePath = './dataset/train/normal'
imagePaths = list(paths.list_images(basePath))
samples = 15
# randomly sample the image paths
random.seed(50)
random.shuffle(imagePaths)
imagePaths = imagePaths[:samples]

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the filename from the image path and then construct the
    # path to the copied image file
    print(imagePath)
    if os.path.exists(imagePath):
      filename = imagePath.split(os.path.sep)[-1]
      outputPath = os.path.sep.join([f"{dataset_path}/test/normal", filename])

      # cut the image
      shutil.move(imagePath, outputPath)

basePath = './dataset/train/covid'
imagePaths = list(paths.list_images(basePath))
samples = 15
# randomly sample the image paths
random.seed(42)
random.shuffle(imagePaths)
imagePaths = imagePaths[:samples]

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the filename from the image path and then construct the
    # path to the copied image file
    print(imagePath)
    if os.path.exists(imagePath):
      filename = imagePath.split(os.path.sep)[-1]
      outputPath = os.path.sep.join([f"{dataset_path}/test/covid", filename])

      # cut the image
      shutil.move(imagePath, outputPath)

"""View the images"""

def ceildiv(a, b):
    return -(-a // b)

def plots_from_files(imspaths, figsize=(10,5), rows=1, titles=None, maintitle=None):
    """Plot the images in a grid"""
    f = plt.figure(figsize=figsize)
    if maintitle is not None: plt.suptitle(maintitle, fontsize=10)
    for i in range(len(imspaths)):
        sp = f.add_subplot(rows, ceildiv(len(imspaths), rows), i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        img = plt.imread(imspaths[i])
        plt.imshow(img)

from imutils import paths
covid_images = list(paths.list_images(f"{dataset_path}/train/covid"))
normal_images = list(paths.list_images(f"{dataset_path}/train/normal"))
covid_test_images = list(paths.list_images(f"{dataset_path}/test/covid"))
normal_test_images = list(paths.list_images(f"{dataset_path}/test/normal"))
print(len(covid_images), len(covid_test_images))
print(len(normal_images), len(normal_test_images))
plots_from_files(covid_images, rows=5, maintitle="Covid-19 X-ray images")
plots_from_files(normal_images, rows=5, maintitle="Other X-ray images")

"""Importing the libraries"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""Preprocessing the tarining directory and Validation directory"""

train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)
test_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_directory(
        './dataset/train',
        target_size=(224, 224),
        batch_size=20,
        class_mode='binary')
validation_generator = test_datagen.flow_from_directory(
        './dataset/test',
        target_size=(224, 224),
        batch_size=20,
        class_mode='binary')

"""Building the Inception Model"""

!wget --no-check-certificate \
    https://storage.googleapis.com/mledu-datasets/inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5 \
    -O /tmp/inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5

from tensorflow.keras import layers
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.models import Model

weights = '/tmp/inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5'
base_model = InceptionV3(weights=None, input_shape = (224, 224, 3), include_top=False)
base_model.load_weights(weights)

for layer in base_model.layers:
    layer.trainable = False

last_layer = base_model.get_layer('mixed5')
last_output = last_layer.output

end_model = layers.Flatten()(last_output)
end_model = layers.Dropout(0.2)(end_model)
end_model = layers.Dense(units=512, activation='relu')(end_model)
end_model = layers.Dropout(0.2)(end_model)
end_model = layers.Dense(units=1, activation='sigmoid')(end_model)
Inceptionmodel = Model(inputs=base_model.input, outputs=end_model)
Inceptionmodel.summary()

class MyCallback(tf.keras.callbacks.Callback):

  def on_epoch_end(self, epoch, logs={}):
    if logs.get('val_acc') >= 0.90 :
      print("\n Reahed accuracy above 70% ")
      self.model.stop_training = True

"""Fitting your Model"""

from tensorflow.keras.optimizers import Adam
opt = Adam(lr=0.0003, decay=0.0003/10)
Inceptionmodel.compile(optimizer=opt, loss='binary_crossentropy', metrics=['acc'])
hist_model = Inceptionmodel.fit(x=train_generator, validation_data=validation_generator, epochs=15, callbacks=[MyCallback()])

"""Testing on an unseen image"""

import numpy as np
from keras.preprocessing import image

test_image = image.load_img('/content/images/extubation-8.jpg', target_size=(224,224))
test_image = image.img_to_array(test_image)
test_image = np.expand_dims(test_image, axis=0)
result = Inceptionmodel.predict(test_image)
train_generator.class_indices
if result[0][0] == 0:
  print("Covid")
else:
  print("Non-Covid")

"""Visualizing the Simple CNN Model's accuracy curve"""

plt.plot(hist_model.history["acc"])
plt.plot(hist_model.history['val_acc'])
plt.title("model accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epoch")
plt.legend(["Accuracy","Validation Accuracy"])
plt.show()

plt.plot(hist_model.history['loss'])
plt.plot(hist_model.history['val_loss'])
plt.title("model accuracy")
plt.ylabel("Loss")
plt.xlabel("Epoch")
plt.legend(["loss","Validation Loss"])
plt.show()