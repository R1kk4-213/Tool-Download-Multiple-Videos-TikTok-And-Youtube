import os.path
import random
import time
from random import randrange
from TikTokApi import TikTokApi
from moviepy.editor import *
from pytube import YouTube
from youtubesearchpython import VideosSearch

# path_download_tiktok -> the location to save video
system_dir = os.getcwd()
path_upload = os.path.join(system_dir, "bin", "uploads")
path_download_tiktok = os.path.join(system_dir, "bin", 'Downloads', "Media", "tiktok")
path_youtube = os.path.join(system_dir, "bin", 'Downloads', "Media", "youtube")
template_path = os.path.join(system_dir, "bin", "templates")
verifyFp = "verify_kv27hd5i_u2qczx0G_c85q_4Ewb_9RZX_a3u1nSbZrA8Y"  # fyp Cookies Tiktok
api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endpoints=True)  # set up


# start Download Video
def download_video_youtube(link):
    yt = YouTube(link).streams.get_highest_resolution()
    yt.download(path_youtube)


# get Url Youtube by keyword
def get_url_youtube_by_keyword(key_word, amount):
    videos_search = VideosSearch(key_word, limit=amount).result()
    content = videos_search['result']
    return content


# Download TIktok by keywords
def download_video_tiktok_by_hashtag(hashtag, count, start_index=0):
    video_result = api.by_hashtag(hashtag, count=count)  # get all video by hashtag
    count_file = 0
    if not os.path.isfile(
            os.path.join(path_download_tiktok, hashtag, "do_not_delete.txt")):  # if didnt downloaded before do this
        for i in range(count):
            video_bytes = api.get_video_by_tiktok(video_result[i])
            name = os.path.join(path_download_tiktok, hashtag, video_result[i]['id'] + ".mp4")
            os.makedirs(os.path.dirname(name), exist_ok=True)  # create folder for files hashtag in tiktok folder
            with open(name, "wb") as out:
                out.write(video_bytes)  # write video to mp4 file
            print("Downloaded: " + name)
    elif os.path.isfile(
            os.path.join(path_download_tiktok, hashtag, "do_not_delete.txt")):  # if downloaded before do this
        with open(os.path.join(path_download_tiktok, hashtag, "do_not_delete.txt"),
                  "r+") as file:  # open the file then download until reach the value had set
            video_deleted = file.read().split()
            for i in range(start_index, count):  # run loop to get bytes video
                if (video_result[i]['id'] + ".mp4" in video_deleted):
                    print(video_result[i]['id'] + " existed !")
                    count_file += 1  # count index to callback
                else:
                    video_bytes = api.get_video_by_tiktok(video_result[i])
                    name = os.path.join(path_download_tiktok, hashtag, video_result[i]['id'] + ".mp4")
                    os.makedirs(os.path.dirname(name),
                                exist_ok=True)  # create folder for files hashtag in tiktok folder
                    with open(name, "wb") as out:
                        out.write(video_bytes)  # write video to mp4 file
                    print("Downloaded: " + name)
            time.sleep(3)
            if count_file > 0:
                return download_video_tiktok_by_hashtag(hashtag, count_file + count,
                                                        start_index=count)  # call back existed File


# search top hashtag by term
def search_hashtag(term_of_hashtag):
    hashtag = api.search_for_hashtags(term_of_hashtag)
    list_title_hashtag = []
    for element in hashtag:
        list_title_hashtag.append(element['challenge']['title'])  # append title hashtag
    print("Các Top Hashtag của ", term_of_hashtag, "Là:", list_title_hashtag)
    return list_title_hashtag


# Show list video Downloaded
def show_list_video(hashtag, max_file):
    path = os.path.join(path_download_tiktok, hashtag)
    random_chose = []
    list_video = os.listdir(path)
    for i in list_video:
        if ".mp4" not in i:
            list_video.remove(i)

    print(list_video)
    if max_file > 0 and len(list_video) > 0:
        random_chose = random.sample(list_video, max_file)  # choose random video's name
        print("Trong folder:", path, "Đã chọn các File :{", random_chose, "}")  # show all video chose
    elif max_file == 0 and len(list_video) > 0:
        print("Trong folder:", path, "Đã chọn các File :{", random_chose,
              "}")  # if max_file variable == 0 return all values
    return random_chose


