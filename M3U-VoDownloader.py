import re, sys, os.path, urllib.request, time, threading, collections, numpy, asyncio, random
from threading import Thread
from os import system, name
from urllib.request import urlretrieve
from proxybroker import Broker

class Channel:
    def __init__(self, name, category, url):
        self.name = name
        self.category = category
        self.url = url
        self.format = str(url.split(".", 3)[-1])
        if self.format == "":
            self.format = "mp4"                                 #default format
        self.size_download = "Not Calculated yet"

    def getName(self):
        return self.name

    def getCategory(self):
        return self.category

    def getUrl(self):
        return self.url

    def getFormat(self):
        return self.format

    def getSize(self):
        return self.size_download

    def setName(self, name):
        if isinstance(name, str):
            self.name = name

    def setSize(self, size):
        if isinstance(size, str):
            self.size_download = size


class Category:

    def __init__(self, categoryName, channels=[Channel]):
        self.categoryName = categoryName
        self.channels = channels
        self.numberChannel = 0

    def getCategoryName(self):
        return self.categoryName

    def getChannels(self):
        return self.channels

    def getNumberChannel(self):
        return self.numberChannel

    def setChannels(self, channel=[Channel]):
        self.channels = channel

    def setCategoryName(self, channel=[Channel]):
        self.categoryName = channel

    def updateNumberChannel(self, new_number):
        self.numberChannel = new_number

#--------| Downloading and Loading channels |------------------------------------------------------------------#

size_file_m3u = 0

filledCategories = [Category]

fresh_proxy = []

status_proxy = False

threadLock = threading.Lock()

class downloadThread (Thread):

    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.channel = channel

    def run(self):
        url = self.channel.getUrl()
        if isinstance(self.channel, Channel):
            global fresh_proxy, status_proxy
            try:
                if status_proxy:
                    rand = random.randint(0, 10)
                    proto = fresh_proxy[rand].split('-')[0]
                    proxy = fresh_proxy[rand].split('-')[1]
                    p = urllib.request.ProxyHandler({proto: proxy})
                    opener = urllib.request.build_opener(p)
                    urllib.request.install_opener(opener)
                    threadLock.acquire()
                    print('[i] You are now downloading with the proxy: '+str(proxy)+"\n")
                    urllib.request.urlretrieve(url, "./Download_folder/"
                                               + str(self.channel.getName() + "." + self.channel.getFormat()[:-1]),
                                               reporthook)
                    threadLock.release()
                    print("\nDownload completed!\n\n")

                else:
                    print("\n> Downloading : " + self.channel.getName() +" | "+ self.channel.getSize() + " [GB]\n")
                    threadLock.acquire()
                    urllib.request.urlretrieve(url, "./Download_folder/"
                                               + str(self.channel.getName() + "." + self.channel.getFormat()[:-1]), reporthook)
                    threadLock.release()
                    print("\nDownload completed!\n\n")

            except:
                threadLock.release()
                if InterruptedError or KeyboardInterrupt:
                    print("\n\n[!] Download Stopped \n")
                    os.remove("./Download_folder/" + str(self.channel.getName() + "." + self.channel.getFormat()[:-1]))
                    lock = True
                else:
                    print("\n[!] Error while downloading " + self.channel.getName() + " [!]\n")
                    os.remove("./Download_folder/" + str(self.channel.getName() + "." + self.channel.getFormat()[:-1]))
                    input("\n* Press any key to download next channel *")


