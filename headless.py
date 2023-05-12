from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 


# Remove links that point to the same chapter
def clean(l):
	clean_data = {}
	for i in l:
		key = i.split('/')[-1].split('-')[-2]
		try: key=int(key)
		except Exception: key=float(key)

		clean_data[key] = i

	return clean_data

# Find the base link of the comic from the url
def prepare(url):
	sections = url.split('/')
	
	# the url belong to the chapter and not to the comic itself
	if sections > 5:  
		url  = "/".join(sections[:5])
		url += "&chap-order=1"	

	# Make the website sort the chapters in ascending order
	elif sections == 5 and "&chap-order=1" not in url:  
		url += "&chap-order=1"
	
	else:
		return url

	return url

# Download chapter links from the url
def grab_chapters(url):
	
	url = prepare(url)

	options = Options()
	
	# enable headless mode in Selenium
	options.add_argument('--headless=new')

	# block image loading and javascript
	options.experimental_options['prefs'] = {
		'profile.managed_default_content_settings.images': 2,
		'profile.managed_default_content_settings.javascript': 2
	}



	# Launches headless browser
	driver = webdriver.Chrome(
		service=ChromeService(ChromeDriverManager().install()),
		options=options
	)

	# Start scraping
	driver.get(url)

	# Grab the links of chapters
	chapter_links = driver.find_elements(By.CSS_SELECTOR,'tr.group > td:nth-child(1) > a')
	chapter_links = [i.get_attribute('href') for i in chapter_links]

	# release the resources allocated by Selenium
	# and shut down the browser
	driver.quit()

	# clean up links with the same chapter
	chapter_links = clean(l)
	
	# return the directory
	return chapter_links


# Downloads the chapter inside url
def download_comic(url, chapter_num, comic_name):
	# enable headless mode in Selenium
	options = Options()
	options.add_argument('--headless=new')

	# Launches headless browser
	driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
	driver.get(url)

	image_links = driver.find_elements(By.CSS_SELECTOR,'')

	# release the resources allocated by Selenium
	# and shut down the browser
	driver.quit()
	