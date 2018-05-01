"""
Convert XML to CSV
"""

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def convert(folder,file):
    image_path = os.path.join(os.getcwd(), 'data', folder, 'annotations','xmls')
    xml_df = xml_to_csv(image_path)
    labels_path = os.path.join(os.getcwd(), 'data', folder,file)
    xml_df.to_csv(labels_path, index=None)
    print(folder, 'Successfully converted xml to csv.')

if __name__=="__main__":
    convert("tf_wider_train_images",'train.csv')
    convert("tf_wider_val_images", 'val.csv')