class LoadFile:

    def check_m3u_file(self):
        file_name = ""
        for file in os.listdir("."):
            find = False
            if file.endswith(".m3u") and find is False:
                file_name = str(file)
                find = True
        return file_name

    def getChannels(self, channels):
        global size_file_m3u
        file_name = LoadFile.check_m3u_file(self)
        if not file_name == "":
            f = open(file_name, "r")
            with open(file_name) as f:
                string_pattern = []

                for line in f:
                    string_pattern.append(line)
                size_file_m3u = len(string_pattern)

                for channel in string_pattern:
                    # this is the first pattern --> Extract channel name from channels.m3u line by line
                    channel_name = re.search('#EXTINF:-1 tvg-id="" tvg-name="(.+?)" tvg-logo=', channel)
                    if channel_name:
                        channel_name = channel_name.group(1)
                    elif channel_name is None:
                        # if the line doesn't contains the channel pattern, the 'line' point into a URL.
                        channel_link = channel
                    # this is the second pattern --> Extract category name
                    channel_category = re.search('.jpg" group-title="(.+?)"', channel)
                    if channel_category:
                        channel_category = channel_category.group(1)
                        cat = Category(channel_category, [Channel])
                    if channel_name and channel_link:
                        c = Channel(channel_name, channel_category, channel_link)
                        channels.append(c)
                    # End Channel build
                return channels
        elif file_name == "":
            print(".m3u file not found in folder or corrupt! \nYou need to have a single .m3u file in the folder!")
            input("\nPress any key to continue.")
            exit(0)

    def getChannels_alternative(self, channels):
        global size_file_m3u
        file_name = LoadFile.check_m3u_file(self)
        try:
            if not file_name == "":
                f = open(file_name, "r")
                with open(file_name) as f:
                    string_pattern = []

                    for line in f:
                        string_pattern.append(line)
                    size_file_m3u = len(string_pattern)
                    for channel in string_pattern:
                        pattern = channel.split(",")
                        channel_link = ''
                        if  channel.find('http') != -1:
                            # if the line doesn't contains the channel pattern, the 'line' point into a URL.
                            channel_link = channel
                        else:
                            channel_name = str(pattern[1])
                        channel_category = 'NaN'
                        if channel_name != '' and channel_link != '': 
                            c = Channel(channel_name, channel_category, channel_link)
                            channels.append(c)
                    # End Channel build
                    return channels
            elif file_name == "":
                print(".m3u file not found in folder or corrupt! \nYou need to have a single .m3u file in the folder!")
                input("\nPress any key to continue.")
                exit(0)
        except:
            pass

    def getCategory(self, channels=[Channel]):
        categories = [Category]
        array_category = []
        # check all channels and format string
        for channel in channels:
            if isinstance(channel, Channel):
                # Add a new category
                if channel.getCategory() not in array_category:
                    pattern = str(channel.getCategory())
                    formatted = re.sub(r'(?<=\d)[,\.]', '', pattern)
                    channel = channel.getCategory()
                    array_category.append(channel)
        temp = [Channel]
        # Create empty categories
        for array in array_category:
            categories.append(Category(str(array), temp))
        return categories

    def fill_categories(self, categories=[Category], channels=[Channel]):
        global filledCategories
        filledCategories = [Category]
        for category in categories:
            temp = [Channel]
            channelName = None
            for channel in channels:
                ok = False
                if isinstance(category, Category) and isinstance(channel, Channel):
                    if channelName is None:
                        channelName = channel.getCategory()
                    elif channelName is not None and channel.getCategory() == category.getCategoryName():
                        temp.append(channel)
                        if ok is False:
                            channelName = channel.getCategory()
                            ok = True
            new_cat = Category(channelName, temp)
            new_cat.updateNumberChannel(len(new_cat.getChannels()) - 1)
            if int(len(new_cat.getChannels())) > 1:
                filledCategories.append(new_cat)
        return filledCategories



#--------| Output for Category and Channels |------------------------------------------------------------------#

def show_category_list(categories=[Category]):
    counter = int(len(categories))
    for category in reversed(categories):
        if isinstance(category, Category):
            counter -= 1
            print("%s] - %s - N.Channels: [%s]" % (counter, str(category.getCategoryName()), category.getNumberChannel()))

    print("\n\nFormat: INDEX] TV-Series/Film - n.Channels [Numbers of Channels]\n")


def show_channels(channels=[Channel]):
    counter = int(len(channels))
    for channel in reversed(channels):
        if isinstance(channel, Channel):
            counter -= 1
            print("%s] %s" % (counter, str(channel.getName())))


def show_channel_category(category=Category):
    counter = int(len(category.getChannels()))
    for channel in reversed(category.getChannels()):
        if isinstance(channel, Channel):
            counter -= 1
            print("%s] - %s - URL: %s" % (counter, str(channel.getName()), channel.getUrl()))

    print("\n\tCATEGORY: " + str(category.getCategoryName())
          + "\t\t\t[Channels loaded : "
          + str(category.getNumberChannel())
          + "]\n")


