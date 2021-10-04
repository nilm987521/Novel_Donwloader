#!/usr/bin/env python3
# coding: utf-8

from bs4 import BeautifulSoup as bs
from requests import get ,post
from urllib.parse import quote
from tqdm import tqdm
import os
import re
import platform
import sys
from pathlib import Path

HOME_PATH = str(Path.home())
DOWNLOADS_DIR  = os.path.join(HOME_PATH,'Downloads')

def get_search_list(keyword:str) -> list:
    result_list =             []
    url =                     'https://www.ttkan.co/novel/search?q={0}'.format(keyword)
    search_request =          get(url)
    search_request.encoding = search_request.apparent_encoding
    search_request_bs =       bs(search_request.text, 'html5lib')
    novels_list =             search_request_bs.find_all('div',{'class':'pure-u-1-1 pure-u-xl-1-3 pure-u-lg-1-3 pure-u-md-1-2 novel_cell'})
    
    for novel in novels_list:
        info =       novel.find_all('li')
        novel_info = {'title': info[0].text,'url' :'https://www.ttkan.co/' + info[0].find('a')['href'], 'writer': info[1].text, 'info':info[2].text}
        result_list.append(novel_info)
    return result_list


def get_novel_chapters_list(novel_url:str) -> list:
    result_list =                   []
    chapter_list_request =          get(novel_url)
    chapter_list_request.encoding = chapter_list_request.apparent_encoding
    chapter_list_bs =               bs(chapter_list_request.text, 'html5lib')
    chapter_list =                  chapter_list_bs.find('div', {'class':'full_chapters'}).find_all('a')
    
    for chapter in chapter_list :
        if re.match(r'https://.*',chapter['href']) != None:
            result_list.append(chapter)
    
    return result_list


def download_novel(chapters_list:list, novel_name:str):
    DOWNLOAD_PATH =                       os.path.join(DOWNLOADS_DIR, novel_name)
    if os.path.isdir(DOWNLOAD_PATH) ==    False : os.mkdir(DOWNLOAD_PATH)
    index =                               1
    for i in tqdm(range(len(chapters_list))):
        chapter_path =                    os.path.join(DOWNLOAD_PATH,'{:4d}'.format(index) + '-' + chapters_list[i].text.replace(' ','-')+'.txt')
        chapter_url =                     chapters_list[i]['href']
        
        chapter_request =                 get(chapter_url)
        if chapter_request.status_code == 200:
            chapter_request.encoding =    chapter_request.apparent_encoding
            
            chapter_request_bs =          bs(chapter_request.text, 'html5lib')
            chapter_content =             chapter_request_bs.find('div', {'class': 'content'}).text.replace('\n','').replace(' ','')
                    
            with open(chapter_path, 'w') as file:
                file.write(chapter_content)
            file.close()
        index = index + 1


def sub_main(url:str, title:str):
    chapter_list = get_novel_chapters_list(url)
    print('開始下載：{}'.format(title))
    download_novel(chapter_list, title)


def clear_terminal():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def command_mode(url: str):
    try:
        clear_terminal()

        novel_url = url
        novel_request = get(novel_url)
        novel_request.encoding = novel_request.apparent_encoding
        novel_request_bs = bs(novel_request.text, 'html5lib')
        title = novel_request_bs.find('h1').text

        novel_request_bs = None
        novel_request = None

        sub_main(novel_url, title)

        sys.exit()
    except KeyboardInterrupt:
        clear_terminal()
        print('下載已終止，程式即將關閉，請多支持『天天看小說（https://www.ttkan.co）』')   


def console_mode():
    # console mode
    print('歡迎使用『天天看小說（https://www.ttkan.co）』下載器')
    print('預設下載路徑為：{}/小說名稱'.format(DOWNLOADS_DIR))
    try:
        while True: 
            user_input = input("請輸入小說名稱 或 作者名稱（輸入b離開程式）:")  #希望可以增價值些輸入網址後下載
            if user_input == 'b':
                print('程式已關閉，歡迎再次使用。')
                break

            novels_list = get_search_list(user_input) 
            if novels_list == []: 
                print('書名『{}』找不到。'.format(user_input))
                continue

            index = 1
            for novel in novels_list:
                print('({0})'.format(index) + '書名:' + novel['title'])
                print('   ' + novel['writer'])
                print('   ' + novel['info'])
                index += 1

            while True:
                range_list = []
                user_input = input("請輸入要下載的小說號碼（範例:1 或 1,3 或 4-7）（輸入b重新搜尋小說）:")
                if user_input == 'b' :
                    clear_terminal()
                    break   

                if re.match(r'\d*,\d*',user_input) == None and re.match(r'\d*-\d*', user_input) == None and re.match(r'^\d*$', user_input) == None:
                    print('輸入的格式錯誤。')
                    continue    

                try:
                    if int(user_input) < len(novels_list) or int(user_input) > 0:
                        range_list.append(range(int(user_input), int(user_input) + 1))
                    else:    
                        print('輸入的數字超過範圍')
                        continue

                except ValueError:
                    if user_input.find(',') == -1:
                        user_input_list = [user_input]
                    else:
                        user_input_list = user_input.split(',')


                    for _input in user_input_list:
                        if _input.find('-') == -1:
                            range_list.append(range(int(_input), int(_input) + 1))
                        else:
                            range_list.append(range(int(_input.split('-')[0]), int(_input.split('-')[1]) + 1))

                    if len(range_list) == 0:
                        print('請輸入數字（半形）')
                        continue                        

                books_list = []
                for books in range_list:
                    for book in books:
                        books_list.append([novels_list[int(book) - 1]['url'],novels_list[int(book) - 1]['title']])
                
                process = 0        
                for book in books_list:
                    print('總進度（{}/{}）'.format(process + 1, len(books_list)))
                    sub_main(book[0], book[1])
                    process += 1

    except KeyboardInterrupt:
        clear_terminal()
        print('下載已終止，程式即將關閉，請多支持『天天看小說（https://www.ttkan.co）』')    


def main():
    if len(sys.argv) > 1:
        command_mode(sys.argv[1])
    else:
        console_mode()


if __name__ == '__main__':
    main()

