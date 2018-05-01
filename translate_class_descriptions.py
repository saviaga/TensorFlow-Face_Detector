"""
After OpenImages dataset is downloaded:
#!/usr/bin/env bash
# downloads and extracts the openimages bounding box annotations and image path files
mkdir data
wget http://storage.googleapis.com/openimages/2017_07/images_2017_07.tar.gz
tar -xf images_2017_07.tar.gz
mv 2017_07 data/images
rm images_2017_07.tar.gz

wget http://storage.googleapis.com/openimages/2017_07/annotations_human_bbox_2017_07.tar.gz
tar -xf annotations_human_bbox_2017_07.tar.gz
mv 2017_07 data/bbox_annotations
rm annotations_human_bbox_2017_07.tar.gz

wget http://storage.googleapis.com/openimages/2017_07/classes_2017_07.tar.gz
tar -xf classes_2017_07.tar.gz
mv 2017_07 data/classes
rm classes_2017_07.tar.gz

We convert everything to JSON 
"""
import csv
import argparse
import json


def class_descriptions_to_JSON(trainable_classes_file, descriptions_file):
    with open(trainable_classes_file, 'r') as file:
        trainable_classes = file.read().replace(' ', '').split('\n')
    description_table = {}
    with open(descriptions_file) as f:
        for row in csv.reader(f):
            if len(row):
                description_table[row[0]] = row[1].replace("\"", "").replace("'", "").replace('`', '')
    output = []
    for elm in trainable_classes:
        if elm != '':
            output.append(description_table[elm])
    return output


def save_classes(formatted_data, translated_path):
    with open(translated_path, 'w+') as f:
        json.dump(formatted_data, f)

parser = argparse.ArgumentParser()
parser.add_argument('--trainable_classes_path', dest='trainable_classes', required=True)
parser.add_argument('--class_description_path', dest='class_description', required=True)
parser.add_argument('--trainable_translated_path', dest='trainable_translated_path', required=True)


if __name__ == '__main__':
    args = parser.parse_args()
    trainable_classes_path = args.trainable_classes
    description_path = args.class_description
    translated_path = args.trainable_translated_path
    translated = class_descriptions_to_JSON(trainable_classes_path, description_path)
    save_classes(translated, translated_path)