import os
import time
import json
import logging
import display
import requests
import headless
from pprint import pprint
from bs4 import BeautifulSoup

# Set up logging configuration
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)

# Function to create a new requests session with custom User-Agent
def get_session():
	session = requests.Session()
	session.headers.update({"User-Agent": "Mozilla/5.0"})
	return session

# Function to download a web page using requests
def scrape(target_url):
	session = get_session()
	response = session.get(target_url)
	return response

# Function to create a new directory if it doesn't exist
def makedir(name):
	if not os.path.isdir(name):
		os.mkdir(name)

# Function to get JSON data from the response
def get_json_data(response):
	# Parse the HTML content using BeautifulSoup
	html = response.text
	soup = BeautifulSoup(html, 'html.parser')
	spec = {'id':"__NEXT_DATA__",'type':'application/json'}
	soup = soup.find('script',spec).text
	data = json.loads(soup)

	return data

# Function to download a comic chapter
def digForImageLinks(html):
	images = []
	soup = BeautifulSoup(html, 'html.parser')
	spec = {'class':''}
	soup = soup.find('div',spec).text
	for i in soup.findAll('img'):
		images += i.get('src')
	return images


# Function to download a comic chapter
def download_comic(url,chapter_num,comic_name):

	# Scrape the chapter URL
	response  = scrape(url)
	base_link = "https://meo3.comick.pictures/"

	# Check if the response is successful
	if not response.ok:
		logging.error("[x] Website blocked the access. Status: ", response.status_code)
		return None

	# Grab JSON data from response
	data = get_json_data(response)

	logging.info(f'Downloaded Chapter {chapter_num} of {comic_name}')

	 # Create a directory for the comic chapter	
	makedir(f'Comics/{comic_name}/{chapter_num}')

	# Extract the image URLs from the JSON data
	images = data['props']['pageProps']['chapter']['md_images']
	images = [base_link+i['b2key'] for i in images]

	# Download each image and save it in the chapter directory
	i=0
	for img_link in images:
		session  = get_session()
		img 	 = session.get(img_link)
		
		filepath = f"Comics/{comic_name}/{chapter_num}/{i}.png"
		
		# Retry the download if the initial request is not successful
		retry = 5
		while not img.ok and retry > 0:

			logging.error(f"[x] Website blocked the access. Status: {img.status_code}")
			logging.info('Sleeping for 1 second.')
			
			time.sleep(1)

			session = get_session()			
			img 	= session.get(img_link)
			retry  -= 1

		# Save the image to the filepath
		with open(filepath,'wb') as f:
			f.write(img.content)
		
		i+=1
		
		logging.info(f"Downloaded {filepath}")



# Function to grab all chapters of a comic
def grab_chapters(url):
	base_link = 'https://comick.app'
	response = scrape(url)

	if not response.ok:
		logging.info(f"[x] Something went wrong. Status: {response.status_code}")
		return None

	# Get JSON data from the response
	chapters = get_json_data(response)
	
	print("JSON data: ",chapters)
	chap_num   = chapters['props']['pageProps']['chapter']['chap']
	comic_name = chapters['props']['pageProps']['chapter']['md_comics']['title']	
	link_name  = chapters['props']['pageProps']['chapter']['md_comics']['slug']
	
	chapters = chapters['props']['pageProps']['chapters']
	chapters = chapters[::-1]


	new_data = {}
	for i in chapters:
		chap = i['chap']
		hid  = i['hid']
		chap_link = f'https://comick.app/comic/{link_name}/{hid}-chapter-{chap}-en'
		new_data[chap] = chap_link


	# Ask the user if they want to download from the current chapter
	choice = input(f"Wanna download from chapter {chap_num}? [y/n]: ")
	start_from_this_chapter = True if choice=='y' else False

	return [new_data, comic_name, new_data, chap_num, start_from_this_chapter]


# Handles Errors of grab chapters
def handle_grab_chapters(url):
	try:
		result = grab_chapters(url)
		
		if result==None:
			return headless.grab_chapters(url)

	except KeyError:
		logging.error(f"Failed to gather chapter links because of corrupted json file.")
		logging.info("Switching to headless mode.")

		return headless.grab_chapters(url)

# Handles Errors of download_comic
def handle_Download_Comic(url,chapter_num,comic_name):
	try:
		return download_comic(url, chapter_num, comic_name)
	except Exception:
		logging.error(f"Failed to download chapter {chapter_num}.")
		logging.info("Switching to headless mode.")
		return headless.download_comic(url, chapter_num, comic_name)

# Function to download the comic
def download():

	url = input("Enter the Url of any chapter of the comic: ")

	result = handle_grab_chapters(url,2)
	if result == None:
		logging.error(f"CORRUPTED JSON: {url}")
		logging.info(f"Exiting the program. Please try again later.")
		os._exit(1)

	new_data, comic_name, chapters, chap_num, start_from_this_chapter = result[0],result[1],result[2],result[3],result[4]

	makedir('Comics')
	makedir(f'Comics/{comic_name}')

	filtered_chapters = (chapter_num for chapter_num in chapters if not start_from_this_chapter or float(chapter_num) >= float(chap_num))

	for chapter_num in filtered_chapters:
		res = handle_Download_Comic(chapters[chapter_num], chapter_num, comic_name,2)
		if res == 'nope':
			logging.warning(f"Chapter {chapter_num} can't be downloaded.")
			logging.info(f"Skipping Chapter {chapter_num}")
			continue


# Shown at the start of program 
def dashboard():
	print("[========== Comic downloader ============]")
	print("[                                        ]")
	print("[    Press 1 to download comic.          ]")
	print("[    Press 2 to read downloaded comics.  ]")
	print("[                                        ]")
	print("[========================================]")

# Function that handles downloading and displaying comics
def main():
	dashboard()
	
	option = input("[*] Enter:")
	while option not in ['1','2']:
		print("\n\n[x] INVALID INPUT. Please enter 1 or 2.\n\n")
		dashboard()
		option = input("[*] Enter:")

	if option == '1':
		download()
	else:
		display.display()



if __name__ == '__main__':
	main()
	