def show_download_list(channels=[Channel]):
    global status_proxy
    counter = 0
    clear()
    print("[*] Loading Channels, please wait ...\n")
    for channel in channels:
        if isinstance(channel, Channel):
            try:
                counter += 1
                if status_proxy:
                    global fresh_proxy
                    rand = random.randint(0, 9)
                    proto = fresh_proxy[rand].split('-')[0]
                    proxy = fresh_proxy[rand].split('-')[1]
                    p = urllib.request.ProxyHandler({proto: proxy})
                    opener = urllib.request.build_opener(p)
                    urllib.request.install_opener(opener)
                    resp = urllib.request.urlopen(str(channel.getUrl()))
                    size = round(int(resp.getheader('content-length')) / 1000000000, 2)
                    channel.setSize(str(size))
                else:
                    resp = urllib.request.urlopen(str(channel.getUrl()))
                    size = round(int(resp.getheader('content-length')) / 1000000000, 2)
                    channel.setSize(str(size))
            except:
                pass

            print("%s] %s --> [%s]" % (counter, str(channel.getName()), channel.getSize() + " [GB"))

    print("\nChannels in download list: "+str(counter))

#--------| Menu Options |---------------------------------------------------------------------------------------------------#

no_category_mode = False

def option_one(categories=[Category]):
    answer = 0
    show_category_list(categories)
    answer = input("Show channels into a category? \n\n\t[1 = YES] - [other = NO]: ")
    if answer == '1':
        option_four(categories)



def option_two(channels=[Channel]):
    key = str(input("Type the keyword to be searched among the channels: "))
    filtred_channels = [Channel]
    for channel in channels:
        if isinstance(channel, Channel):
            if str(key).lower() in str(channel.getName()).lower():
                filtred_channels.append(channel)
    show_channels(filtred_channels)
    if len(filtred_channels) > 1:
        add_to_list(filtred_channels)
    elif len(filtred_channels) <= 1:
        print("\n[!] Channel not found!")


def option_three():
    global donwloadlist
    show_download_list(donwloadlist)
    try:
        answer = int(input("\nStart the download?\n\n\t [1 = YES] - [2] Clean DownloadList  [Other = NO]: "))
        if answer == 1:
            load_list = donwloadlist
            lock = False
            clear()
            print("[**] Press CTRL + C for stop the download and back to menu' [**]\n ")
            for channel in load_list:
                if isinstance(channel, Channel) and lock is False:
                    thread = downloadThread(channel)
                    thread.start()
                    thread.join()
                    load_list.remove(channel)
            donwloadlist = load_list
        if answer == 2:
            clean_list = [Channel]  
            donwloadlist = clean_list
            numpy.save("./settings/download list", donwloadlist)
            donwloadlist = numpy.load("./settings/download list.npy", allow_pickle=True)
            
            print("\nDownload list successfully cleaned.")
    except:
        print("Error while downloading files, please check if the contents of m3u file are online")
        input("\nPress any key to continue...")




def option_four(categories=[Category]):
    global no_category_mode
    choice = int(input("\nWhich category do you wanna see? [1 - " + str(len(categories) ) + "] :" ))
    print('\n')
    length = int(len(categories))
    if choice < 0 or choice > length:
        print("Index < 0 or index > " + str(len(categories) ))
    elif 0 <= choice < length and no_category_mode :
        show_channel_category(categories.__getitem__(choice))
        add_to_list(categories.__getitem__(choice).getChannels())

    


def option_five(categories=[Category]):
    key = str(input("Type the keyword to be searched among the categories: ").upper())
    filtred_cat = [Category]
    for category in categories:
        if isinstance(category, Category):
            if str(key).lower() in str(category.getCategoryName()).lower():
                filtred_cat.append(category)
    if len(filtred_cat) > 1:
        show_category_list(filtred_cat)
        answer = int(input("Show channels into a category?\n\n\t [1 = YES] - [other = NO] : "))
        if answer == 1:
            index = int(input("\nChose the index of category selected: [1 -%s]: " % (len(filtred_cat) - 1)))
            if index > 0 and index < len(filtred_cat):
                show_channels(filtred_cat.__getitem__(index).getChannels())
                add_to_list(filtred_cat.__getitem__(index).getChannels())
    elif len(filtred_cat) <= 1:
        print("\n[!] Category not found!")

#--------| Functions |-------------------------------------------------------------------------------------------------#

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def reload_m3u():
    global no_category_mode
    load = LoadFile()
    category = None
    channels = [Channel]
    channels = load.getChannels(channels)
    categories = load.getCategory(channels)
    if check_size_multimedia(channels) == False:
        channels = [Channel]
        channels = load.getChannels_alternative(channels)
        categories = [Category]
        category = Category('Nan',channels)
        category.setChannels(channels)
        no_category_mode = False
    else:
        categories = load.fill_categories(categories, channels)
        no_category_mode = True
    save_settings(channels,categories,category)
    menu(categories,channels,category)


