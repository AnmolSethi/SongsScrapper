import bs4
from datetime import datetime
from tqdm import tqdm
import requests

base_url = "http://shiavoice.com"
urlList = []


def main():
    global urlList
    # Get menu links from the dropdown menu
    get_menu_links()

    print("\n[==========Main Execution==========]\n")
    for link in urlList:
        print(f"[=========={link}==========]")
        soup = get_content(link)
        fetch_data(soup)

    with open("cat_list.txt", "r") as f:
        cat_list = f.readlines()
        f.close()

    print("\n[==========Category List==========]\n")
    for cat in cat_list:
        link = cat.replace("\n", "")
        print(f"[=========={link}==========]")
        soup = get_content(link)
        fetch_data(soup)

    print("\n[==========Generating Download Links==========]\n")
    get_download_link()

    print("\n[==========Starting Downloading==========]\n")
    with open("dowload_links_list.txt", "r") as f:
        download_links = f.readlines()
        f.close()

    for songURL in download_links:
        download_data(songURL)

    print('Songs downloaded succesfully!!!')
    print("\nPress any key to exit")


def get_content(url):
    res = requests.get(url)

    if res.status_code == 200:
        return bs4.BeautifulSoup(res.text, "html.parser")
    else:
        print(f"Status Code: {res.status_code}\nError: {res.content}")


def get_menu_links():
    global urlList
    global base_url

    soup = get_content(base_url)
    menuLinks = soup.find("ul", attrs={"id": "menulinks"})
    [urlList.append(a_tags.get('href')) for a_tags in menuLinks.findAll("a")]


def get_download_link():
    with open("play_list.txt", "r") as f:
        play_list = f.readlines()
        f.close()

    with open(r"dowload_links_list.txt", "a+") as file:
        for link in play_list:
            link = link.replace("\n", "")
            print(f"\n============{link}============\n")
            soup = get_content(link.strip())

            download_link = soup.find('audio', id="PlayerSound").source.get('src')

            file.write(f"{download_link}\n")
    file.close()


def write_to_cat_list(cat_list):
    with open(r"cat_list.txt", "a+") as file:
        # file.truncate(0)
        [file.write(f"{cat}\n") for cat in cat_list]
        file.close()


def write_to_play_list(play_list):
    with open(r"play_list.txt", "a+") as file:
        # file.truncate(0)
        [file.write(f"{play}\n") for play in play_list]
        file.close()


def fetch_data(soup):
    # Get all anchor tags from the url
    a_tags = soup.find_all('a')

    play_list = []
    cat_list = []

    for link in a_tags:
        data = link.get('href')
        if "http" in data:
            if "play" in data:
                play_list.append(data)
            elif "cat" in data:
                cat_list.append(data)

    write_to_play_list(play_list)
    write_to_cat_list(cat_list)


def download_data(songURL):
    fileSizeRequest = requests.get(songURL, stream=True)
    fileSize = int(fileSizeRequest.headers['Content-Length'])
    fileName = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')
    t = tqdm(total=fileSize, unit='B', unit_scale=True, desc=fileName, ascii=True)
    with open(f"songs/{fileName}.mp3", 'wb') as f:
        for data in fileSizeRequest.iter_content(1024):
            t.update(len(data))
            f.write(data)
    t.close()


if __name__ == '__main__':
    main()
