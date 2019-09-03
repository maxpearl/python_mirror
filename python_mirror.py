import time
import re
import os
from io import open as iopen
from urllib.parse import urlparse, urlsplit
import requests
from bs4 import BeautifulSoup
import click

@click.command()
@click.option('--wait', default=0, help='Number of seconds to wait between requests.', type=int) # Not implemented yetS
@click.option('--path', default='.', help="Local path to store files. NO trailing slash!")
@click.option('--subdomains', is_flag=True) # not implemented yet
@click.option('--url', required=True, type=str, help='URL of site to mirror')
@click.option('--replace_urls_str', type=str, help='Comma delimited list of URLs to replace with relative.')
@click.option('--debug', is_flag=True, default=False)

def mirror(wait, subdomains, url, replace_urls_str, path, debug):
    replace_urls = replace_urls_str.split(',')
    if debug:
        print(f"Replace urls: {replace_urls}")
    followed_links = []
    if path[-1] == '/':
        if debug:
            print("No trailing slash in path!")
        return
    if not replace_urls:
        replace_urls = [url]
    url_netloc = urlparse(url).netloc
    url_scheme = urlparse(url).scheme
    url_queue = [url]
    while url_queue:
        if debug:
            print(f"followed: {len(followed_links)}, queue: {len(url_queue)}")
        get_url = url_queue.pop(0)
        parsed_get_url = urlparse(get_url)
        if debug:
            print(parsed_get_url)
        if parsed_get_url.path == '/': # Skip
            continue
        if not parsed_get_url.netloc: #relative link
            new_get_url = url_scheme + '://' + url_netloc + '/' + get_url
        elif ((not parsed_get_url.scheme) or (parsed_get_url.scheme not in ['http', 'https'])): #missing scheme
            new_get_url = url_scheme + '://' + parsed_get_url.netloc + '/' + parsed_get_url.path
        else:
            new_get_url = get_url
        page = requests.get(new_get_url, allow_redirects=True)
        if page.status_code != 200:
            continue
        page_url = page.url
        content_type = page.headers.get('content-type')
        if 'html' not in content_type:
            # Just download it and store it
            store_page(page, page_url, path, debug)
        else:
            soup = BeautifulSoup(page.text, 'html.parser')
            links = soup.find_all('a')
            links = links + soup.find_all('link')
            images = soup.find_all('img')
            img_srcs = []
            for image in images:
                img_srcs.append(image.get('src'))
            scripts = soup.find_all('script')
            script_srcs = []
            for script in scripts:
                script_srcs.append(script.get('src'))
            links = links + img_srcs + script_srcs
            url_queue = process_links(
                queue=url_queue,
                url=page_url,
                links=links,
                followed=followed_links)
            new_page = soup.prettify()
            for replace_url in replace_urls:
                new_page = re.sub(replace_url, '', new_page)
            stored = store_page(new_page, page_url, path, debug)
            if stored:
                followed_links.append(get_url)
            else:
                if debug:
                    print("Not stored!")
                return
    return

def store_page(page, page_url, path, debug):
    # Store page 
    if isinstance(page, str): # a parsed page
        page_text = page
    parsed_url = urlparse(page_url)
    full_path = parsed_url.path
    full_path = re.sub('//', '/', full_path)
    filename = full_path.split('/')[-1]
    if '.html/' in full_path: # it's a parameter, skip it, but pretend it was stored.
        return True
    if '.' not in filename: # it's a path, not a filename:
        filename = 'index.html'
        directory_path = full_path
    else:
        directory_path = full_path.rsplit('/',1)[0]
    if not directory_path:
        local_path = path + directory_path + '/' + filename
    elif directory_path[-1] != '/':
        local_path = path + directory_path + '/' + filename
    else:
        local_path = path + directory_path + filename

    if directory_path:
        local_directory_path = path + directory_path
        if not os.path.exists(local_directory_path):
            try:
                os.makedirs(local_directory_path, exist_ok=True)
            except OSError as e:
                if debug:
                    print(f"Couldn't make the directory! {local_directory_path}: {e}")
                return False

    image_suffix_list = ['jpg', 'gif', 'png', 'jpeg']
    file_ext = filename.split('.')[-1]
    if file_ext in image_suffix_list: #image file save
        try:
            with iopen(local_path, 'wb') as f:
                f.write(page.content)
        except Exception as e:
            if debug:
                print(f"Couldn't write file! {e}")
            return False
    elif not isinstance(page, str): #other file save
        try:
            with open(local_path, 'w') as f:
                f.write(page.text)
        except Exception as e:
            if debug:
                print(f"Couldn't write file! {e}")
            return False
    else:
        try:
            with open(local_path, 'w') as f:
                f.write(page_text)
        except Exception as e:
            if debug:
                print(f"Couldn't write file! {e}")
            return False

    return True

def process_links(**kwargs):
    queue = kwargs['queue']
    for link in kwargs['links']:
        parsed_url = urlparse(kwargs['url'])
        url_netloc = parsed_url.netloc
        if not link:
            continue
        if isinstance(link, str):
            link_href = link
        else:
            link_href = link.get('href')
        parsed_link_url = urlparse(link_href)
        link_netloc = parsed_link_url.netloc
        if not link_netloc or (link_netloc == url_netloc): #relative link or same domain 
            #TODO deal with subdomains
            if not isinstance(link_href,str) or '?encoding' in link_href:
                continue
            if '#' in link_href: # no internal links
                continue
            new_item = True
            for queue_item in queue:
                if queue_item == link_href:
                    new_item = False
            for followed_item in kwargs['followed']:
                if followed_item == link_href:
                    new_item = False
            if new_item:
                queue.append(link_href)

    return queue

if __name__ == '__main__':
    mirror()