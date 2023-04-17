from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import time
import urllib.request
import os
import requests
import io
from PIL import Image

import patch


class ImageScraper():
    def __init__(self, webdriver_path, image_path, search_key="cat",
                 number_of_images=1, headless=False, min_re=(0, 0), max_re=(1920, 1080)):
        image_path = os.path.join(image_path, search_key)
        while (True):
            try:
                options = Options()
                # options.add_extension('chromedrivers/extension_5_3_2_0.crx')
                if (headless):
                    options.add_argument('--headless')
                driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                # 1400, 1050
                driver.set_window_size(1400, 1050)
                driver.get("https://www.google.com")
                break
            except:
                try:
                    driver
                except NameError:
                    is_patched = patch.download_lastest_chromedriver()
                else:
                    is_patched = patch.download_lastest_chromedriver(driver.capabilities['version'])

        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw & biw = 1920 & bih = 947"%(search_key)
        self.headless = headless
        self.min_re = min_re
        self.max_re = max_re

    def find_image_urls(self):
        image_urls = []
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)
        indx = 1
        while self.number_of_images > count:
            try:
                # time.sleep(5)
                imgurl = self.driver.find_element(By.XPATH, '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(indx)))
                # try:
                self.driver.execute_script("arguments[0].click();", imgurl)
                # imgurl.click()
                # except Exception as e:
                #     print('click error', e)
                #     imgurl.send_keys(Keys.ENTER)

                missed_count = 0
            except Exception as e:
                print('pass', e)
                missed_count = missed_count + 1
                if (missed_count > 1000):
                    print("[INFO] No more photos.")
                    break

            try:
                time.sleep(1)
                class_names = ["n3VNCb"]
                images = [self.driver.find_elements(By.CLASS_NAME, class_name)
                          for class_name in class_names if len
                          (self.driver.find_elements(By.CLASS_NAME, class_name)) != 0][0]
                for image in images:
                    src_link = image.get_attribute("src")
                    if (("http" in src_link) and (not "encrypted" in src_link)):
                        print("[INFO] %d. %s" % (count, src_link))
                        image_urls.append(src_link)
                        count += 1
                        break
            except Exception:
                try:
                    if (count % 3 == 0):
                        self.driver.execute_script("window.scrollTo(0, " + str(indx * 60) + ");")
                    element = self.driver.find_element(By.CLASS_NAME, "mye4qd")
                    element.click()
                    time.sleep(3)
                except Exception:
                    time.sleep(1)
                indx += 1

        self.driver.quit()
        return image_urls

    def save_images(self, image_urls):
        for indx, image_url in enumerate(image_urls):
            try:
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url, timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if os.path.isdir(self.image_path):
                                pass
                            else:
                                os.makedirs(self.image_path, exist_ok=True)

                            filename = "%s%s.%s" % (search_string, str(indx),
                                                    image_from_web.format.lower())
                            image_path = os.path.join(self.image_path, filename)

                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if image_resolution[0] < self.min_re[0] or image_resolution[1] < self.min_re[1]:
                                image_from_web.close()
                                os.remove(image_path)

                    image_from_web.close()
            except Exception as e:
                print('save error', e)
                pass