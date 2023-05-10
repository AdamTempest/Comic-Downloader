# Comic Downloader

 > Save the entire series in storage to read anywhere you want, antime you want.

After spending some time on comick.app, I found out that there is no feature to save all the chapters of the comic you are reading.
There IS a save button but it only save one chapter! That's pretty inconvenient if you are going places where wifi is not available.
And so I made this tool that can download any comic in the background.

## Supported Platforms

- Windows
- Linux
- MacOS

## Download

1. Clone this repository.

2. Download the dependencies using the following command.

    ```sh
    pip3 install -r requirements.txt
    ```

3. Run the download.py

    ```sh
    python3 download.py
    ```

4. It will ask for a link.

    ```sh
    Enter the Url of any chapter of the comic: 
    ```

    Open the [comick.app](https://comick.app) and navigate to the comic you want to download.
    Then click on any chapter of that comic.
    Copy the url and paste it into the field.

    ```sh
    Enter the Url of any chapter of the comic: https://comick.app/comic/00-grand-blue/72Poy-chapter-22-en
    ```

5. Hit Enter and it will start downloading. Enjoy.
