import os
import math
from html2image import Html2Image
from moviepy.editor import *
import random
import shutil

DURATION = 60
END_SIZE = (720,1280)
row_char_width = 60
shorts_width = int(END_SIZE[0] / 2)
SCALE = 2


class Common():
    def __init__(self, submission_id,score,text="",subreddit=""):
        self.submission_id = submission_id
        self.score = score
        self.text = text
        self.subreddit = subreddit
        self.video_file_path = os.getcwd()+"/"+str(self.subreddit.display_name)+"/"+str(self.submission_id)+"/"
        self.audio_file_path = None
        self.image_height = 0
    
    def compute_height(self):
        pass
    
    def process(self):
        pass
    
    def screenshot(self):
        pass
    
    def getAFC(self):
        self.af = AudioFileClip(self.audio_file_path)
        return self.af
    
    def getIC(self):
        pass
    # Functions for sort algorithm uses
    def __lt__(self, obj):
        return ((self.score) < (obj.score))  
    def __gt__(self, obj):
        return ((self.score) > (obj.score))
    def __le__(self, obj):
        return ((self.score) <= (obj.score))  
    def __ge__(self, obj):
        return ((self.score) >= (obj.score))  
    def __eq__(self, obj):
        return (self.score == obj.score)

    
class Title(Common):
    def __init__(self, submission_id,score,text="",subreddit="",title=""):
        super().__init__(submission_id, score, text, subreddit)
        self.title = title
        self.audio_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.submission_id)+"/title.wav"
        self.compute_height()
        
    def compute_height(self):
        newlines=self.title.count("\n")
        strlen=len(self.title)
        rows = math.ceil(strlen/row_char_width)
        if self.text == "":
            self.image_height = 110+(rows*22)+(newlines*5)
        else:
            textrows = math.ceil(len(self.text) / 50)
            text_newlines = self.text.count("\n")
            self.image_height = 110+(rows*22)+(newlines*5)+(textrows*17)+(text_newlines*4)
     # Currently not in use. Need to re-integrate it.
    #def generateHTML(self,sub="",pid="",cid="",h=1):
    #    return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=self.subreddit,postid=self.submission_id,h=self.image_height)
    
    def process(self):
        self.screenshot()
        
    def screenshot(self):
        res = """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/?ref_source=embed&amp;ref=share&amp;embed=true" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=self.subreddit,postid=self.submission_id,h=self.image_height)
        hti = Html2Image(output_path=self.video_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as='title.png')
    
    def getIC(self,start_time=0):
        bi = ImageClip(self.video_file_path + '/title.png')
        bi = bi.set_duration(DURATION)
        bi = bi.set_start(start_time)
        self.bi = bi.resize(SCALE)
        return self.bi
    
    
    
class Comment(Common):
    def __init__(self, submission_id,score,text="",subreddit="", comment_id=""):
        super().__init__(submission_id, score, text, subreddit)
        self.comment_id = comment_id
        self.audio_file_path = os.getcwd() + "/" + str(self.subreddit.display_name)+ "/" + str(self.submission_id)+"/"+str(self.comment_id)+".wav"
        self.compute_height()
        
    def compute_height(self):
        newlines=self.text.count("\n")
        strlen=len(self.text)
        rows = math.ceil(strlen/row_char_width)
        self.image_height = 110+(rows*20)+(newlines*5)
        
    def generateHTML(self,sub="",pid="",cid="",h=1):
        return """<iframe id="reddit-embed" src="https://www.redditmedia.com/r/{sub}/comments/{postid}/comments/{commentid}/?depth=1&amp;showmore=false&amp;embed=true&amp;showmedia=false" sandbox="allow-scripts allow-same-origin allow-popups" style="border: none;" scrolling="no" width="360" height="{h}"></iframe>""".format(sub=sub,postid=pid,commentid=cid,h=h)
    def process(self):
        self.screenshot()
    def screenshot(self):
        res=self.generateHTML(self.subreddit,self.submission_id,self.comment_id,self.image_height)
        hti = Html2Image(output_path=self.video_file_path,size=(shorts_width,self.image_height))
        hti.screenshot(html_str=res,save_as=str(self.comment_id)+'.png')
    def getIC(self, start_time=0):
        bi = ImageClip(self.video_file_path + '/' + str(self.comment_id)+'.png')
        bi = bi.set_duration(self.af.duration)
        bi = bi.set_start(start_time)        
        self.bi = bi.resize(SCALE)
        return self.bi 

class MediaGroups():
    def __init__(self, title_ic, title_afc):
        self.title_image = title_ic
        self.title_audio = title_afc
        self.white_background = None
        self.groups = []
        self.cg = MediaGroup(self.title_image, self.title_audio)
        self.nsp = self.title_audio.duration
    def set_background_clip(self):
        self.cg.set_background_clip()
    def set_white_background(self, backg):
        self.white_background = backg
        self.cg.set_white_background(backg)
    def save(self):
        self.groups.append(self.cg)
    def save_and_init_new_group(self):
        self.save()
        self.cg = MediaGroup(self.title_image, self.title_audio)
        self.cg.set_background_clip()
        self.cg.set_white_background(self.white_background)
        
    def add_audio(self, afc):
        self.cg.add_audio(afc)
        
    def add_video(self, ic):
        title_offset = ((((END_SIZE[1] - self.cg.background_clip.h)-(self.title_image.h)) - ic.h)/2)+(self.title_image.h)
        ic_moved = ic.set_position((0, title_offset))
        self.cg.add_video(ic_moved)
        
    def add_av(self, comment):
        afc = comment.getAFC()
        if self.nsp + afc.duration > DURATION:       
#            print("Overflow")
#            self.save_and_init_new_group()
#            self.nsp = self.title_audio.duration
            return False
        ic = comment.getIC(self.nsp)
        self.add_audio(afc)
        self.add_video(ic)
        
        self.nsp = self.nsp + afc.duration
        return True
    def render_all(self, path, filename):
        if self.cg not in self.groups:
            self.save()
        for number, mg in enumerate(self.groups):
            mg.render(path+str(number)+filename)
    def get_upload_info(self):
        retval = []
        for i in self.groups:
            retval.append([i.rendered_video, i.tags])
        return retval
        
        
class MediaGroup():
    def __init__(self, title_ic, title_afc):
        self.background_clip = self.set_background_clip()
        self.white_background = None
        self.title_ic = title_ic
        self.title_afc = title_afc
        self.videos = []
        self.audios = []
        self.tags = []
        self.rendered_video = None
    def set_background_clip(self):
        os.chdir("Content")
        file = random.choice(os.listdir())
        os.chdir("../")
        self.background_clip = VideoFileClip("Content/"+file)
        clip_start = random.randint(0,int(self.background_clip.duration-(DURATION+1)))
        self.background_clip = self.background_clip.subclip(clip_start,clip_start+DURATION)
        self.background_clip = self.background_clip.resize(width=END_SIZE[0])
        self.background_clip = self.background_clip.set_position((0, (END_SIZE[1]-self.background_clip.h)))
        self.tags = get_tags(file)
    def set_white_background(self, backg):
        self.white_background = backg
    def add_audio(self, afc):
        self.audios.append(afc)
    def add_video(self, ic):
        self.videos.append(ic)
    def render(self, filepath):
        self.videos.insert(0, self.white_background)
        self.videos.insert(1, self.background_clip)
        self.videos.insert(2, self.title_ic)
        self.audios.insert(0, self.title_afc)
        
        videoclips = CompositeVideoClip(self.videos)
        audioclips = concatenate_audioclips(self.audios)
        videoclips = videoclips.set_audio(audioclips)
        
        # Trim clip in case audio doesnt go the full 60 seconds
        if audioclips.duration < DURATION:
            videoclips = videoclips.subclip(0, audioclips.duration)
        # If it is EXACTLY 60 seconds, make it 59.9 since youtube doesnt let 60 second vids into shorts (it thinks theyre longer i guess)
        else:
            videoclips = videoclips.subclip(0, DURATION-0.1)
            
        videoclips = videoclips.set_fps(30)
        videoclips.write_videofile(filepath, threads=6)
        
        self.rendered_video = filepath
    

def get_tags(filename):
    if "minecraft" in filename:
        return ['minecraft','gaming','parkour']
    elif 'satisfying' in filename:
        return ['satisfying','sosatisfying','mmm','relaxing']
    elif 'trackmania' in filename:
        return ['gaming','racing','trackmania','speedrun']












