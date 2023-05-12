import os



# Function to extract comic name from url
def get_name(url):
    name = url.split('/')[-2]
    name = " ".join(name.split('-')[1:-2])
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
        <div class="content">"""

    # List and sort the image files in the specified path
    images = [i for i in os.listdir(path) if i.endswith('.png') or i.endswith('.jpg')]
    images = sort(images,'img')

    # Add an img tag for each image in the HTML file
    for i in images:
        html += f"\n          <img src=\"{path+'/'+i}\">"

    # Close the HTML tags
    html += '\n       </div>\n'
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
def which_chapter(reading,chapters):
    length   = len(chapters)

    display_chapters(reading,chapters,length)

    option = input("[*] Enter the chapter number: ")

    while not option in chapters:
        print(f"[x] There's no {option} chapter.\n    Please try again.")
        input(f"[-] Press Enter: ")
        
        display_chapters(reading,chapters,length)
        option = input("[*] Enter the chapter number: ")

    return chapters.index(option)

# Function to open provided path of html in browser
def open_in_browser(path):
    os.system(f"explorer {path}")

# Function to get chapters of selected comic
def get_chapters(comic):
    chapters = os.listdir(f'Comics/{comic}')
    chapters = sort(chapters,'folder')
    return chapters


# Function to open comic from chapter 'start'
def read_this_chap(start,comic,chapters):
    for i in chapters[start:]:
        # Rewrite the html with the selected comic's chapter
        path = f"Comics/{comic}/{i}"
        create_HTML(path)

        file = "Main_Display.html"
        print(f'\n[+] Chapter {i} of {comic}')
        open_in_browser(file)
        c=" "
        
        while c not in ['','1','2','q']:
            if i != chapters[-1]:
                msg =  "\n[*] Press 1 to read another comic.\n"
                msg +=   "[*] Press 2 to choose another chapter.\n"
                msg +=   "[*] Press Enter to continue to the next chapter.\n"
                msg +=   "[*] Press q to quit.\n" 
                msg += "\n[*] Enter: "
            else:
                msg  = "\n[+] This is the final chapter of the comic.\n"
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
def handle_choice(c,info):
    if c=='1':
        display()
    elif c=='2':
        reading,chapters,place = info[0],info[1],info[2]
        chapters = get_chapters(reading)
        # Display chapters of selected comic
        place = which_chapter(reading,chapters)
        c=read_this_chap(place,reading,chapters)
        handle_choice(c,info)
    elif c=='q':
        print("[~] Closing the program.")
        return

# Function to display downloaded comics
def display():
    # Prompt user to select comic, they want to read
    reading = which_comic()

    # Get a list of chapters of selected comic
    chapters = get_chapters(reading)

    # Display chapters of selected comic
    place = which_chapter(reading,chapters)

    c=read_this_chap(place,reading,chapters)
    info = [reading,chapters,place]
    handle_choice(c,info)
