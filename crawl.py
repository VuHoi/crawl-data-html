import copy
import time
import csv
import json
import datetime
from slugify import slugify
import requests

from urllib.request import urlopen
from parsel import Selector

import settings

import boto3
aws_credentials = settings.aws_credentials
s3 = {
    's3_client': boto3.client('s3', **aws_credentials),
    'bucket': settings.aws_bucket
}

def get_template_line():
     # Read data that needs processing from CSV files
    template = []
    with open('template.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            template.append(row)

    return template[0]

images=[]
names=[]
def get_product_page(page):
    print('Fetching page {}...'.format(page))
    response = requests.get(settings.products_url + 'page/{}'.format(page)+'/?s=1+'+'&post_type=product')
    selector = Selector(response.text)
    container= selector.css('div.products > div.product-small')
    img= container.css('div.box-image')
    img1= img.css('a>img:first-child')
    
    images = img1.xpath('./@src').getall()
    text = container.css('div.box-text')
    names = text.xpath('.//a/text()').getall()
    # price =  text.css('span.price')
    # print(price.xpath('.//span/text()').getall())
    # return page 
    return (images,names)


template_line = get_template_line()
parent_data = copy.deepcopy(template_line)
fieldnames = template_line.keys()


with open('import.csv', 'w', newline='\n') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    page = 1
    products = get_product_page(page)
    print(len(products[0]),len(products[1]))
    # print(products[0],products[1])
    while products[0]:
        
        i=0
        while(i<len(products[0])):
        # for image in products[0]:
            try:
                req_for_image = requests.get(products[0][i], stream=True)
                image_object_from_req = req_for_image.raw

                image_name = products[0][i].split('/')[-1].split('?')[0]
                image_key = slugify(image_name.split('.')[0]) + '.' + image_name.split('.')[1]
                # s3['s3_client'].upload_fileobj(image_object_from_req, s3['bucket'], image_key)
                image_link = 'https://{}.s3.amazonaws.com/{}'.format(s3['bucket'], image_key)
                parent_data['Images']=image_link
            except:
                continue
            parent_data['Name']=products[1][i]
            writer.writerow(parent_data)
            print(products[1][i])
            i+=1
        page+=1
        products = get_product_page(page)

                
