import os
import cv2
import numpy as np
from keras.preprocessing.image import ImageDataGenerator

# Define data directories
data_directory = 'data'  # Specify the path to your data directory
victory_sign_folder = os.path.join(data_directory, 'victory sign')
no_victory_sign_folder = os.path.join(data_directory, 'no victory sign')

# Ensure the output augmented data directory exists
output_directory = os.path.join(data_directory, 'augmented_data')
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Augmentation parameters
batch_size = 32  # Number of images to generate at a time
target_size = (224, 224)  # Target size for the images
class_mode = 'binary'  # For two classes

# Image data generator for augmentation
datagen = ImageDataGenerator(
    rescale=1.0 / 255,  # Rescale pixel values to [0, 1]
    rotation_range=40,  # Degree range for random rotations
    width_shift_range=0.2,  # Fraction of total width for random horizontal shift
    height_shift_range=0.2,  # Fraction of total height for random vertical shift
    shear_range=0.2,  # Shear intensity (shear angle in radians)
    brightness_range=[0.2,1.2],
    zoom_range=0.2,  # Random zoom range
    horizontal_flip=True,  # Randomly flip inputs horizontally
    fill_mode='nearest'  # Strategy for filling in newly created pixels
)

# Generate augmented images and save to output directory
generator = datagen.flow_from_directory(
    data_directory,
    target_size=target_size,
    batch_size=batch_size,
    class_mode=class_mode,
    save_to_dir=output_directory,  # Save augmented images to this directory
    save_prefix='augmented',
    save_format='jpeg'  # Save images as JPEG files
)

# Determine the number of batches to generate (assuming an arbitrary number of steps)
num_batches = 100

# Generate augmented images
for i in range(num_batches):
    batch = generator.next()

# Note: You can adjust the number of batches and augmentation parameters based on your requirements
