import os
import webbrowser

# record the chap num of the comic
def record(chap_num,comic):
    chap_num = str(chap_num) if type(chap_num) != str else chap_num
    path     = f"Comics/{comic}/bookmark"

    with open(path,'w') as f:
        f.write(chap_num)

# read the record for the chapter num that's last read
def read_record(comic):
    path = f"Comics/{comic}/bookmark"

    if not os.path.exists(path):
        return None
    
    with open(path,'r') as f:
        num = f.read()
    return num

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

# Function to create an HTML file for displaying the downloaded comic images
def create_HTML(path):
    # HTML template
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel='stylesheet' href='web/styles.css'>
        <script src='web/scripts.js'></script>
        """
    html+=f"        <title>chapter {path.split('/')[2]} of {path.split('/')[1]}</title>"
    html+="""</head>
    <body>
        <div id="content">"""

    # List and sort the image files in the specified path
    images = [i for i in os.listdir(path) if i.endswith('.png') or i.endswith('.jpg')]
    images = sort(images,'img')

    # Add an img tag for each image in the HTML file
    for i in images:
        html += f"\n          <img src=\"{path+'/'+i}\">"

    # Close the HTML tags
    html += '\n       </div>\n'
    html += "   <button id='previous' onclick=previous()>Previous</button>\n"
    html += "   <button id='next' onclick=next()>Next</button>\n"
    html += '   </body>\n'
    html += '</html>'

    
    file = "Main_Display.html"

    # Write the HTML template to a new file in the specified path
    with open(file,'w') as f:
        f.write(html) 

# Function to add space to the end of the string
def addspace(msg,maxL):
    while len(msg)<maxL:
        msg+=" "
    return msg

# Function to display available chapters of selected comic
def display_chapters(comic_name, chapters, length):
    print(f"\nChapters of the {comic_name}")
    col_num = 2 if length%2 == 0 else 3
    i = 0
    for row in range(length+1//col_num):
        for col in range(col_num):
            if i>=length:
                break
            msg = f"    Chapter {chapters[i]}"
            msg = addspace(msg,20)
            print(msg,end='')
            i+=1
        if i>=length:
            break
        print('')
    print('\n')

# Function to display Downloaded Comics
def display_comics(comics,length):
    message =   '\n\n[========= Downloaded Comics ========]\n\n'
    
    for i in range(length):
        message += f"     {i}. {comics[i]}     \n"
    
    message+=     "\n======================================"

    print(message)

# Function for user to select comic to read
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

# Function for user to select chapter
def which_chapter(comic,chapters):
    length   = len(chapters)

    display_chapters(comic,chapters,length)

    past_chap = read_record(comic)

    if past_chap != None:
        print(f"[+] You were reading chapter {past_chap} last time.")
        
    option = input("[*] Enter the chapter number: ")

    while not option in chapters:
        print(f"[x] There's no {option} chapter.\n    Please try again.")
        input(f"[-] Press Enter: ")
        
        display_chapters(comic,chapters,length)
        option = input("[*] Enter the chapter number: ")

    return chapters.index(option)

# Function to open provided path of html in browser
def open_in_browser(path):
    webbrowser.open(path)
    #os.system(f"explorer {path}")

# Function to get chapters of selected comic
def get_chapters(comic):
    chapters = os.listdir(f'Comics/{comic}')
    chapters.remove('bookmark') if 'bookmark' in chapters else print('')
    chapters = sort(chapters,'folder')
    return chapters

# Function to open comic from chapter 'start'
def read_this_chap(start,comic,chapters):
    data = {}
    for chapter_num in chapters[start:]:
        # Rewrite the html with the selected comic's chapter
        path = f"Comics/{comic}/{chapter_num}"
        
        create_HTML(path)

        file = "Main_Display.html"
        print(f'\n[+] Chapter {chapter_num} of {comic}')
        
        # record the current chapter 
        record(chapter_num,comic)

        
        open_in_browser(file)
        c=" "
        
        while c not in ['','1','2','q']:
            if chapter_num != chapters[-1]:
                msg =  "\n[*] Press 1 to read another comic.\n"
                msg +=   "[*] Press 2 to choose another chapter.\n"
                msg +=   "[*] Press Enter to continue to the next chapter.\n"
                msg +=   "[*] Press q to quit.\n" 
                msg += "\n[*] Enter: "
            else:
                msg  =   "[+] This is the final chapter of the comic.\n\n"
                msg +=   "[*] Press 1 to read another comic.\n"
                msg +=   "[*] Press 2 to choose another chapter.\n"
                msg +=   "[*] Press Enter to quit.\n" 
                msg += "\n[*] Enter: "
        
            c = input(msg)
        
        if c in ['1','2']:
            return c
        if c=='q':
            return None

# Function to handle output of function read_this_chap
def handle_choice(c,comic,chapters):
    if c=='1':
        display()
    elif c=='2':
        # Display chapters of selected comic
        # Get the index of selected chapter number in chapters
        start_index = which_chapter(comic,chapters)
        
        # display the comic from selected chapter number
        c=read_this_chap(start_index,comic,chapters)
        
        handle_choice(c,comic,chapters)
    elif c=='q':
        print("[~] Closing the program.")
        return

# Function to display downloaded comics
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

    # Display chapters of selected comic and
    # Get the index of selected chapter number in chapters
    start_index = which_chapter(comic,chapters)

    # display the comic from selected chapter number
    c=read_this_chap(start_index,comic,chapters)
    handle_choice(c, comic, chapters)
