import sys

# General
language = "fa"  # Catalog in study/locales/: "fa" (Persian) or "en" (English).
controls = {
    "advance": "space",
    "pump": "space",
    "collect": "return",
    "skip": "i",
    "replay": "r",
    "pause": "p",
    "abort": "escape",
}
fullscreen = False
column_order = [
    "subjectName",
    "subjectCode",
    "gender",
    "age",
    "handedness",
    "video",
    "section",
    "arousal",
    "pleasure",
    "trial",
    "choice",
    "gain",
    "loss",
    "RT",
    "pumps",
    "explosion",
]  # dont change the names just change the order if you wish.
dollar_toman = 4200
font_color = [-1, -1, -1]  # RGB value in normalized form for Black color
fixation_sleep_time = 0.5

# Video
which_video = 3  # set the number of video you wish to be played. 1:negative 2:positive 3:neutral
negative_video = "assets/videos/negative.mp4"  # video number 1
positive_video = "assets/videos/positive.mp4"  # video number 2
neutral_video = "assets/videos/neutral.mp4"  # video number 3

if which_video == 1:
    video_name = "negative"
    video_path = negative_video
elif which_video == 2:
    video_name = "positive"
    video_path = positive_video
elif which_video == 3:
    video_name = "neutral"
    video_path = neutral_video
else:
    raise ValueError("which_video must be 1, 2, or 3")

# Shared native task presentation. Hex colors are converted to PsychoPy RGB by apps/desktop/presentation.py.
ui_theme = {
    "canvas": "#F5F7FC",
    "surface": "#FFFFFF",
    "deck": "#4960CF",
    "border": "#9AA8C4",
    "ink": "#1B2640",
    "muted": "#566585",
    "accent": "#4960CF",
    "gain": "#17734E",
    "loss": "#B13F4A",
    "on_deck": "#F2F4FF",
    "pattern": "#BBC6FF",
    "edge": "#D6DDF0",
    "balloon": "#ED735D",
    "balloon_edge": "#C65B49",
    "balloon_light": "#FFE7DD",
}
# Visual dimensions are fractions of the task viewport, independent of burst rules.
bart_presentation = {
    "min_width": 0.12,
    "max_width": 0.42,
    "min_height": 0.23,
    "max_height": 0.80,
    "center_y": 0.0,
}

# IGT
igt_skip = 0  # set to 1 if you dont want IGT experiment to show up
igt_deck1_all_losses = [0, 0, 0, 0, 0, 1.5, 2, 2.5, 3, 3.5]
igt_deck2_all_losses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 12.5]
igt_deck3_all_losses = [0, 0, 0, 0, 0, 0.25, 0.5, 0.5, 0.5, 0.75]
igt_deck4_all_losses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5]
igt_deck1_gain = 1
igt_deck2_gain = 1
igt_deck3_gain = 0.5
igt_deck4_gain = 0.5
igt_initial_liquidity = 20  # initial liquidity
igt_total_number_of_trials = 5
igt_bg_color = [1, 1, 1]  # RGB value in normalized form for White color
igt_font_color = [-1, -1, -1]  # RGB value in normalized form for Black color
igt_sleep_time = 2  # gain and loss will appear on screen for this long

# BART
bart_skip = 0  # set to 1 if you dont want BART experiment to show up
bart_max_balloon_capacity = (
    128  # Every balloon will definitly burst if you blow it up to this number
)
bart_blow_addition = 0.05  # gained liquidity after each blow in a balloon
bart_bg_color = [1, 1, 1]  # RGB value in normalized form for White color
bart_font_color = [-1, -1, -1]  # RGB value in normalized form for Black color
bart_blowing_factor = sys.maxsize  # increase this value to reduce the speed of blowing in balloon in case of holding space button. use 'sys.maxsize' to disable blowing multiple times in balloon in case of holding space button.
bart_total_number_of_trials = 5
bart_rope_path = "assets/images/bart/rope.png"
bart_balloon_path = "assets/images/bart/balloon-1.png"
bart_blow_sound = 0  # set to 0 if you dont want blowing sound to play
bart_blow_path = "assets/sounds/blow.mp3"
bart_burst_sound = 1  # set to 0 if you dont want bursting sound to play
bart_burst_path = "assets/sounds/bang.mp3"
bart_collect_sound = 0  # set to 0 if you dont want collecting sound to play
bart_collect_path = "assets/sounds/collect.mp3"

# SAM #no need to change anything here
arousal_1_path = "assets/images/sam/arousal/1.jpg"
arousal_2_path = "assets/images/sam/arousal/2.jpg"
arousal_3_path = "assets/images/sam/arousal/3.jpg"
arousal_4_path = "assets/images/sam/arousal/4.jpg"
arousal_5_path = "assets/images/sam/arousal/5.jpg"
pleasure_1_path = "assets/images/sam/pleasure/1.jpg"
pleasure_2_path = "assets/images/sam/pleasure/2.jpg"
pleasure_3_path = "assets/images/sam/pleasure/3.jpg"
pleasure_4_path = "assets/images/sam/pleasure/4.jpg"
pleasure_5_path = "assets/images/sam/pleasure/5.jpg"
number1_unselected_path = "assets/images/numbers/unselected/1.png"
number2_unselected_path = "assets/images/numbers/unselected/2.png"
number3_unselected_path = "assets/images/numbers/unselected/3.png"
number4_unselected_path = "assets/images/numbers/unselected/4.png"
number5_unselected_path = "assets/images/numbers/unselected/5.png"
number6_unselected_path = "assets/images/numbers/unselected/6.png"
number7_unselected_path = "assets/images/numbers/unselected/7.png"
number8_unselected_path = "assets/images/numbers/unselected/8.png"
number9_unselected_path = "assets/images/numbers/unselected/9.png"
number1_selected_path = "assets/images/numbers/selected/1.png"
number2_selected_path = "assets/images/numbers/selected/2.png"
number3_selected_path = "assets/images/numbers/selected/3.png"
number4_selected_path = "assets/images/numbers/selected/4.png"
number5_selected_path = "assets/images/numbers/selected/5.png"
number6_selected_path = "assets/images/numbers/selected/6.png"
number7_selected_path = "assets/images/numbers/selected/7.png"
number8_selected_path = "assets/images/numbers/selected/8.png"
number9_selected_path = "assets/images/numbers/selected/9.png"

# Results remain local. Relative paths are resolved against this repository.
output_directory = "results"
