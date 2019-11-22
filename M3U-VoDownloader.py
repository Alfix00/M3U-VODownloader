import re, sys, os.path, urllib.request
from os import system, name
from urllib.request import urlretrieve

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux
    else:
        _ = system('clear')


class Channel:
    def __init__(self, name, category, url):
        self.name = name
        self.category = category
        self.url = url
        self.format = str(url.split(".", 3)[-1])
        if self.format is "":
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
        file_name = LoadFile.check_m3u_file(self)
        if not file_name == "":
            f = open(file_name, "r")
            with open(file_name) as f:
                string_pattern = []
                for line in f:
                    string_pattern.append(line)
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


# Show Method
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
    counter = 0
    clear()
    print("[*] Loading Channels, please wait ...\n")
    for channel in channels:
        if isinstance(channel, Channel):
            counter += 1
            try:
                resp = urllib.request.urlopen(str(channel.getUrl()))
                size = round(int(resp.getheader('content-length')) / 1000000000, 2)
                channel.setSize(str(size))
            except:
                pass
            print("%s] %s --> [%s]" % (counter, str(channel.getName()), channel.getSize() + " [GB"))
    print("\nChannels in download list: "+str(counter))


def option_one(categories=[Category]):
    answer = 0
    if isinstance(categories, type([Category])):
        show_category_list(categories)
        answer = input("Show channels into a category? \n\n\t[1 = YES] - [other = NO]: ")
    if answer == '1':
        option_two(categories)


def option_two(categories=[Category]):
    choice = int(input("\nWhich category do you wanna see? [1 - " + str(len(categories) - 1) + "] :" ))
    print('\n')
    length = int(len(categories))
    if choice < 1 or choice > length:
        print("Index < 0 or index > " + str(len(categories) - 1))
    elif 1 <= choice < length:
        show_channel_category(categories.__getitem__(choice))
        add_to_list(categories.__getitem__(choice).getChannels())


def option_three(categories=[Category]):
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


def option_four(channels=[Channel]):
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



def reporthook(blocknum, blocksize, totalsize):              #I Use this method for the progress bar in urllib.request
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))


def option_five():
    global donwloadlist
    show_download_list(donwloadlist)
    answer = int(input("\nStart the download?\n\n\t [1 = YES] - [Other = NO] : "))
    if answer is 1:
        load_list = donwloadlist
        lock = False
        clear()
        print("[**] Press CTRL + C for stop the download and back to menu' [**]\n ")
        for channel in load_list:
            if isinstance(channel, Channel) and lock is False:
                try:
                    url = channel.getUrl()
                    print("\n> Downloading : " + channel.getName() + channel.getSize() + " [GB]")
                    urllib.request.urlretrieve(url, "./Download_folder/"
                                               + str(channel.getName() + "." + channel.getFormat()[:-1]), reporthook)
                    print("\nDownload completed!\n\n")
                    load_list.remove(channel)
                except:
                    if InterruptedError:
                        lock = True
                    elif not InterruptedError:
                        print("\n[!] Error while downloading " + channel.getName() + " [!]\n")
                        input("\n* Press any key to download next channel *")

        donwloadlist = load_list

    #Take the golbal variable "downloadList" and append the new passed list
def append_to_list(channel_list=[Channel]):
    global donwloadlist
    donwloadlist = donwloadlist + channel_list

donwloadlist = [Channel] #This is the global array of channels in download list.


def add_to_list(channels=[Channel]):
    download_list = [Channel]
    if int(len(channels)) == 0:
        print('Error to load channels')
    if int(len(channels)) > 0:
        answer = int(input('[*] You want to add a channel(s) to the download list?\n\n\t [1 = YES] - [2 = NO] : '))

        if answer == 1:
            answer_two = int(input('\nYou want to make a multiple selection?\n\n\t [1 = YES] - [2 = NO] : '))
            # ---------------------------Multiple download section--------------------------------#
            if answer_two == 1:
                answer_tree = int(input(
                    '\n[*] Set a selection method.\n\n[1 = Add by index] - [2 = Add by range] : '))
                # ------------------------|Single selection of links (e.g. list >: 1, 3, 5, 6) |--------------------------#
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
                # ----------------------|Download by index range (e.g: 1 to 10) |---------------------------------#
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
                # ----------------------|Download single link by index|-------------------------------------------#
                print('\nIndexes available [1 -' + str(len(channels)) + "]. \n")
                channel = int(input("Enter the ID of the channel you want to download: "))
                if channel > 0 and channel < int(len(channels)):
                    download_list.append(channels.__getitem__(channel))
                    append_to_list(download_list)
                print('Channel added succesfully! ')
        if answer == 2:
            print('Back to menu...')


def menu(categories=[Category], channels=[Channel]):
    exit = False
    download_list = [Channel]
    while exit is False:
        try:
            clear()
            print('GitHub: https://github.com/Alfix00')
            print('\n---------------| VodExplorer |------------\n')
            print('    1) Show Categories list.')
            print('    2) Show Channels into Categories.')
            print('    3) Search Categories by name.')
            print('    4) Search Channels by name.\n')
            print('    5) Show download list and download. \n')                              #Not finish yet
            print('    0) Exit.')
            print('--------------------------------------------[Dev by Alfix00]')
            print('Loaded: ')
            print('\tChannels: ' + str(len(channels)))
            print('\tCategories: ' + str(len(categories)))
            choice = int(input("\n\tScelta: "))
            clear()
            if choice == 0:
                print("\n\n-> Exit from the program!\n")
                exit = True
            if choice < 1 or choice > 5 and choice != 0:
                print('Error! back to menu... ')
            if choice == 1:
                option_one(categories)
            if choice == 2:
                option_two(categories)
            if choice == 3:
                option_three(categories)
            if choice == 4:
                option_four(channels)
            if choice == 5:
                option_five()
            if exit is False:
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n-> Exit from the program!\n")
            exit = True

        #except:
        #    input("\n[!] Utilizza i numeri della tastiera per navigare all'interno del menu' ")


def checkFolder():
    if not os.path.isfile("./Download_folder"):
        try:
            os.mkdir("Download_folder")
        except OSError:
            pass


def initialize():
    # START
    clear()
    try:
        checkFolder()
        channels = [Channel]
        channels = LoadFile().getChannels(channels)
        categories = LoadFile().getCategory(channels)
        print('Loading file, please wait...')
        categories = LoadFile().fill_categories(categories, channels)
        print('\nLoaded Succesfully!\n')
        menu(categories, channels)
    except Exception:
        print("\n\n> Exit from the program.\n")


initialize()
