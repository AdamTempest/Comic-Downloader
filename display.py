import os
import webbrowser

# Function to extract comic name from url of a chapter
def get_name(url):
    name = url.split('/')[-2]
    name = " ".join(name.split('-')[1:])
    return name

# Function to extract chapter number from url
def get_chap_num(url):
    name = url.split('/')[-2]
    num  = name.split('-')[-1]
    return num

# Function to sort a list of images or folders using bubble-sort method
def sort(l,format):
    for i in range(len(l)-1):
        for j in range(len(l)-i-1):
            
            if format=='img':
                a = l[j][:l[j].index('.')]
                b = l[j+1][:l[j+1].index('.')]
            if format=='imgPath':
                a = l[j].split('/')[-1]
                a = a[:a.index('.')]
                b = l[j+1].split('/')[-1]
                b = l[j+1][:l[j+1].index('.')]
            elif format == 'folder':
                a=l[j]
                b=l[j+1]
            
            # if not a.isdigit() or not b.isdigit():
            #     continue

            if float(a) > float(b):
                temp   = l[j]
                l[j]   = l[j+1]
                l[j+1] = temp

    return l

# Returns a list of chapters of selected comic
def get_chapters(comic):
    chapters = os.listdir(f'Comics/{comic}')
    chapters.remove('bookmark') if 'bookmark' in chapters else print('')
    chapters = sort(chapters,'folder')
    return chapters

# get a list of image paths from path
def get_image_paths(path):
    images = [i for i in os.listdir(path) if i.endswith('.png') or i.endswith('.jpg') or i.endswith('.jpeg')]
    images = sort(images,'img')
    images = ["file:///"+os.path.abspath(f"{path}/{i}") for i in images]
    return images

# get dictionary of image paths in the path of every chapters of the comic
def get_path_data(comic,chapters):
    data = {}
    for chapter_num in chapters:
        path = f"Comics/{comic}/{chapter_num}"
        data[int(chapter_num)] = get_image_paths(path)
    return data

# pass the dictionary containing paths of images of every chapters of the comic to the javascript
def pass_to_JS(comic,data):
    # read the content from JS file
    with open("web/scripts.js",'r') as f:
        content = f.readlines()
    
    # write the path data and comic name into the content of JS file
    content[0] = f"let chapters   = {data};\n"
    content[1] = f"let comic_name = \"{comic}\";\n"
    
    # rewrite the JS file with modified content
    with open('web/scripts.js','w') as f:
        f.writelines(content) 

# Displays Downloaded Comics
def display_comics(comics,length):
    message =   '\n\n[========= Downloaded Comics ========]\n\n'
    for i in range(length):
        message += f"     {i}. {comics[i]}     \n"
    message+=     "\n======================================"

    print(message)

# Interface for selecting comic to read
def which_comic():
    # get a list of downloaded comics
    comics = os.listdir('Comics')
    length = len(comics)
    
    # Display Downloaded Comics
    display_comics(comics,length)
    
    option = int(input("\n[*] Enter the number corresponding to the comic you want to read: "))
    
    while option > length or option < 0:
        print("[x] INVALID INPUT.\n    Please try again.")

        display_comics(comics,lengths)
        
        option = int(input("\n[*] Enter the number corresponding to the comic you want to read: "))

    return comics[option]

# Opens the path in browser
def open_in_browser(path):
    webbrowser.open(path)

# Main function for displaying downloaded comics
def display():
    # Prompt user to select comic, they want to read
    comic = which_comic()

    # Get a list of chapters of selected comic
    chapters = get_chapters(comic)

    # get paths of images of every chapters of the comic
    # {chapter_num:["imagePaths",'imagePaths'],
    #  chapter_num:["imagepaths",'imagePaths'], ...}
    data = get_path_data(comic,chapters)

    # pass the data to javascript
    pass_to_JS(comic,data)

    # renders the HTML
    open_in_browser('web/index.html')

    try:
        display()
    except KeyboardInterrupt:
        print("\n"*40)
        print("[~] Have a nice day :)")
        os._exit(1)