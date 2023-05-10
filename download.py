import os
import time
import json
import logging
import requests
from pprint import pprint
from bs4 import BeautifulSoup

# Set up logging configuration
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)


def sort(l,is_images):
	for i in range(len(l)-1):
		for j in range(len(l)-i-1):
			
			if is_images:
				a = l[j][:l[j].index('.')]
				b = l[j+1][:l[j].index('.')]
			else:
				a=l[j]
				b=l[j+1]
			
			if not a.isdigit() or not b.isdigit():
				continue

			if int(a) > int(b):
				temp   = l[j]
				l[j]   = l[j+1]
				l[j+1] = temp

	return l

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
	images = sort(images,True)

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
def digForImageLinks(html):
	images = []
	soup = BeautifulSoup(html, 'html.parser')
	spec = {'class':''}
	soup = soup.find('div',spec).text
	for i in soup.findAll('img'):
		images += i.get('src')
	return images


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


def retry_til_eternal(url):
	try:
		return grab_chapters(url)
			
	except KeyError:
		logging.info(f"Failed to gather chapter links because of corrupted json file.")
		logging.info("Retrying in 5 seconds.")

		time.sleep(5)
		return retry_til_eternal(url)

def try_again(url,chapter_num,comic_name):
	try:
		return download_Comic(url, chapter_num, comic_name)
	except KeyError:
		logging.info(f"Failed to download chapter {chapter_num} because of corrupted json file.")
		logging.info("Retrying in 5 seconds.")

		time.sleep(5)
		return try_again(url, chapter_num, comic_name)

# Function to download the comic
def download():

	url = input("Enter the Url of any chapter of the comic: ")

	chapters,comic_name,chap_num, start_from_this_chap = retry_til_eternal(url)	

	makedir('Comics')
	makedir(f'Comics/{comic_name}')

	filtered_chapters = (chapter_num for chapter_num in chapters if not start_from_this_chap or float(chapter_num) >= float(chap_num))

	for chapter_num in filtered_chapters:
		
		try_again(chapters[chapter_num], chapter_num, comic_name)


def display_chapters(comic_name, chapters, length):
	print(f"Chapters of the {comic_name}")
	col_num = 2 if length%2 == 0 else 3
	i = 0
	for row in range(length+1//col_num):
		for col in range(col_num):
			if i>=length:
				break
			print(f"	Chapter {chapters[i]}",end='')
			i+=1
		print('')

def display_comics(comics,length):
	message =   '\n\n[========= Downloaded Comics ========]\n'
	
	for i in range(length):
		message += f"     {i}. {comics[i]}     \n"
	
	message+=       "======================================"

	print(message)

# Function to display downloaded comics
def display():
	# Display Downloaded Comics
	comics = os.listdir('Comics')
	length = len(comics)
	display_comics(comics,length)
	
	option = int(input("\n[*] Enter the number corresponding to the comic you want to read: "))
	
	while option > length or option < 0:
		print("[x] INVALID INPUT.\n    Please try again.")
		
		display_comics()
		option = int(input("\n[*] Enter the number corresponding to the comic you want to read: "))

	# Display chapters of selected comic
	reading  = comics[option]
	chapters = os.listdir(f'Comics/{reading}')
	chapters = sort(chapters,False)
	length 	 = len(chapters)

	display_chapters(reading,chapters,length)

	option = input("[*] Enter the chapter number: ")

	while not option in chapters:
		print(f"[x] There's no {option} chapter.\n    Please try again")
		display_chapters(reading,chapters)

		option = input("[*] Enter the chapter number: ")

	place = chapters.index(option)

	for i in chapters[place:]:
		path = os.path.abspath(f"Comics/{reading}/{i}/display.html")
		print(path)
		os.system(f"explorer {path}")
		input("[*] Press Enter to continue to the next chapter: ")


# shown at the beginning 
def dashboard():
	print("[========== Comic downloader ============]")
	print("[                                        ]")
	print("[    Press 1 to download comic.          ]")
	print("[    Press 2 to read downloaded comics.  ]")
	print("[                                        ]")
	print("[========================================]")

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
		display()



if __name__ == '__main__':
	main()
	