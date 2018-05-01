"""
# Formats the raw OpenImages csv bounding box
"""

import csv
import json
import argparse
from tqdm import tqdm



def annotations_formatting(annotations_path, trainable_classes_path):
    annotations = []
    cont=0
    ids = []
    with open(trainable_classes_path, 'r') as file:
        trainable_classes = file.read().split('\n')
        print("we will use images from these classes",trainable_classes)

    with open(annotations_path, 'r') as annofile:
        for row in csv.reader(annofile):
            if row[2] in trainable_classes:
                annotation = {'id': row[0], 'label': row[2], 'confidence': row[3], 'x0': row[4],
                              'x1': row[5], 'y0': row[6], 'y1': row[7]}
                annotations.append(annotation)
                ids.append(row[0])
    ids = dedupe(ids)
    return annotations, ids


def dedupe(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def format_images(images_path):
    images = []
    with open(images_path, 'r') as f:
        reader = csv.reader(f)
        dataset = list(reader)
        for row in tqdm(dataset, desc="reformatting image data"):
            image = {'id': row[0], 'url': row[2]}
            images.append(image)
            print(row[2])
    return images


def image_filtering(dataset, ids):
    output_list = []
    for element in tqdm(dataset, desc="only keeps the images we want"):
        if element['id'] in set(ids):
            output_list.append(element)

    return output_list


def save_data(data, out_path):
    with open(out_path, 'w+') as f:
        json.dump(data, f)


def points_maker(annotations):
    by_id = {}
    for anno in tqdm(annotations, desc="groups annotations"):
        if anno['id'] in by_id:
            by_id[anno['id']].append(anno)
        else:
            by_id[anno['id']] = []
            by_id[anno['id']].append(anno)
    groups = []
    while len(by_id) >= 1:
        key, value = by_id.popitem()
        groups.append({'id': key, 'annotations': value})
    return groups


parser = argparse.ArgumentParser()
parser.add_argument('--annotations_input_path', dest='anno_path', required=True)
parser.add_argument('--image_index_input_path', dest='index_in_path', required=True)
parser.add_argument('--point_output_path', dest='point_path', required=True)
parser.add_argument('--image_index_output_path', dest='index_out_path', required=True)
parser.add_argument('--trainable_classes_path', dest='trainable_path', required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    anno_input_path = args.anno_path
    image_index_input_path = args.index_in_path
    point_output_path = args.point_path
    image_index_output_path = args.index_out_path
    trainable_classes_path = args.trainable_path
    annotations, valid_image_ids = annotations_formatting(anno_input_path, trainable_classes_path)
    images = format_images(image_index_input_path)
    points = points_maker(annotations)
    filtered_images = image_filtering(images, valid_image_ids)
    save_data(filtered_images, image_index_output_path)
    save_data(points, point_output_path)