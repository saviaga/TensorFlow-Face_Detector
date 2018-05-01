"""
Download Images from OpenImages dataset
https://storage.googleapis.com/openimages/web/index.html
"""

import json
import os
import random
import requests
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse


def parallel_process(array, function, n_jobs=16, use_kwargs=False, front_num=3):

    if front_num > 0:
        front = [function(**a) if use_kwargs else function(a) for a in array[:front_num]]

    if n_jobs==1:
        return front + [function(**a) if use_kwargs else function(a) for a in tqdm(array[front_num:])]

    with ProcessPoolExecutor(max_workers=n_jobs) as pool:

        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(function, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }

        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []

    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out


def download(element):
    image_content = None
    dir_path = save_directory_path
    browser_headers = [
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704 Safari/537.36"},
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:44.0) Gecko/20100101 Firefox/44.0"}
    ]
    try:
        response = requests.get(element['url'],
                                headers=random.choice(browser_headers),
                                verify=False)
        image_content = response.content
    except:
        pass
    if image_content:
        complete_file_path = os.path.join(dir_path, element['id']+'.'+element['url'].split('.')[-1])
        with open(complete_file_path, "wb") as f:
            f.write(image_content)
            f.close()

parser = argparse.ArgumentParser()
parser.add_argument('--images_path', dest='images_path', required=True)
parser.add_argument('--images_output_directory', dest='images_output_directory', required=True)

if __name__ == "__main__":
    browser_headers = [
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704 Safari/537.36"},
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:44.0) Gecko/20100101 Firefox/44.0"}
    ]
    args = parser.parse_args()
    images_path = args.images_path
    save_directory_path = args.images_output_directory
    try:
        os.makedirs(save_directory_path)
    except OSError:
        pass  # already exists
    with open(images_path, 'rb') as f:

        image_urls = json.load(f)
        print(image_urls)
    parallel_process(image_urls, download)