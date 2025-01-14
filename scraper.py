
import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import csv
from csv import DictWriter
import requests
import json
import sys

def append_dict_as_row(file_name, dict_of_elem, field_names):
    # Open file in append mode
    with open(file_name, 'a+', newline='', encoding="utf-8") as write_obj:
        # Create a writer object from csv module
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        # Add dictionary as wor in the csv
        dict_writer.writerow(dict_of_elem)


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")
#options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
filename =  sys.argv[1]
def get_product_data(product_link):
                page_data = {}
                driver.get(product_link)
                #try:    
                    #cookije_button2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pop > div > section > button')))
                    #if cookije_button2.is_displayed():
                        #cookije_button2.click()
                #except:
                    #pass
                try:
                    cookie_consent = WebDriverWait(driver, 3).until(EC.presence_of_element_located((BY.CSS_SELECTOR, "#jm > div.banner-pop > button > span > svg")))
                    if cookie_consent.is_displayed():
                        cookie_consent.click()
                except:
                    pass
                try:
                    product_details = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#wishlist')))
                    product_name = product_details.get_attribute('data-gtm-name')
                    product_sku = product_details.get_attribute('data-sku')
                    product_vendorname = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#jm > main > div:nth-child(1) > div.col4 > div > section > div.-hr.-pas > p"))).text
                    page_data['title'] = product_name
                    page_data['sku'] = product_sku
                    page_data['vendorname'] = product_vendorname
                    page_data['product_url'] = product_link
                except Exception as e:
                    print('could not grab all details')

                  
                print(page_data)
                field_names = ['title', 'sku', 'vendorname', 'product_url']
                append_dict_as_row(filename, page_data, field_names) 




def get_product_links(url, number_of_pages):
    driver.get(url)
    all_products = [] 
    try:
        cookie_consent = WebDriverWait(driver, 3).until(EC.presence_of_element_located((BY.CSS_SELECTOR, "#jm > div.banner-pop > button > span > svg")))
        if cookie_consent.is_displayed():
          cookie_consent.click()
    except:
        print('fuck off 2')

    for i in range (1, number_of_pages + 1):
        products_page_url = f'{url}&page={i}#catalog-listing'
        print(products_page_url)
        driver.get(products_page_url)
        try:
            products = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#jm > main > div.aim.row.-pbm > div.-pvs.col12 > section > div.-paxs.row._no-g._4cl-3cm-shs > article > a')))
            for item in products:
                page_url = item.get_attribute('href')
                if page_url is not None:                    
                    all_products.append(page_url)
                    print(page_url)
        except:
            continue
    return all_products



if __name__ == '__main__':
    if len(sys.argv) < 4: 
        print("usage: python scraper.py csvname.csv catalog_url number_of_pages")
        sys.exit()
    catalog_url = sys.argv[2]
    number_of_pages = int(sys.argv[3])
    product_links = get_product_links(catalog_url, number_of_pages)
    if len(product_links) > 0:
        for link in product_links:
            if 'customer' in link:
                continue
            else: 
                get_product_data(link)
        





