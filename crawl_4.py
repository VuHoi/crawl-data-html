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
    response = requests.get(settings. products_url4+ '?page={}'.format(page))
    selector = Selector(response.text)
  
    container= selector.css('div.item > a.grid__image')
    img1= container.css('img:first-child')
    print(img1)
    images = img1.xpath('./@src').getall()
    text = selector.css('p.desktop_nav')

    names = text.xpath('.//a/text()').getall()
    
    return (images,names)


template_line = get_template_line()
parent_data = copy.deepcopy(template_line)
fieldnames = template_line.keys()


with open('4.csv', 'w', newline='\n') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    page = 1
    products = get_product_page(page)
    print(len(products[0]),len(products[1]))
    while products[0]:
        
        i=0
        while(i<len(products[0])):
            parent_data['image']=products[0][i]
            parent_data['name']=products[1][i].replace('\n','').replace('\t','')
            writer.writerow(parent_data)
            print(parent_data['name'])
            i+=1
        page+=1
        products = get_product_page(page)

                
