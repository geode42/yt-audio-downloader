from typing import BinaryIO
import pyperclip
import pytube
from os.path import isfile, expanduser
from time import time
import platform
import sys
import shutil

# This is useful in general
CLEARLINESTRING = '\033[2K\r' # "\033[2K" clears the entire line ("\r" only clears the line up to the cursor's current position), "\r" moves the cursor back to the start of the line

OUTPUT_LOCATION = expanduser('~/Downloads')

url = pyperclip.paste()
if len(url) == 11: url = 'v=' + url # pytube requires the url to be at least v=vid_id, I think the vid_id should be enough though

def on_progress(chunk: bytes, file_handler: BinaryIO, bytes_remaining: int):
	bytes_downloaded = audio_num_bytes - bytes_remaining
	PROGRESS_BAR_LENGTH = shutil.get_terminal_size((10, 20)).columns - 6 - 11
	bar = ''
	bar += '\033[2K\r'

	progress_bar_completed_color = f'\033[90m'
	progress_bar_not_completed_color = f'\033[2m'
	unit_color = f'\033[2m'
	
	characters_completed = int(bytes_downloaded / audio_num_bytes * PROGRESS_BAR_LENGTH)
	percent_completed = int(bytes_downloaded / audio_num_bytes * 100)
	
	time_left = round((time() - start_time) / bytes_downloaded * (audio_num_bytes - bytes_downloaded))


	bar += f'{percent_completed}{unit_color}%'.rjust(4 + len(unit_color)) + '  '

	bar += '\033[1m'
	if characters_completed == 0:
		bar += progress_bar_not_completed_color + '―' * PROGRESS_BAR_LENGTH
	elif characters_completed >= PROGRESS_BAR_LENGTH - 1:
		bar += progress_bar_completed_color + '―' * characters_completed + ' ' * (PROGRESS_BAR_LENGTH - characters_completed)
	else:  # Normal
		bar += progress_bar_completed_color + '―' * characters_completed + ' ' + progress_bar_not_completed_color + '―' * (PROGRESS_BAR_LENGTH - characters_completed - 1)
	
	bar += f'  \033[0m{time_left} {unit_color}seconds'

	print(bar + '\033[0m', end='')


# Init yt object
try:
	yt = pytube.YouTube(url, on_progress_callback=on_progress)
except pytube.exceptions.RegexMatchError:
	print(CLEARLINESTRING + "The URL isn't valid")
	sys.exit(1)

# Return friendlier error messages
try:
	yt.check_availability()
except pytube.exceptions.MembersOnly:
	print(CLEARLINESTRING + "This utility can't download member-only videos")
	sys.exit(1)
except pytube.exceptions.RecordingUnavailable:
	print(CLEARLINESTRING + 'This live stream recording is unavailable')
	sys.exit(1)
except pytube.exceptions.VideoUnavailable:
	print(CLEARLINESTRING + 'This video is unavailable')
	sys.exit(1)
except pytube.exceptions.VideoPrivate:
	print(CLEARLINESTRING + 'This video has been made private')
	sys.exit(1)
except pytube.exceptions.LiveStreamError:
	print(CLEARLINESTRING + "This stream can't be downloaded")
	sys.exit(1)

# Add a slash if there isn't one already
if platform.system() == 'Windows':
	if len(OUTPUT_LOCATION) > 0 and not (OUTPUT_LOCATION.endswith('/') or OUTPUT_LOCATION.endswith('\\')):
		OUTPUT_LOCATION += '\\'
else:
	if len(OUTPUT_LOCATION) > 0 and not OUTPUT_LOCATION.endswith('/'):
		OUTPUT_LOCATION += '/'

print(CLEARLINESTRING + 'Getting streams...', end='')
audiostream = yt.streams.filter(only_audio=True, is_dash=True).order_by('bitrate').last()
audio_num_bytes = audiostream.filesize

filename = audiostream.default_filename

try:
	start_time = time()
	print(CLEARLINESTRING + 'downloading...', end='')
	audiostream.download(OUTPUT_LOCATION, filename + '.webm')

	if isfile(OUTPUT_LOCATION + filename + '.webm'):
		print(f'\033[2K\rVideo downloaded at {OUTPUT_LOCATION + filename + ".webm"}')
	else:
		print(f'Video could not be downloaded')

except KeyboardInterrupt:
	print('\033[2K\rKeyboard Interrupt, canceling download...')