def reporthook(blocknum, blocksize, totalsize):  #I Use this method for the progress bar in urllib.request
    global start_time
    readsofar = blocknum * blocksize
    if blocknum == 0:
        start_time = time.time()
        return
    if totalsize > 0:
        duration = time.time() - start_time
        progress_size = int(blocknum * blocksize)
        speed = int(progress_size / (1024 * duration))
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d MB / %d MB --- %d KB/s --- %d seconds passed" % (percent, len(str(totalsize)), readsofar*1e-6, totalsize*1e-6, speed, duration)
        sys.stderr.write(s)
        if readsofar >= totalsize:                # near the end
            sys.stderr.write("\n")
    else:                                         # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


def load_p():
    proxies = numpy.load("./settings/proxies.npy", allow_pickle=True)
    LoadFile.set_proxies(proxies)


def load_proxies():
    proxies = fresh_proxy
    path = './settings/'
    path_p = './settings/proxies.npy'
    if os.path.exists(path_p):
        load_p()
    else:
        if len(proxies) < 1:
            get_fresh_proxy()
            load_p()


async def save(proxies):
    global fresh_proxy
    proxy_arr = [None] * 10
    index = 0
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        proto = 'https' if 'HTTPS' in proxy.types else 'http'
        proxy_arr[index] = str(proto) + "-" + str(proto)+"://" + str(str(proxy.host)+":" + str(proxy.port))
        fresh_proxy = fresh_proxy + proxy_arr
        index = index + 1


def get_fresh_proxy():
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=10), save(proxies))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)


def clean_proxies():
    global fresh_proxy
    clean_list = []
    for proxy in fresh_proxy:
        if proxy is not None:
            clean_list.append(proxy)
    return clean_list


def append_to_list(channel_list=[Channel]):     #Take the golbal variable "downloadList" and append the new passed list.
    global donwloadlist
    donwloadlist = donwloadlist + channel_list
    numpy.save("./settings/download list", donwloadlist)


def check_dwn_list():
    if os.path.isfile('./settings/download list.npy'):
        global donwloadlist
        tmp = numpy.load("./settings/download list.npy", allow_pickle=True)
        download_list = [Channel]
        for channel in tmp:
            download_list.append(channel)
        donwloadlist = donwloadlist + download_list

donwloadlist = [Channel]                        #This is the global array of channels in download list.

def add_to_list(channels=[Channel]):
        download_list = [Channel]
        if int(len(channels)) == 0:
            print('Error to load channels')
        if int(len(channels)) > 0:
            answer = int(input('[*] You want to add a channel(s) to the download list?\n\n\t [1 = YES] - [2 = NO] : '))
            if answer == 1:
                answer_two = int(input('\nYou want to make a multiple selection?\n\n\t [1 = YES] - [2 = NO] : '))
                #------------------------------------| Multiple download section |--------------------------------------------#
                if answer_two == 1:
                    answer_tree = int(input(
                        '\n[*] Set a selection method.\n\n[1 = Add by index] - [2 = Add by range] : '))
                    #------------------------|Single selection of links (e.g. list >: 1, 3, 5, 6) |------------------------#
                    if answer_tree == 1:
                        exit = False
                        print('[i] Once finished adding the channels, type [0] to exit.')
                        print('\nIndexes available [1 -' + str(len(channels) - 1) + "]. \n")
                        while exit == False:
                            channel = int(input('Add ID channel : '))
                            if channel == 0:
                                exit = True
                            elif 0 < channel < len(channels):
                                download_list.append(channels.__getitem__(channel))
                        append_to_list(download_list)
                    #----------------------------|Download by index range (e.g: 1 to 10) |---------------------------------#
                    elif answer_tree == 2:
                        print('\n[*] Indexes available [1 - ' + str(len(channels) - 1) + "]. ")
                        first = int(input('\n\tSet first index ID: '))
                        second = int(input('\tSet last index ID: '))
                        if first < len(channels) and second < len(channels) and first < second and first > 0:
                            while first <= second:
                                download_list.append(channels.__getitem__(first))
                                first += 1
                            print('\nChannel added to list!\n')
                        elif first >= len(channels) or second >= len(channels):
                            print("Error, index(s) selected higher than the indexes available in the category.\n")
                        append_to_list(download_list)
                elif answer_two == 2:
                    #----------------------------|Download single link by index|-------------------------------------------#
                    print('\nIndexes available [1 -' + str(len(channels) - 1) + "]. \n")
                    channel = int(input("Enter the ID of the channel you want to download: "))
                    if channel > 0 and channel < int(len(channels)):
                        download_list.append(channels.__getitem__(channel))
                        append_to_list(download_list)
                    print('Channel added succesfully! ')
            if answer == 2:
                print('Back to menu...')