# resize video
def resize_video(hashtag, file_name):
    clip = VideoFileClip(os.path.join(path_download_tiktok, hashtag, file_name))
    return clip


# create transition effect for clip.
def transition_video(path=os.path.join(path_download_tiktok, "quack.mp4")):
    video = (VideoFileClip(path, target_resolution=(1920, 1080)))
    return video


# get file in folder then merge , with max_file
def tiktok_merge_video(hashtag, max_file, name_file, name_channel='', intro_path=''):
    watermark_text = TextClip("@" + name_channel, fontsize=65, color='black', stroke_width=3).set_opacity(0.5)
    background = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=10)  # black background
    intro_video = (VideoFileClip(intro_path).fx(vfx.resize, height=1080))  # intro video
    list_video = show_list_video(hashtag, max_file)  # get random video from folder hashtag
    video = []  # list save video to concatenate

    for video_in_list in list_video:
        video.append(VideoFileClip(os.path.join(path_download_tiktok, hashtag, video_in_list))
                     .fx(vfx.resize,
                         height=1080))  # tạo 2 biến clip và transition sau đó composite để không bị lỗi resolution
        video.append(transition_video())  # append transition

    video = concatenate_videoclips(video)  # concate all video
    final = CompositeVideoClip(
        [intro_video.set_end(intro_video.duration),
         background.set_position("center").set_start(intro_video.duration),
         video.set_position("center").set_start(intro_video.duration),
         watermark_text.set_start(intro_video.duration).set_duration(video.duration).set_position("top", "center"),
         ])  # composite intro vs video
    print(intro_video.duration + video.duration)
    final.write_videofile(os.path.join(path_upload, name_file),
                          threads=5,
                          bitrate="2000k",
                          audio_codec="aac",
                          codec="h264_nvenc",
                          )  # export file
    with open(os.path.join(path_download_tiktok, hashtag, "do_not_delete.txt"), "a+") as file:
        for i in list_video:
            os.remove(os.path.join(path_download_tiktok, hashtag, i))  # delete video downloaded
            file.write("\n" + i)
            print("video đã xóa: ", os.path.join(path_download_tiktok, hashtag, i))

def order_function():
    shift = 0
    try:
        while not int(shift) in range(1, 4):
            shift = int(input("Please enter your shift (1 - 4) :"))
        return shift
    except ValueError:
        print("That's not an int!")
        return order_function()

if __name__ == '__main__':


    hashtag = str(input("Type your hashtag or Keyword:"))
    print(''' Please choose which service do you want!
    1) Download video youtube by link:
    2) Download video youtube by keyword:
    3) Download video tiktok by hashtag:
    4) Search hashtag by terms:
    ''')




    value_order = order_function()
    print(value_order)
    if(value_order == 1):
        url_video = str(input("Type your Youtube URL:"))
        download_video_youtube(url_video)
    elif(value_order == 2):
        amount = int(input("Type number of videos you want to download: "))
        content = get_url_youtube_by_keyword(hashtag, amount)
        for i in content:
            print(i["title"], i["link"])

            download_video_youtube(i["link"])
    elif(value_order == 3):
        amount = int(input("Type number of videos you want to download: "))
        download_video_tiktok_by_hashtag(hashtag, amount)
    elif(value_order == 4):
        search_hashtag(hashtag)



#            Developing . Spoil: Merge multiple file to one video . With water mark and transition
    # while True:
    #     try:
    #         hashtag ="funnymoments"
    #         intro_path = os.path.join(template_path,"intro","intro2.mp4")
    #         download_video_tiktok_by_hashtag(hashtag, 10)
    #         tiktok_merge_video(hashtag, 10,str(random.randrange(999999999))+".mp4",name_channel,intro_path)
    #         break
    #     except Exception as e:
