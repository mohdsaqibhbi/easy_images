import logging
import os
import time
from datetime import datetime
from importlib.resources import path
from urllib.parse import quote

import bs4
import cv2
import magic
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tabulate import tabulate
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager


class EasyImages:

    def __init__(self, browser_name='chrome', loading_timeout=2):

        '''
        Intialized all the necessary variables and constants while creating the class object.

        Parameters:
        -----------
            - browser_name (str): Browser name of the user
            - loading_timeout (float): Page loading timeout. Less for fast and more for slow internet.

        Returns:
        --------
        None
        '''

        log_filename = "easyimages.log"
        logging.basicConfig(filename=log_filename,
                    format='%(asctime)s %(message)s',
                    filemode='a')

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        self.BROWSER_FILE_PATH = '/usr/bin/brave-browser'
        self.BROWSER_NAME = 'brave'
        self.browser_name = browser_name
        self.MAX_SCROLL_NUMBER = 160
        self.MIN_SCROLL_NUMBER = 0
        self.IMAGES_PER_SCROLL = 25
        self.SCROLL_SIMILARITY = 2
        self.IMAGES_PER_HALF_PAGE = 350
        self.PAGE_LOADING_TIMEOUT = loading_timeout
        self.SCROLLING_TIMEOUT_FACTOR = 40
        self.PAGE_SCROLLING_TIMEOUT = self.PAGE_LOADING_TIMEOUT / self.SCROLLING_TIMEOUT_FACTOR
        self.UTILITY_FUNCTIONS_TIMEOUT = 0.01

        self.PRINT_FORMAT = {"LINE": {"SYMBOL": "#", "LENGTH": 80},
                             "1_NEWLINE": "\n",
                             "2_NEWLINE": "\n\n"}

        self.logger.info("[INFO] Initialized all the variables.")

    def _make_directory(self, keyword):

        '''
        Create directory for the given keyword inside the main output directory. If not already,
        create an output directory first.

        Parameters:
        -----------
            - keyword (str): Keyword to create sub-directory

        Returns:
        --------
        None
        '''

        keyword = keyword.replace(" ", "_")

        try:

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                time.sleep(0.2)
                keyword_directory = os.path.join(self.output_dir, keyword)

                if not os.path.exists(keyword_directory):
                    os.makedirs(keyword_directory)
            else:
                keyword_directory = os.path.join(self.output_dir, keyword)
                if not os.path.exists(keyword_directory):
                    os.makedirs(keyword_directory)

            self.logger.info("[INFO] Successfully created the directories.")

        except OSError as e:
            self.logger.error("[ERROR] {}".format(e))
            if e.errno != 17: raise

    def _check(self, keywords_dict, check_type="Final"):

        '''
        Prepare the summary dict for the given tag name.

        Parameters:
        -----------
            - check_type (str): Final number of images

        Returns:
        --------
        None
        '''

        for keyword_directory in keywords_dict.keys():

            keyword_directory_path = os.path.join(self.output_dir, keyword_directory.replace(" ", "_"))
            self.summary_dict[keyword_directory][check_type] = len(os.listdir(keyword_directory_path))

    def _generate_hash(self, image, hash_size=8):

        '''
        Generate hash for the given image.

        Parameters:
        -----------
            - image (numpy array): Keyword to create sub-directory
            - hash_size (int): Size of hash

        Returns:
        --------
        Hash (int): Hash generated for the given image
        '''

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (hash_size + 1, hash_size))

        diff = resized[:, 1:] > resized[:, :-1]

        return sum([2 ** index for (index, value) in enumerate(diff.flatten()) if value])

    def _remove_duplicates(self, image_path):

        '''
        Find out if the given image is duplicate or not. True stand for duplicate.

        Parameters:
        -----------
            - image_path (str): Path of the image

        Returns:
        --------
        Duplicate (boolean): Duplicate or not
        '''

        image = cv2.imread(image_path)
        image_hash = self._generate_hash(image)

        same_hash_image_list = self.image_hash_dict.get(image_hash, [])
        if len(same_hash_image_list) == 0:
            same_hash_image_list.append(image_path)
            self.image_hash_dict[image_hash] = same_hash_image_list
            return False
        else:
            return True

    def _scroll_down(self, number):

        '''
        Scroll down the page according to the given number of images to download.

        Parameters:
        -----------
            - number (int): Number of the images to download

        Returns:
        --------
        None
        '''

        # Number of times to scroll down
        number = max(self.MIN_SCROLL_NUMBER, min(self.MAX_SCROLL_NUMBER,
            int((number - self.IMAGES_PER_SCROLL)/self.SCROLL_SIMILARITY)))
        for i in range(number):
            time.sleep(self.PAGE_SCROLLING_TIMEOUT)
            self.scroll_element.send_keys(Keys.DOWN)

    def _get_image_url(self, base_url, keyword, max_limit):

        '''
        Get the list of image urls from the page.

        Parameters:
        -----------
            - base_url (str): Base url of the page where to visit to get the images
            - max_limit (int): Maximum number of images needed

        Returns:
        --------
        image_url_list (list): List of image urls.
        '''

        self.browser.get(base_url)

        # Wait to get the page loaded
        time.sleep(self.PAGE_LOADING_TIMEOUT)
        soup = bs4.BeautifulSoup(self.browser.page_source, features="html.parser")
        self.scroll_element = self.browser.find_element(By.ID, 'yDmH0d')

        if self.scroll_element:
            self._scroll_down(max_limit)
            time.sleep(self.PAGE_LOADING_TIMEOUT)
            soup = bs4.BeautifulSoup(self.browser.page_source, features="html.parser")

            if max_limit > self.IMAGES_PER_HALF_PAGE:
                try:
                    self.more_element = self.browser.find_element(By.CLASS_NAME, 'mye4qd')
                    if self.more_element:
                        self.more_element.click()
                        time.sleep(self.PAGE_LOADING_TIMEOUT)
                        if self.scroll_element: self._scroll_down(max_limit)
                except Exception as e:
                    self.logger.error("[ERROR] {}".format(e))

        time.sleep(self.PAGE_LOADING_TIMEOUT)
        image_url_list = set()

        image_elements = self.browser.find_elements(By.CLASS_NAME, 'rg_i.Q4LuWd')

        for image_element in tqdm(image_elements, desc = "[INFO] Getting URLs for keyword '{}'".format(keyword), leave=False, colour="green"):

            try:
                image_element.click()
                time.sleep(self.PAGE_SCROLLING_TIMEOUT)
                soup = bs4.BeautifulSoup(self.browser.page_source, features="html.parser")

                for image_element in soup.find_all('img', class_='n3VNCb'):
                    if image_element.has_attr('src'):
                        if "data:image" not in image_element['src']:
                            image_url_list.add(image_element['src'])

            except Exception as e:
                self.logger.error("[ERROR] {}".format(e))

        return list(image_url_list)

    def download(self, keywords, output_dir='easy_images_dir', max_limit=10, image_formats={'.jpg', '.jpeg', '.png'}, remove_duplicates=False):

        '''
        Download the images for the given keyword(s) as per given a number of helpful variables like
        (maximum number of images, image formas, remove duplicate or not etc.).

        Parameters:
        -----------
            - keywords (str / dict): Keywords for which images will be downloaded
            - output_dir (srt): Path of the main output directory
            - max_limit (int): Maximum number of images needed
            - image_formats (set): Supported image formats
            - remove_duplicates (boolean): Whether to remove duplicate images or not while downloading. Set remove_duplicates=True to remove duplicates.

        Returns:
        --------
        None
        '''

        start_time = datetime.now()

        self.output_dir = output_dir
        self.image_formats = image_formats
        self.summary_dict = {}

        # Make the keyword dict e.g {"dog": 10, "cat": 10} from "dog, cat"
        if isinstance(keywords, str):
            keywords_dict = {str(item).strip():max_limit for item in keywords.split(',')}
        else:
            keywords_dict = keywords

        if self.browser_name == self.BROWSER_NAME:
            option = Options()
            option.binary_location = self.BROWSER_FILE_PATH
            self.browser = webdriver.Chrome(options = option, service = Service(ChromeDriverManager().install()))
        else:
            self.browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

        ##########################################################################################
        # Downloading section

        print(self.PRINT_FORMAT["1_NEWLINE"])
        for keyword, max_limit in tqdm(keywords_dict.items(), desc = '[INFO] Downloading images', colour="CYAN"):

            count_dict = {'Found': 0, 'Downloaded': 0}
            image_url_list = []
            image_number = 0

            if remove_duplicates:
                self.logger.info("[INFO] Remove duplicates factor is set.")
                self.image_hash_dict = {}

            base_url = 'https://www.google.com/search?q=' + quote(
            keyword.encode('utf-8')) + '&biw=1536&bih=674&tbm=isch&sxsrf=ACYBGNSXXpS6YmAKUiLKKBs6xWb4uUY5gA:1581168823770&source=lnms&sa=X&ved=0ahUKEwioj8jwiMLnAhW9AhAIHbXTBMMQ_AUI3QUoAQ'

            image_url_list = self._get_image_url(base_url, keyword, max_limit)

            self._make_directory(keyword)
            keyword_directory_path = os.path.join(self.output_dir, keyword.replace(" ", "_"))

            for image_index in tqdm(range(len(image_url_list)), desc = "[INFO] Downloading images for keyword '{}'".format(keyword), leave=False, colour="green"):

                if count_dict['Downloaded'] == max_limit:
                    break

                try:
                    request_object = requests.get(image_url_list[image_index], allow_redirects=True, timeout=1)

                    if('html' not in str(request_object.content)):
                        mime = magic.Magic(mime=True)
                        file_type = mime.from_buffer(request_object.content)
                        file_format = f'.{file_type.split("/")[-1]}'

                        if file_format not in image_formats:
                            raise ValueError()

                        file_name = str(keyword.replace(" ", "_")) + "_" + str(image_number + 1) + file_format

                        file_path = os.path.join(keyword_directory_path, file_name)

                        with open(file_path, 'wb') as file:
                            file.write(request_object.content)

                        if remove_duplicates:

                            if self._remove_duplicates(file_path):
                                try:
                                    count_dict['Downloaded'] -= 1
                                    image_number -= 1
                                    os.remove(file_path)
                                except Exception as e:
                                    self.logger.error("[ERROR] {}".format(e))

                        image_number += 1
                        count_dict['Downloaded'] += 1

                except Exception as e:
                    self.logger.error("[ERROR] {}".format(e))

            if count_dict['Downloaded'] < max_limit:
                self.logger.info("[INFO] Only {} images are downloaded for keyword '{}'".format(
                count_dict['Downloaded'], keyword))
            else:
                self.logger.info("[INFO] Total {} images are downloaded for keyword '{}'".format(
                count_dict['Downloaded'], keyword))

            count_dict['Found'] = len(image_url_list)
            self.summary_dict[keyword] = count_dict

        self.browser.close()

        ##########################################################################################
        # Print Section

        self._check(keywords_dict, check_type="Final")
        end_time = datetime.now()

        print(self.PRINT_FORMAT["1_NEWLINE"])
        print(self.PRINT_FORMAT["LINE"]["SYMBOL"]*self.PRINT_FORMAT["LINE"]["LENGTH"],
            end=self.PRINT_FORMAT["2_NEWLINE"])

        print('[INFO] Total time taken (hh:mm:ss.ms) {}'.format(end_time - start_time),
            end=self.PRINT_FORMAT["2_NEWLINE"])

        print(self.PRINT_FORMAT["LINE"]["SYMBOL"]*self.PRINT_FORMAT["LINE"]["LENGTH"],
            end=self.PRINT_FORMAT["2_NEWLINE"])

        print("[SUMMARY] Summary of downloaded images:", end=self.PRINT_FORMAT["2_NEWLINE"])

        summary_list = [[key]+list(value.values()) for key, value in self.summary_dict.items()]
        headers = ['Keyword']+list(list(self.summary_dict.values())[0].keys())
        print(tabulate(summary_list, headers=headers), end=self.PRINT_FORMAT["2_NEWLINE"])

        print(self.PRINT_FORMAT["LINE"]["SYMBOL"]*self.PRINT_FORMAT["LINE"]["LENGTH"],
            end=self.PRINT_FORMAT["2_NEWLINE"])

    ##########################################################################################
    ##########################################################################################
    # Extra Functionalities

    def remove_duplicates(self, image_dir):

        '''
        Remove the duplicate images present in a directory.

        Parameters:
        -----------
            - image_dir (str): Path of the directory having images

        Returns:
        --------
        None
        '''

        image_hash_dict = {}
        image_dir_name = image_dir.split("/")[-1]
        if not image_dir_name: image_dir_name = image_dir.split("/")[-2]
        number_of_images = len(os.listdir(image_dir))

        for image_name in tqdm(os.listdir(image_dir), desc = '[INFO] Removing duplicate images for "{}"'.format(image_dir_name), colour="red"):

            if number_of_images <= 1000: time.sleep(self.UTILITY_FUNCTIONS_TIMEOUT)
            image_path = os.path.join(image_dir, image_name)
            image = cv2.imread(image_path)

            if image is None:
                try:
                    os.remove(image_path)
                except Exception as e:
                    self.logger.error("[ERROR] {}".format(e))
            else:
                image_hash = self._generate_hash(image)
                same_hash_image_list = image_hash_dict.get(image_hash, [])
                same_hash_image_list.append(image_path)
                image_hash_dict[image_hash] = same_hash_image_list

        for (image_hash, hashed_paths) in image_hash_dict.items():

            if len(hashed_paths) > 1:
                for image_path in hashed_paths[1:]:
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        self.logger.error("[ERROR] {}".format(e))

    def resize_and_save(self, image_dir, size=(200, 200)):

        '''
        Resize images present in a directory.

        Parameters:
        -----------
            - image_dir (str): Path of the directory having images
            - size (tuple): Image size to resize

        Returns:
        --------
        None
        '''

        image_dir_name = image_dir.split("/")[-1]
        if not image_dir_name: image_dir_name = image_dir.split("/")[-2]
        number_of_images = len(os.listdir(image_dir))

        for image_name in tqdm(os.listdir(image_dir), desc = '[INFO] Resizing images with {} for "{}"'.format(size, image_dir_name), colour="#2554C7"):
            if number_of_images <= 1000: time.sleep(self.UTILITY_FUNCTIONS_TIMEOUT)
            image_path = os.path.join(image_dir, image_name)
            image = cv2.imread(image_path)

            if image is not None:
                image = cv2.resize(image, size)
                cv2.imwrite(image_path, image)

    def to_grayscale(self, image_dir):

        '''
        Convert images present in a directory to grayscale.

        Parameters:
        -----------
            - image_dir (str): Path of the directory having images

        Returns:
        --------
        None
        '''

        image_dir_name = image_dir.split("/")[-1]
        if not image_dir_name: image_dir_name = image_dir.split("/")[-2]
        number_of_images = len(os.listdir(image_dir))

        for image_name in tqdm(os.listdir(image_dir), desc = '[INFO] Grayscaling images for "{}"'.format(image_dir_name), colour="#778899"):
            if number_of_images <= 1000: time.sleep(self.UTILITY_FUNCTIONS_TIMEOUT)
            image_path = os.path.join(image_dir, image_name)
            image = cv2.imread(image_path)

            if image is not None:
                try:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(image_path, image)
                except Exception as e:
                    self.logger.error("[ERROR] {}".format(e))

    def calculate_avg_image_size(self, image_dir):

        '''
        Calculate average image size of the images present in a directory.

        Parameters:
        -----------
            - image_dir (str): Path of the directory having images

        Returns:
        --------
        None
        '''

        heights = []
        widths = []

        image_dir_name = image_dir.split("/")[-1]
        if not image_dir_name: image_dir_name = image_dir.split("/")[-2]

        for image_name in tqdm(os.listdir(image_dir), desc = '[INFO] Calculating average image size for "{}"'.format(image_dir_name), colour="#E2F516"):
            try:
                image_path = os.path.join(image_dir, image_name)
                image = cv2.imread(image_path)
                height, width, _ = image.shape
                heights.append(height)
                widths.append(width)
            except Exception as e:
                self.logger.error("[ERROR] {}".format(e))

        heights = np.array(heights)
        widths = np.array(widths)
        print("[OUTPUT] Total number of images: {}".format(len(heights)))
        print("[OUTPUT] Mean height: {} | Mean width: {}".format(heights.mean(), widths.mean()))

    def post_processing(self, image_dir, remove_duplicates=False, resize=None, grayscale=False, avg_image_size=False):

        '''
        Perform various image post processing operations in one go.

        Parameters:
        -----------
            - image_dir (str): Path of the directory having images
            - remove_duplicates (boolean): Whether to remove duplicate images from a directory. Set remove_duplicates=True to remove duplicates.
            - resize (tuple): Image size to resize
            - grayscale (boolean): Whether to convert images in a directory,  into grayscale. Set grayscale=True to convert.
            - avg_image_size (boolean): Whether to calculate average image size of all the images in a directory. Set avg_image_size=True to calculate.

        Returns:
        --------
        None
        '''

        if remove_duplicates: self.remove_duplicates(image_dir=image_dir)
        if resize: self.resize_and_save(image_dir=image_dir, size=resize)
        if grayscale: self.to_grayscale(image_dir=image_dir)
        if avg_image_size: self.calculate_avg_image_size(image_dir=image_dir)
