# -*- coding: utf-8 -*-
"""ES_Sign.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TVPI3GiLwXFHCB96AG8v9PAYUfTasG8N
"""

import matplotlib.pyplot as plt
import seaborn as sns
from keras.models import Sequential
from keras.layers import Dense, Conv2D , MaxPool2D , Flatten , Dropout , BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix
import pandas as pd
import csv

PATH = "/content/drive/MyDrive/SpanishSignLanguage2"

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
drive.mount('/content/drive')

# %cd PATH
# The following code to be run if it is the first time
#!unzip archive.zip -d archive

# Commented out IPython magic to ensure Python compatibility.
!ls
# %cd drive/MyDrive/SpanishSignLanguage2
# %cd archive

# Commented out IPython magic to ensure Python compatibility.
!ls
# %cd Image

!ls

## Move images into train file, valid & test files
import os
PATH = "/content/drive/MyDrive/SpanishSignLanguage2/archive/Image"

def data_display_count(spath):
  for letter in range(ord('A'), ord('Z') + 1):
      class_folder_name = chr(letter)
      class_folder_path = os.path.join(spath, class_folder_name)
      if os.path.isdir(class_folder_path):
        num_items = len([item for item in os.listdir(class_folder_path) if os.path.isfile(os.path.join(class_folder_path, item))])
        print(f"Class {class_folder_name}: {num_items} items")

data_display_count(PATH)

import shutil
import random

def move_percentage_files(source, destination, percentage):
    files = os.listdir(source)
    num_files_to_move = int(len(files) * percentage)
    files_to_move = random.sample(files, num_files_to_move)

    for file_name in files_to_move:
        source_path = os.path.join(source, file_name)
        destination_path = os.path.join(destination, file_name)
        shutil.move(source_path, destination_path)

TEST_PATH =  "/content/drive/MyDrive/SpanishSignLanguage2/archive/TEST"

for letter in range(ord('A'), ord('Z') + 1):
    class_folder_name = chr(letter)
    class_folder_path = os.path.join(TEST_PATH, class_folder_name)
    os.makedirs(class_folder_path, exist_ok=True)


percentage_to_move = 0.2
for letter in range(ord('A'), ord('Z') + 1):
    class_folder_name = chr(letter)
    source_class_path = os.path.join(PATH, class_folder_name)
    destination_class_path = os.path.join(TEST_PATH, class_folder_name)
    move_percentage_files(source_class_path, destination_class_path, percentage_to_move)

## Data preprocessing before even transformnig all into csv file
print("---------- TRAIN COUNT ---------")
data_display_count(PATH)
print("---------- TEST COUNT ---------")
data_display_count(TEST_PATH)

# Transforming photos into csv format for easily handinling them alongside with label update

from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
import cv2

# horizontal shift
img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data, 0)
datagen = ImageDataGenerator(width_shift_range=[-50,50])
iter = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = iter.next()
  image = batch[0].astype('uint8')
  plt.imshow(image)

plt.show()

def ho_shift(img_path):
  img = load_img(img_path)
  img_dir = os.path.dirname(img_path)
  img_name, img_extension = os.path.splitext(os.path.basename(img_path))
  data = img_to_array(img)
  samples = expand_dims(data, 0)
  datagen = ImageDataGenerator(width_shift_range=[-50,50])
  iter = datagen.flow(samples, batch_size=1)
  for i in range(9):
    batch = iter.next()
    image = batch[0].astype('uint8')
    s_name = f'{img_name}_{i}_augmented_hor.png'
    s_path = os.path.join(img_dir,s_name)
    cv2.imwrite(s_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

# an example to see the data augmentation how it is like
# vertical shifting
img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data,0)
datagen = ImageDataGenerator(height_shift_range=0.5)
iter = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = iter.next()
  image = batch[0].astype('uint8')
  plt.imshow(image)
plt.show()

def vert_shift(img_path):
  img = load_img(img_path)
  img_name, img_extension = os.path.splitext(os.path.basename(img_path))
  img_dir = os.path.dirname(img_path)
  data = img_to_array(img)
  samples = expand_dims(data,0)
  datagen = ImageDataGenerator(height_shift_range=0.5)
  iter = datagen.flow(samples, batch_size=1)
  for i in range(9):
    batch = iter.next()
    image = batch[0].astype('uint8')
    s_name = f'{img_name}_{i}_augmented_vert.png'
    s_path = os.path.join(img_dir,s_name)
    cv2.imwrite(s_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

## Flipping augmentation
# Horizontal
img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data,0)
datagen = ImageDataGenerator(vertical_flip=True)
it = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = it.next()
  image = batch[0].astype('uint8')
plt.imshow(image)

img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data,0)
datagen = ImageDataGenerator(rotation_range=90)
it = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = it.next()
  image = batch[0].astype('uint8')
  plt.imshow(image)
plt.show()

# Random Brightness
img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data,0)
datagen = ImageDataGenerator(brightness_range=[0.2,1.0])
it = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = it.next()
  image = batch[0].astype("uint8")
  plt.imshow(image)
plt.show()

def bright(img_path):
  img = load_img(img_path)
  img_name, img_extension = os.path.splitext(os.path.basename(img_path))
  img_dir = os.path.dirname(img_path)
  data = img_to_array(img)
  samples = expand_dims(data,0)
  datagen = ImageDataGenerator(brightness_range=[0.2,1.0])
  iter = datagen.flow(samples, batch_size=1)
  for i in range(9):
    batch = iter.next()
    image = batch[0].astype("uint8")
    s_name = f'{img_name}_{i}_augmented_bright.png'
    s_path = os.path.join(img_dir,s_name)
    cv2.imwrite(s_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

# Zooming
img = load_img(PATH+"/G/0.png")
data = img_to_array(img)
samples = expand_dims(data,0)
datagen = ImageDataGenerator(zoom_range=[0.5,1.0])
it = datagen.flow(samples, batch_size=1)
for i in range(9):
  plt.subplot(330 + 1 + i)
  batch = it.next()
  image = batch[0].astype('uint8')
  plt.imshow(image)
plt.show()

def zoom(img_path):
  img = load_img(img_path)
  img_name, img_extension = os.path.splitext(os.path.basename(img_path))
  img_dir = os.path.dirname(img_path)
  data = img_to_array(img)
  samples = expand_dims(data,0)
  datagen = ImageDataGenerator(zoom_range=[0.5,1.0])
  iter = datagen.flow(samples, batch_size=1)
  for i in range(9):
    batch = iter.next()
    image = batch[0].astype('uint8')
    s_name = f'{img_name}_{i}_augmented_zoom.png'
    s_path = os.path.join(img_dir,s_name)
    cv2.imwrite(s_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

# Augmentation core engine
!ls
subdirectories = [d for d in os.listdir(PATH) if os.path.isdir(os.path.join(PATH, d))]
for sd in subdirectories:
  sd_path = os.path.join(PATH, sd)
  for image_file in os.listdir(sd_path):
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        image_path = os.path.join(sd_path, image_file)
        ho_shift(image_path)
        vert_shift(image_path)
        bright(image_path)
        zoom(image_path)

data_display_count(PATH)

import tensorflow as tf
def visualize(original, augmented):
    fig = plt.figure()
    plt.subplot(1,2,1)
    plt.title('Original image')
    plt.imshow(original)

    plt.subplot(1,2,2)
    plt.title('Augmented image')
    plt.imshow(augmented)
    flipped = tf.image.flip_left_right(image)
    visualize(image, flipped)

# Augmentation technique on the train