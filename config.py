import sys

#General
fullscreen = False
column_order = ['subjectName','subjectCode','gender','age','handedness','video',
               'section','arousal','pleasure','trial','choice','gain',
               'loss','RT','pumps','explosion']    #dont change the names just change the order if you wish.
dollar_toman = 4200
font_color = [-1,-1,-1]                           #RGB value in normalized form for Black color
fixation_sleep_time = 0.5

#Video
which_video = 3                                 #set the number of video you wish to be played. 1:negative 2:positive 3:neutral
negative_video = 'videos/negative.mp4'             #video number 1
positive_video = 'videos/positive.mp4'             #video number 2
neutral_video  = 'videos/neutral.mp4'              #video number 3

if which_video == 1:
    video_name = 'negative'
    video_path = negative_video
elif which_video == 2:
    video_name = 'positive'
    video_path = positive_video
elif which_video == 3:
    video_name = 'neutral'
    video_path = neutral_video

#IGT
igt_skip = 0                                          #set to 1 if you dont want IGT experiment to show up
igt_deck1_all_losses = [0,0,0,0,0,1.5,2,2.5,3,3.5]
igt_deck2_all_losses = [0,0,0,0,0,0,0,0,0,12.5]
igt_deck3_all_losses = [0,0,0,0,0,0.25,0.5,0.5,0.5,0.75]
igt_deck4_all_losses = [0,0,0,0,0,0,0,0,0,2.5]
igt_deck1_gain = 1
igt_deck2_gain = 1
igt_deck3_gain = 0.5
igt_deck4_gain = 0.5 
igt_initial_liquidity = 20                            #initial liquidity
igt_total_number_of_trials = 5
igt_bg_color = [1,1,1]                                #RGB value in normalized form for White color
igt_font_color = [-1,-1,-1]                           #RGB value in normalized form for Black color
igt_sleep_time = 2                                    #gain and loss will appear on screen for this long
igt_card_back_path = 'images/IGT/back1.png'
igt_card_front_path = 'images/IGT/front1.png'

#BART
bart_skip = 0                                         #set to 1 if you dont want BART experiment to show up
bart_max_balloon_capacity = 128                       #Every balloon will definitly burst if you blow it up to this number
bart_blow_addition = 0.05                             #gained liquidity after each blow in a balloon
bart_bg_color = [1,1,1]                               #RGB value in normalized form for White color
bart_font_color = [-1,-1,-1]                          #RGB value in normalized form for Black color
bart_blowing_factor = sys.maxsize                     #increase this value to reduce the speed of blowing in balloon in case of holding space button. use 'sys.maxsize' to disable blowing multiple times in balloon in case of holding space button.
bart_total_number_of_trials = 5 
bart_rope_path = 'images/Bart/rope.png'
bart_balloon_path = 'images/Bart/balloon1.png'
bart_blow_sound = 0                                   #set to 0 if you dont want blowing sound to play
bart_blow_path = 'sounds/blow.mp3'
bart_burst_sound = 1                                  #set to 0 if you dont want bursting sound to play
bart_burst_path = 'sounds/bang.mp3'
bart_collect_sound = 0                                #set to 0 if you dont want collecting sound to play
bart_collect_path = 'sounds/collect.mp3'

#SAM #no need to change anything here
arousal_1_path = 'images/SAM/arousal/1.jpg'
arousal_2_path = 'images/SAM/arousal/2.jpg'
arousal_3_path = 'images/SAM/arousal/3.jpg'
arousal_4_path = 'images/SAM/arousal/4.jpg'
arousal_5_path = 'images/SAM/arousal/5.jpg'
pleasure_1_path = 'images/SAM/pleasure/1.jpg'
pleasure_2_path = 'images/SAM/pleasure/2.jpg'
pleasure_3_path = 'images/SAM/pleasure/3.jpg'
pleasure_4_path = 'images/SAM/pleasure/4.jpg'
pleasure_5_path = 'images/SAM/pleasure/5.jpg'
number1_unselected_path = 'images/Numbers/Unselected/1.png'
number2_unselected_path = 'images/Numbers/Unselected/2.png'
number3_unselected_path = 'images/Numbers/Unselected/3.png'
number4_unselected_path = 'images/Numbers/Unselected/4.png'
number5_unselected_path = 'images/Numbers/Unselected/5.png'
number6_unselected_path = 'images/Numbers/Unselected/6.png'
number7_unselected_path = 'images/Numbers/Unselected/7.png'
number8_unselected_path = 'images/Numbers/Unselected/8.png'
number9_unselected_path = 'images/Numbers/Unselected/9.png'
number1_selected_path = 'images/Numbers/Selected/1.png'
number2_selected_path = 'images/Numbers/Selected/2.png'
number3_selected_path = 'images/Numbers/Selected/3.png'
number4_selected_path = 'images/Numbers/Selected/4.png'
number5_selected_path = 'images/Numbers/Selected/5.png'
number6_selected_path = 'images/Numbers/Selected/6.png'
number7_selected_path = 'images/Numbers/Selected/7.png'
number8_selected_path = 'images/Numbers/Selected/8.png'
number9_selected_path = 'images/Numbers/Selected/9.png'