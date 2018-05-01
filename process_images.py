"""
Dimensionality reduction of images
"""

import json
from PIL import Image
import os
import argparse
from tqdm import tqdm



def load_images_dataset(file_path):
    with open(file_path, 'rb') as f:
        annotations = json.load(f)
    return annotations


def save_images_dataset(data, file_path):
    with open(file_path, 'w+') as f:
        json.dump(data, f)


def process_images(saved_images_path, resized_images_path, points):
    cleaned_points = []
    for point in tqdm(points, desc="checking if images are valid"):
            try:
                stored_path = os.path.join(saved_images_path, point['id'] + '.jpg')
                im = Image.open(stored_path)
                im.verify()
                im.close()
                im = Image.open(stored_path)
                im.thumbnail((256, 256))
                if resized_images_path:
                    resized_path = os.path.join(resized_images_path, point['id'] + '.jpg')
                    im.save(resized_path, 'JPEG')
                else:
                    os.remove(stored_path)
                    im.save(stored_path, 'JPEG')
                cleaned_points.append(point)
            except:
                pass
    return cleaned_points

parser = argparse.ArgumentParser()
parser.add_argument('--image_directory', dest='image_directory_path', required=True)
parser.add_argument('--image_saving_directory', dest='resized_directory_path')
parser.add_argument('--datapoints_input_path', dest='datapoints_input_path', required=True)
parser.add_argument('--datapoints_output_path', dest='datapoints_output_path', required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    images_directory = args.image_directory_path
    resized_directory = args.resized_directory_path
    points_input_path = args.datapoints_input_path
    points_save_path = args.datapoints_output_path
    points = load_images_dataset(points_input_path)
    filtered_points = process_images(images_directory, resized_directory, points)
    save_images_dataset(filtered_points, points_save_path)