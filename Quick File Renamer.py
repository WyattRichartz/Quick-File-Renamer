import os, time, threading
import win32gui as windows
from tkinter import Tk, Entry
from send2trash import send2trash

#*Need to install MediaInfo first: https://mediaarea.net/en/MediaInfo
#*file_size_threshold in kilobytes
#*For now, this software only works in Windows

#!Does not work on .flac files, have error handling for this/alternate way to scan files

#?Global Settings
analyzed_location = r'D:\Media HDD\Videos HDD'
RenameFiles, ScanForDuplicates = True, False

#?RenameFiles Settings
AnalyzeImages, AnalyzeVideos = True, True
Fullscreen, MuteAudio = True, False
AnalyzeSubfolders = False
CreateNewFolder = False #creates a new folder and puts media files in them to differentiate from files that you have tagged and ones you haven't
volume_level = 0 #0 is silence, 100 is full volume, int from 0-100

video_extensions, image_extensions, image_details_extensions, file_list = ['3g2', '3gp', 'a64', 'ac3', 'adts', 'adx', 'aiff', 'alaw', 'alp', 'amr', 'amv', 'apm', 'apng', 'aptx', 'aptx_hd', 'argo_asf', 'argo_cvg', 'asf', 'asf_stream', 'ass', 'ast', 'au', 'avi', 'avif', 'avm2', 'avs2', 'avs3', 'bit', 'caca', 'caf', 'cavsvideo', 'chromaprint', 'codec2', 'codec2raw', 'crc', 'dash', 'data', 'daud', 'dfpwm', 'dirac', 'dnxhd', 'dts', 'dv', 'dvd', 'eac3', 'f32be', 'f32le', 'f4v', 'f64be', 'f64le', 'ffmetadata', 'fifo', 'fifo_test', 'film_cpk', 'filmstrip', 'fits', 'flac', 'flv', 'framecrc', 'framehash', 'framemd5', 'g722', 'g723_1', 'g726', 'g726le', 'gif', 'gsm', 'gxf', 'h261', 'h263', 'h264', 'hash', 'hds', 'hevc', 'hls', 'ico', 'ilbc', 'image2', 'image2pipe', 'ipod', 'ircam', 'ismv', 'ivf', 'jacosub', 'kvag', 'latm', 'lrc', 'm4v', 'matroska', 'md5', 'microdvd', 'mjpeg', 'mkvtimestamp_v2', 'mlp', 'mmf', 'mov', 'mp2', 'mp3', 'mp4', 'mpeg', 'mpeg1video', 'mpeg2video', 'mpegts', 'mpjpeg', 'mulaw', 'mxf', 'mxf_d10', 'mxf_opatom', 'null', 'nut', 'obu', 'oga', 'ogg', 'ogv', 'oma', 'opus', 'psp', 'rawvideo', 'rm', 'roq', 'rso', 'rtp', 'rtp_mpegts', 'rtsp', 's16be', 's16le', 's24be', 's24le', 's32be', 's32le', 's8', 'sap', 'sbc', 'scc', 'sdl,sdl2', 'segment', 'smjpeg', 'smoothstreaming', 'sox', 'spdif', 'spx', 'srt', 'streamhash', 'sup', 'svcd', 'swf', 'tee', 'truehd', 'tta', 'ttml', 'u16be', 'u16le', 'u24be', 'u24le', 'u32be', 'u32le', 'u8', 'uncodedframecrc', 'vc1', 'vc1test', 'vcd', 'vidc', 'vob', 'voc', 'w64', 'wav', 'webm', 'webm_chunk', 'webm_dash_manifest', 'webvtt', 'wsaud', 'wtv', 'wv', 'yuv4mpegpipe', 'm4a', 'wma', 'aac'], ['raw', 'cr2', 'nef', 'orf', 'sr2', 'eps', 'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'webp', 'jfif', 'PNG'], ['bmp', 'gif', 'ico', 'jpeg', 'png', 'tiff', 'jpg'], []
is_window_open, is_window_close = threading.Event(), threading.Event()

def generate_file_list(directory):
    for file in os.listdir(directory):
        AnalyzeFile = False
        file_extension = file.rsplit('.', 1)[-1]
        if AnalyzeImages and AnalyzeVideos:
            if file_extension in image_extensions or file_extension in video_extensions:
                AnalyzeFile = True
        elif AnalyzeImages:
            if file_extension in image_extensions:
                AnalyzeFile = True
        elif AnalyzeVideos:
            if file_extension in video_extensions:
                AnalyzeFile = True
        if AnalyzeSubfolders:
            if os.path.isdir(f'{directory}\{file}'):
                generate_file_list(f'{directory}\{file}')
        if AnalyzeFile:
            file_list.append(f'{directory}\{file}')
    return file_list

def focus_window():
    while True:
        try:
            text_window = windows.FindWindow(0, "QuickRenamerText")
            windows.SetForegroundWindow(text_window)
            break
        except:
            time.sleep(0.001)

def get_windows_open(hwnd, ctx):
    if windows.IsWindowVisible(hwnd):
        window_name = windows.GetWindowText(hwnd)
        if window_name.find('QuickRenamerFFPlay') != -1:
            is_window_open.set()

def get_windows_close(hwnd, ctx):
    if windows.IsWindowVisible(hwnd):
        window_name = windows.GetWindowText(hwnd)
        if window_name.find('QuickRenamerFFPlay') == -1:
            is_window_close.set()

def wait_for_open():
    is_window_open.clear()
    while True:
        windows.EnumWindows(get_windows_open, None)
        if is_window_open.is_set():
            break

def wait_for_close():
    is_window_close.clear()
    while True:
        windows.EnumWindows(get_windows_close, None)
        if is_window_close.is_set():
            break

def run_ffplay(media):
    appended_string = ' '
    if Fullscreen:
        appended_string += '-fs '
    if MuteAudio:
        appended_string += '-an '
    os.system(f'cmd /C ffplay "{media}" -window_title QuickRenamerFFPlay -loop 0 -nostats -volume {volume_level} {appended_string}')

def enter_press(window, entry):
    global new_file_name
    new_file_name = entry.get()
    window.destroy()

def control_press(window, entry):
    global DeleteFile
    DeleteFile = True
    window.destroy()

def escape_press(window, entry):
    window.destroy()
    os.system(f'cmd /C "TASKKILL /F /IM ffplay.exe /T"')
    quit()

def open_dummy_window():
    window = Tk()
    window.title("QuickRenamerText")
    window.geometry('100x50+50+50')
    entry = Entry(window, width= 40)
    entry.pack()
    window.bind('<Return>', lambda event, window=window, entry=entry : enter_press(window, entry))
    window.bind('<Control-Return>', lambda event, window=window, entry=entry : control_press(window, entry))
    window.bind('<Escape>', lambda event, window=window, entry=entry : escape_press(window, entry))
    entry.focus_set()
    window.after(1, focus_window)
    window.mainloop()

if analyzed_location[-1] == '\\':
    if analyzed_location[-2] == '\\':
        analyzed_location = analyzed_location[:-2]
    else:
        analyzed_location = analyzed_location[:-1]
file_list = generate_file_list(analyzed_location)
print(file_list)

if RenameFiles:
    if CreateNewFolder:
        if not os.path.isdir(f'{analyzed_location}\Renamed Files'):
            os.mkdir(f'{analyzed_location}\Renamed Files')
        ending_location = f'{analyzed_location}\Renamed Files'
    else:
        ending_location = analyzed_location

    for i in range(len(file_list)):
        print('here 6')
        DeleteFile = False
        previous_extension = file_list[i].rsplit('.', 1)[-1]
        run_ffmplay_thread = threading.Thread(target=run_ffplay, args=(file_list[i],))
        print('here 7')
        try:
            run_ffmplay_thread.start()
        except:
            continue
        print('wait for open...')
        wait_for_open()
        open_dummy_window()
        os.system(f'cmd /C "TASKKILL /F /IM ffplay.exe /T"')
        print('here 1')
        wait_for_close()
        print('here 2')
        if DeleteFile:
            while True:
                try:
                    send2trash(file_list[i])
                    break
                except:
                    time.sleep(0.001)        
        else:
            while True:
                try:
                    print('here 4')
                    print(file_list[i])
                    print(f'{ending_location}\{new_file_name}.{previous_extension}')
                    os.rename(file_list[i], f'{ending_location}\{new_file_name}.{previous_extension}')
                    print('here 10')
                    break
                except:
                    print('here 5')
                    time.sleep(0.001)
        print('here 3')