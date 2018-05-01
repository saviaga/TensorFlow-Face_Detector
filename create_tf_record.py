"""
This script creates the TF Records that we need for Tensor Flow
"""

import tensorflow as tf
from PIL import Image
import os
from object_detection.utils import dataset_util
import json
import hashlib
import argparse
from tqdm import tqdm


def generate_class_number(points):
    output = []
    with open(trainable_classes_file, 'r') as file:
        trainable_classes = file.read().split('\n')
    for point in tqdm(points):
        for anno in point['annotations']:
            anno['class_num'] = trainable_classes.index(anno['label'])+1
            output.append(anno)
    return output



def create_tf_record(point, image_directory):
    format = b'jpeg'
    xmins = xmaxs = ymins = ymaxs = class_nums = class_ids =[]
    image_id = point['id']
    filename = os.path.join(image_directory, image_id + '.jpg')
    print(filename)
    try:
        image = Image.open(filename)

        width, height = image.size
        print(width,height)
        with tf.gfile.GFile(filename, 'rb') as fid:
            encoded_jpg = bytes(fid.read())
    except:
        return None
    key = hashlib.sha256(encoded_jpg).hexdigest()
    for anno in point['annotations']:
        xmins.append(float(anno['x0']))
        xmaxs.append(float(anno['x1']))
        ymins.append(float(anno['y0']))
        ymaxs.append(float(anno['y1']))
        class_nums.append(anno['class_num'])
        class_ids.append(bytes(anno['label'],'utf8'))
    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
        'image/filename': dataset_util.bytes_feature(bytes(filename,'utf8')),
        'image/source_id': dataset_util.bytes_feature(bytes(image_id,'utf8')),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(class_ids),
        'image/object/class/label': dataset_util.int64_list_feature(class_nums)
    }))
    return tf_example


def load_points(file_path):
    with open(file_path, 'r') as f:
        points = json.load(f)
    return points

parser = argparse.ArgumentParser()
parser.add_argument('--points_path', dest='points_file_path', required=True)
parser.add_argument('--record_save_path', dest='record_save_path', required=True)
parser.add_argument('--trainable_classes_path', dest='trainable_classes_path', required=True)
parser.add_argument('--saved_images_directory', dest='saved_images_directory', required=True)


if __name__ == "__main__":
    args = parser.parse_args()
    trainable_classes_file = args.trainable_classes_path
    record_save_path = args.record_save_path
    points_file = args.points_file_path
    saved_images_directory = args.saved_images_directory
    points = load_points(points_file)
    with_class_num = generate_class_number(points)
    writer = tf.python_io.TFRecordWriter(record_save_path)
    for point in tqdm(points, desc="writing to file"):
        record = create_tf_record(point, saved_images_directory)
        if record:
            serialized = record.SerializeToString()
            writer.write(serialized)
    writer.close()