def proxy_mode():
    global fresh_proxy, status_proxy
    on_off_proxies()
    if status_proxy:
        print("> Getting proxies...")
        get_fresh_proxy()
        print("> Loading proxies... ")
        load_proxies()
        proxies = clean_proxies()
        fresh_proxy = proxies
        print("> Added 10 fresh proxies ! \n")
        print("[i] Proxy mode succesfully activated. ")
    else:
        print("[i] Proxy mode deactivated !")


#-------------------------| MENU |-------------------------------------------------------------------------------------#

def menu(categories=[Category], channels=[Channel], category=Category):
    global no_category_mode
    exit = False
    download_list = [Channel]
    while exit is False:
        try:
            clear()
            print('GitHub: https://github.com/Alfix00')
            print('\n---------------| VODownloader |------------\n')
            print('    1) Show Categories/Channel list.')
            print('    2) Search Channels by name.')
            print('    3) Show download list and download.\n ')
            if no_category_mode:
                print('    4) Show Channels into Categories.')
                print('    5) Search Categories by name.')
            print('    6) Reload m3u file.')
            #print('    7) On/Off Proxy Mode \n')                                           //Under maintenance
            print('    0) Exit.')
            print('---------------------------------------------[Dev by Alfix00]')
            #print('> Proxy Mode: '+str(status_proxy))
            print('\nLoaded: ')
            print('\tChannels: ' + str(len(channels)))
            if no_category_mode:
                print('\tCategories: ' + str(len(categories)))
            choice = int(input("\n\tChoice: "))
            clear()
            if choice == 0:
                print("\n\n-> Exit from the program!\n")
                exit = True
            if choice < 1 or choice > 7 and choice != 0:
                if choice != 0:
                    print('Error! back to menu... ')
            try:
                if choice == 1:
                    if no_category_mode == False:
                        print("ok")
                        channels = [Channel]
                        channels = category.getChannels()
                        show_channels(channels)
                    else:
                        option_one(categories)
            except:
                reload_m3u()
            if choice == 2:
                option_two(channels)
            if choice == 3:
                option_three()
            if choice == 4:
                option_four(categories)
            if choice == 5:
                option_five(categories)
            if choice == 6:
                clear()
                input("Press any key to reload m3u/m3u8 file...")
                reload_m3u()
            if choice == 7:
                proxy_mode()
            if exit is False:
                input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n-> Exit from the program!\n")
            exit = True


def checkFolder():
    if not os.path.isfile("./Download_folder"):
        try:
            os.mkdir("Download_folder")
        except OSError:
            pass

def checkSettings():
    path = './settings/'
    path_c = './settings/categories.npy'
    path_s = './settings/channels.npy'
    if os.path.exists(path_c) and os.path.exists(path_s) :
        return True
    return False

def on_off_proxies():
    global status_proxy
    status_proxy = not status_proxy

def save_settings(channels,categories,category):
    global size_file_m3u, no_category_mode
    if len(channels) > size_file_m3u / 3:           #If the channels are less than the real size, the script will not save any settings.
        if not os.path.isfile("./settings"):
            try:
                os.mkdir("settings")
            except OSError:
                pass
        numpy.save("./settings/channels", channels, allow_pickle=True)
        numpy.save('./settings/category', category, allow_pickle=True)
        numpy.save('./settings/categories', filledCategories, allow_pickle=True)

def check_size_multimedia(channels):
    global size_file_m3u
    if (len(channels) * 2) > size_file_m3u - 1:
        return True
    else:
        return False


def initialize():
    # START
    global no_category_mode
    clear()
    try:
        print('Loading file, please wait...')
        checkFolder()
        settings = False
        settings = checkSettings()
        category = None
        check_dwn_list()
        if settings is False:
            reload_m3u()
        else:   #This will save loading time!
            channels = numpy.load("./settings/channels.npy", allow_pickle=True)
            categories = numpy.load("./settings/categories.npy", allow_pickle=True)
            category = numpy.load("./settings/category.npy", allow_pickle=True)
            menu(categories, channels, category)
    except Exception as e:
        print("\n\n> Exit from the program.\n")
        print(e)


initialize()
