#!/usr/bin/env python3


"""
Convert dataset to PASCAL XML


"""
import cv2
import os
import numpy as np
from glob import iglob # python 3.5 or newer
from shutil import copyfile
import xml.etree.cElementTree as ET

def createXMLPASCALfile(imageheight, imagewidth, path, basename):
    annotation = ET.Element("annotation", verified="yes")
    ET.SubElement(annotation, "folder").text = "images"
    ET.SubElement(annotation, "filename").text = basename
    ET.SubElement(annotation, "path").text = path
    source = ET.SubElement(annotation, "source")
    ET.SubElement(source, "database").text = "test"
    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(imagewidth)
    ET.SubElement(size, "height").text = str(imageheight)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(annotation, "segmented").text = "0"
    tree = ET.ElementTree(annotation)

    return tree

def appendXMLPASCAL(curr_et_object,x1, y1, w, h, filename):
    et_object = ET.SubElement(curr_et_object.getroot(), "object")
    ET.SubElement(et_object, "name").text = "face"
    ET.SubElement(et_object, "pose").text = "Unspecified"
    ET.SubElement(et_object, "truncated").text = "0"
    ET.SubElement(et_object, "difficult").text = "0"
    bndbox = ET.SubElement(et_object, "bndbox")
    ET.SubElement(bndbox, "xmin").text = str(x1)
    ET.SubElement(bndbox, "ymin").text = str(y1)
    ET.SubElement(bndbox, "xmax").text = str(x1+w)
    ET.SubElement(bndbox, "ymax").text = str(y1+h)
    filename = filename.strip().replace(".jpg",".xml")
    curr_et_object.write(filename)
    return curr_et_object

def readAndWrite(bbx_gttxtPath,Train_path):
    cnt = 0
    with open(bbx_gttxtPath, 'r') as f:
        curr_filename = ""
        curr_path = ""
        img = np.zeros((80, 80))
        for line in f:
            inp = line.split(' ')

            if len(inp)==1:
                img_path = inp[0]
                img_path = img_path[:-1]
                curr_img = img_path
                if curr_img.isdigit():
                    continue
                img = cv2.imread(Train_path + '/' + curr_img, 2) # POSIX only
                curr_filename = curr_img.split("/")[1].strip()
                curr_path = os.path.join(Train_path, os.path.dirname(curr_img))

            else:
                inp = [int(i) for i in inp[:-1]]
                x1, y1, w, h, blur, expression, illumination, invalid, occlusion, pose = inp
                n = max(w,h)
                if invalid == 1 or blur > 0 or n < 50:
                    continue
                img2 = img[y1:y1+n, x1:x1+n]
                img3 = cv2.resize(img2, (80, 80))
                vec = hog.compute(img3)
                cnt += 1
                fileNow = os.path.join(curr_path,curr_filename)
                print("{}: {} {} {} {}".format(len(vec),x1, y1, w, h) + " " + fileNow)


def runScriptForData(folder,graphfolder,graphtxt,tfimagefolder):
    # get images
    Train_path = os.path.join(curr_path, "data",folder, "images")
    bbx_gttxtPath = os.path.join(curr_path, "data", graphfolder,graphtxt)
    readAndWrite(bbx_gttxtPath,Train_path)
    # save in folders
    to_xml_folder = os.path.join(curr_path, "data",tfimagefolder , "annotations", "xmls")
    to_image_folder = os.path.join(curr_path, "data",tfimagefolder, "images")

    try:
        os.makedirs(to_xml_folder)
        os.makedirs(to_image_folder)
    except Exception as e:
        pass

    rootdir_glob = Train_path + '/**/*'
    file_list = [f for f in iglob(rootdir_glob, recursive=True) if os.path.isfile(f)]
    train_annotations_index = os.path.join(curr_path, "data", tfimagefolder, "annotations", "train.txt")
    with open(train_annotations_index, "a") as indexFile:
        for f in file_list:
            if ".xml" in f:
                print(f)
                copyfile(f, os.path.join(to_xml_folder, os.path.basename(f)))
                img = f.replace(".xml", ".jpg")
                copyfile(img, os.path.join(to_image_folder, os.path.basename(img)))
                indexFile.write(os.path.basename(f.replace(".xml", "")) + "\n")


if __name__=="__main__":
    curr_path = os.getcwd()
    cnt = 0
    hog = cv2.HOGDescriptor((80, 80), (16, 16), (8,8), (8,8), 9)


    runScriptForData("WIDER_val_images", "wider_face_split", "wider_face_val_bbx_gt.txt", "tf_wider_val_images")

    runScriptForData("WIDER_train_images", "wider_face_split", "wider_face_train_bbx_gt.txt", "tf_wider_train_images")
