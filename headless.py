from selenium import webdriver 
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager 
import undetected_chromedriver as uc 

import os
import time
import logging
import requests
from pprint import pprint

# Set up logging configuration
logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.INFO)

# Function to create a new directory if it doesn't exist
def makedir(name):
	if not os.path.isdir(name):
		os.mkdir(name)


# Remove links that point to the same chapter
def clean(l):
	clean_data = {}
	for i in l:
		key = i.split('/')[-1].split('-')[-2]
		
		try: 
			key=int(key)
		except Exception: 
			key=float(key)

		clean_data[key] = i

	return clean_data

# Find the base link of the comic from the url
def prepare(url):
	sections = url.split('/')
	
	# Make the website sort the chapters in ascending order
	if len(sections) >= 5:  
		sections[4] = sections[4].split("?")[0]
		url  = "/".join(sections[:5])
		url += "?lang=en&chap-order=1"
	else:
		return url

	return url

# record the directory into a file
def record(data,name):
	print("[~] Recording chapter links into a file ...")

	new_data={}
	new_data[name] = [data,list(data.keys())[0]]
	# {name: [{1:'url', 2:'url', ...}, 1]}

	with open("download_log",'w') as f:
		f.write(str(new_data))
	print("[+] Finished recording.")

# returns the data from log
def read_log():
	print("[~] Reading the previous log.")

	file = "download_log"
	if file not in os.listdir():
		return {}
	
	with open(file,'r') as f:
		data=f.read()
	data = eval(data)
	
	return data

# Download chapter links from the url
def grab_chapters(url,driver):
	url = prepare(url)

	print(f"[~] Sending requests to {url}")

	# Start scraping
	driver.get(url)

	selector = 'tr.group > td:nth-child(1) > a'

	element  = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, selector))
	)

	# reach the end of the scroll bar
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	print("[~] Gathering links of the chapters ...")

	# Grab the links of chapters
	chapter_links = driver.find_elements(By.CSS_SELECTOR,selector)
	chapter_links = [i.get_attribute('href') for i in chapter_links]

	print("[+] Got a list of chapters' links.")
	print("[+] Cleaning up the links with the same chapter.")

	# clean up links with the same chapter
	chapter_links = clean(chapter_links)
	
	# return the directory
	return chapter_links

# Extract image links from the url
def get_image_links(url,driver):

	print(f'[~] Sending requests to {url}')

	try:
		driver.set_page_load_timeout(40)  # Set the timeout to 40 seconds
		driver.get(url)
	except TimeoutException:
		print("[x] Page load timed out, the website might be taking too long to respond.")
		return None
	
	# reach the end of the scroll bar
	driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

	selector = 'div.images-reader-container > div:nth-child(1) > div > div > div > div > img'
	
	element = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.CSS_SELECTOR, selector))
	)
	print("[~] Grabbing links of the images ...")
	image_links = driver.find_elements(By.CSS_SELECTOR,selector)
	image_links = [i.get_attribute('src') for i in image_links]
	
	return image_links

# get session
def get_session():
	session = requests.Session()
	session.headers.update({"User-Agent": "Mozilla/5.0"})
	return session


# Gets image data from the url of an image
def get_img(url):
	session  = get_session()
	img 	 = session.get(url)

	# Retry the download if the initial request is not successful
	retry = 5
	while not img.ok and retry > 0:

		logging.error(f"[x] Website blocked the access. Status: {img.status_code}")
		logging.info('[-] Sleeping for 1 second.')
		
		time.sleep(1)

		session = get_session()			
		img 	= session.get(link)
		retry  -= 1

	return img

# save the image data into a file
def save_img(data, filepath):
	with open(filepath,'wb') as f:
		f.write(data)

# Downloads the chapter inside url
def download_comic(url, chapter_num, comic_name, driver):
	
	print(f"[~] Gathering image links of chapter {chapter_num}")

	# get image links fromm the url of a chapter
	image_links = get_image_links(url,driver)
	
	if image_links == None:
		return "refresh"

	print("[+] Got image links in the bag!")

	print(f"[~] Downloading images of chapter {chapter_num}")

	# Download each image and save it in the chapter directory
	i=0
	for link in image_links:
		path = f"Comics/{comic_name}/{chapter_num}"
		makedir(path)

		# Download image data from the url
		img 	 = get_img(link).content

		path += f"/{i}.png"

		# Save the image to the filepath
		save_img(img, path)
		print(f"[+] Downloaded {link} to {path}")
		
		i+=1


	
# Function to extract comic name from url
def get_name(url):
	name = url.split('/')[4]
	name = " ".join(name.split('-')[1:])
	return name

# Delete the folder if it is empty. 
def checkFolder(path):
	if len(os.listdir(path))==0:
		shutil.rmtree(path)
		print(f"Failed to download {path.split('/')[2]} of {path.split('/')[1]}")


# Get Chrome driver 
def get_diver():

	options = Options()

	# enable headless mode
	# options.add_argument("--headless")

	# block image loading
	options.add_argument('--blink-settings=imagesEnabled=false')

	driver = uc.Chrome(use_subprocess=True, options=options)
	driver.maximize_window()

	return driver

# handles errors related to download_comic function
def handle_download_comic(url, i, name, driver, chapters):
	state = download_comic(chapters[i], i, name, driver)
	
	if state == "refresh":
		print("[~] Refreshing the browser ...")
		driver.quit()
		driver=get_diver()
		
		print("[~] Resting for 5 seconds ...")
		time.sleep(5)
		
		handle_download_comic(chapters[i], i, name, driver,chapters)
	
	# Delete the folder if it is empty.
	checkFolder(f"Comics/{name}/{i}")  


# Filter the list to download from the marked chapter
def filter(chapters):
	mark = 72
	# mark = 50
	filtered = list(chapters.keys())
	pprint(chapters)
	indx = filtered.index(mark)
	return filtered[indx:]

# function to test grab_chapters and download_comic functions
def test():
	driver=get_diver()
	# driver.minimize_window()

	url 	 = 'https://comick.app/comic/00-the-legendary-mechanic/TLqmS0Ej-chapter-21-en'
	name 	 = get_name(url)
	log 	 = read_log()
	
	# check if there is a record of chapter links of comic [name]
	if name in log.keys():
		chapters = log[name][0]
	else:
		print(f"[-] There is no log for {name}")
		chapters = grab_chapters(url,driver)
		# record the chapter links into a filepath
		# this saves extra time for a second time of download.
		record(chapters,name)
	
	makedir('Comics')
	makedir(f'Comics/{name}')

	filtered = filter(chapters)

	for i in filtered:
		if i == 106:
			break
		handle_download_comic(chapters[i],i,name,driver,chapters)
		print("[~] Resting for 5 seconds ...")
		time.sleep(5)


	# release the resources allocated by Selenium
	# and shut down the browser
	driver.quit()

if __name__ == "__main__":
	test()