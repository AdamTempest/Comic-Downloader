import os
import time
import json
import logging
import requests
from bs4 import BeautifulSoup

# Set up logging configuration
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)

# Function to create an HTML file for displaying the downloaded comic images
def create_HTML(path):
	# HTML template
	html = """<!DOCTYPE html>
	<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<style>
			body:{
				background-color:black;
			}
		</style>
		<title>Comic</title>
	</head>
	<body>
		<div class="content">
	"""

	# List and sort the image files in the specified path
	images = [i for i in os.listdir(path) if i.endswith('.png') or i.endswith('.jpg')]
	images = sorted(images, key=lambda x: int("".join([i for i in x if i.isdigit()])))

	# Add an img tag for each image in the HTML file
	for i in images:
		html += f"			<img src='{i}'>\n"

	# Close the HTML tags
	html += '		</div>\n'
	html += '	</body>\n'
	html += '</html>'

	
	file = f"{path}/display.html"

	# Write the HTML template to a new file in the specified path
	with open(file,'w') as f:
		f.write(html)	


# Function to download a web page using requests
def scrape(target_url):
	response = requests.get(target_url)
	return response


# Function to create a new directory if it doesn't exist
def makedir(name):
	if not os.path.isdir(name):
		os.mkdir(name)


# Function to create a new requests session with custom User-Agent
def get_session():
	session = requests.Session()
	session.headers.update({"User-Agent": "Mozilla/5.0"})
	return session


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
def download_Comic(url,chapter_num,comic_name):

	# Scrape the chapter URL
	response  = scrape(url)
	base_link = "https://meo3.comick.pictures/"

	# Check if the response is successful
	if not response.ok:
		logging.info("[x] Website blocked the access. Status: ", response.status_code)
		return None

	# Grab JSON data from response
	data = get_json_data(response)

	logging.info(f'Downloaded {url}')

	 # Create a directory for the comic chapter	
	makedir(f'Comics/{comic_name}/{chapter_num}')

	# Extract the image URLs from the JSON data
	images = data['props']['pageProps']['chapter']['md_images']
	images = [i['b2key'] for i in images]

	# Download each image and save it in the chapter directory
	i=0
	for img_name in images:
		session = get_session()

		img_link = base_link + img_name
		img 	 = session.get(img_link)
		
		filepath = f"Comics/{comic_name}/{chapter_num}/{i}.png"
		
		# Retry the download if the initial request is not successful
		retry = 5
		while not img.ok and retry > 0:

			logging.info(f"[x] Website blocked the access. Status: {img.status_code}")
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

	# Create an HTML file to display the downloaded images
	path = f"Comics/{comic_name}/{chapter_num}"
	create_HTML(path)



# Function to grab all chapters of a comic
def grab_chapters(url):
	base_link = 'https://comick.app'

	response = scrape(url)

	if not response.ok:
		logging.info(f"[x] Something went wrong. Status: {response.status_code}")
		return None

	# Get JSON data from the response
	chapters = get_json_data(response)
	
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

	return new_data, comic_name, chap_num, start_from_this_chapter

def main():

	url = input("Enter the Url of any chapter of the comic: ")

	chapters,comic_name,chap_num, start_from_this_chap = grab_chapters(url)

	makedir('Comics')
	makedir(f'Comics/{comic_name}')

	filtered_chapters = (chapter_num for chapter_num in chapters if not start_from_this_chap or float(chapter_num) >= float(chap_num))

	for chapter_num in filtered_chapters:
		try:
			download_Comic(chapters[chapter_num], chapter_num, comic_name)
		except KeyError:
			logging.info(f"Failed to download chapter {chapter_num} because of corrupted json file.")
			logging.info(f"Skipping chapter {chapter_num}")


if __name__ == '__main__':
	main()
