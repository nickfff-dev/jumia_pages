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
options.add_argument("--headless")

def product_run(driver, mainurl, page_url,  page_data, listing_dir,numberofproducts):
        print(page_url)
        driver.get(page_url)
        try:
            cookije_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pop > div > section > button')))
            if cookije_button.is_displayed():
                cookije_button.click()
        except:
            pass
        try:
            products = driver.find_elements(By.CSS_SELECTOR, '#jm > main > div.aim.row.-pbm > div.-pvs.col12 > section > div.-paxs.row._no-g._4cl-3cm-shs > article')
        except:
            print("no products")
            return
        if len(products) > 0:
            for product in products:     
                product_link = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                page_data['productcount'] = numberofproducts
                page_data['product_url'] = product_link
                driver = webdriver.Chrome(options=options)
                driver.get(product_link)
                try:    
                    cookije_button2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pop > div > section > button')))
                    if cookije_button2.is_displayed():
                        cookije_button2.click()
                except:
                    pass
                try:
                    cookie_consent = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((BY.CSS_SELECTOR, "#jm > div.banner-pop > button > span > svg")))
                    if cookie_consent.is_displayed():
                        cookie_consent.click()
                except:
                    pass
                try:
                    product_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/main/div[1]/section/div/div[2]/div[1]/div/h1'))).text
                    product_sku = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[1]/section/div/div[2]/div[1]/a"))).get_attribute('data-simplesku')
                    print(product_sku)
                    page_data['title'] = product_name
                    page_data['sku'] = product_sku.replace("SKU: ", "")
                except:
                    print('could not grab all details')
                    continue         
                images = driver.find_elements(By.XPATH, '/html/body/div[1]/main/div[1]/section/div/div[1]/div/div[1]/a')                                                       
                if len(images) > 0:
                    try:
                        for i in range(7):
                            page_data[f'image{i+1}'] = images[i].get_attribute('href')
                            # avoid 403 forbidden when downloading the image
                            p_url = page_data[f'image{i+1}']
                            req = requests.get(p_url, headers={'User-Agent': 'Mozilla/5.0'})
                            if req.status_code == 200:
                            # remove characters that are not allowed in file names from the product name
                                new_file_name = product_name.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
                                os.makedirs(f'{listing_dir}/{new_file_name}', exist_ok=True)
                            with open(f'{listing_dir}/{new_file_name}/{product_sku.replace("SKU: ", "")}_{i+1}.jpg', 'wb') as f:
                                f.write(req.content)                   
                    except:
                            page_data[f'image{i+1}'] = f'no image {i+1}'
                            print(f'no image {i+1} for {product_name}')
                field_names = ['title', 'sku', "productcount", 'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'product_url']
                filename =  f'{listing_dir}/{mainurl.split("/")[3]}.csv'
                append_dict_as_row(filename, page_data, field_names)




def getData(mainurl):
    page_data ={"title": "","sku": "","productcount": "", "image1": "", "image2": "", "image3": "", "image4": "", "image5": "", "image6": "", "image7": "", "image8": "", "product_url": ""}
    driver = webdriver.Chrome(options=options)
    listing_dir = mainurl.split('/')[3]
    print(listing_dir)
    os.makedirs(listing_dir, exist_ok=True)
    driver.get(mainurl)
    numberofpages = 0
    try:
        cookije_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pop > div > section > button')))
        if cookije_button.is_displayed():
            cookije_button.click()
    except:
        pass
    try:
        productCount = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#jm > main > div.aim.row.-pbm > div.-pvs.col12 > section > header > div.-phs.-mh-48px.-df.-j-bet.-i-ctr.-bb > p')))
    except:
        print('{} has no products'.format(listing_dir))
        return
    if productCount.is_displayed():
        productCounttext = productCount.text
        numberofproducts = int(productCounttext.replace(' products found', ''))
        print(numberofproducts)
        numberofpages = int(numberofproducts / 40 )
        remainder = int(numberofproducts) % 40
        if remainder > 0:
            numberofpages = numberofpages + 1
        print(numberofpages)
        i = 0
        for i in range(1, numberofpages + 1):
            page_url = f'{mainurl}?page={i}#catalog-listing'
            driver = webdriver.Chrome(options=options)
            product_run(driver, mainurl, page_url,  page_data, listing_dir,numberofproducts)

        





allurls = ['https://www.jumia.co.ke/mlp-hp-store','https://www.jumia.co.ke/mlp-apple-store','https://www.jumia.co.ke/mlp-garnier-store','https://www.jumia.co.ke/mlp-pz-cussons-store','https://www.jumia.co.ke/mlp-eagm-store','https://www.jumia.co.ke/mlp-infinix-official-store','https://www.jumia.co.ke/mlp-clinique-official-store','https://www.jumia.co.ke/mlp-kenya-fashion-council-store','https://www.jumia.co.ke/mlp-miniso-store','https://www.jumia.co.ke/mlp-pernod-ricard-store','https://www.jumia.co.ke/mlp-mac-official-store','https://www.jumia.co.ke/mlp-maybelline-store','https://www.jumia.co.ke/mlp-nice-and-lovely-store','https://www.jumia.co.ke/mlp-ilife-official-store','https://www.jumia.co.ke/mlp-/lg-store/','https://www.jumia.co.ke/mlp-bruhm-store','https://www.jumia.co.ke/mlp-la-colors-store','https://www.jumia.co.ke/mlp-nokia-official-store','https://www.jumia.co.ke/mlp-blu-store','https://www.jumia.co.ke/mlp-hisense-store','https://www.jumia.co.ke/mlp-samsung-store','https://www.jumia.co.ke/mlp-dr-mattress-store','https://www.jumia.co.ke/mlp-kimfay-store','https://www.jumia.co.ke/mlp-chandaria-store','https://www.jumia.co.ke/mlp-la-girl-store','https://www.jumia.co.ke/mlp-mika-store','https://www.jumia.co.ke/mlp-menengai-official-store','https://www.jumia.co.ke/mlp-venus-store','https://www.jumia.co.ke/mlp-visionplus-official-store','https://www.jumia.co.ke/mlp-la-girls-store','https://www.jumia.co.ke/mlp-la-girl-official-store','https://www.jumia.co.ke/mlp-maybelline-online-store','https://www.jumia.co.ke/mlp-mizani-official-store','https://www.jumia.co.ke/mlp-eabl-official-store','https://www.jumia.co.ke/mlp-ring-store']

for url in allurls:
    getData(url)





