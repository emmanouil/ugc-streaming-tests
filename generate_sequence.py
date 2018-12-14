import sys
import json
import os
import datetime
import re
from logs import log

TEST = '33-FOV_ONLY'
INFILE = 'Scs' + TEST + '.json'
LOGFILE = 'python_script.log'
OUTDIR = "D:\\Gits\\ugc-streaming-tests\\out"
ASSETSDIR = "D:\\Gits\\ugc-streaming-tests\\assets"
PL_FILE = 'clips-list.txt'
V_OUT_FILE = 'clips' + TEST + '.mp4'
S_OUT_FILE = 'score' + TEST + '.csv'
MIN_LENGTH_DATA_S = 0
MIN_VIDEO_LENGTH_S = 77


##	Checks a file (or filename) for extension
#
#	Return the file NAME without the extension if true
#	Return None otherwise
def get_file_name(file_in, extension):
    if (type(file_in) is str):
        file_full_name = os.path.splitext(os.path.split(file_in)[1])
    else:
        file_full_name = os.path.splitext(os.path.split(file_in.name)[1])
    file_name = file_full_name[0]
    file_ext = file_full_name[1]
    if (file_ext != extension):
        return
    else:
        return file_name


def construct_filename(name_in, rep):
    if rep == 0:
        return name_in + '_720p_1800k.mp4'
    elif rep == 2:
        return name_in + '_240p_400k.mp4'
    else:
        log('Unknown representation ' + rep, -1)


##	Processes file
#
#	void
def process_file(f_in, extension):
    log('Processing file: ' + f_in + extension, 1)
    with open(OUTDIR + '/' + f_in + extension, 'r') as file_in:
        data = json.load(file_in)
        clips = []
        score_csv = 'Time (t_video), Stream ID, Rep, Score \n'    #used for score logging
        for elem in data:
            #first log scores
            try:
                score_csv += str(elem['t_elapsed']) + ', ' + elem['id'] + ', ' + str(elem['rep']) + ', ' + str(elem['Score']) + '\n'
            except KeyError:
                log('Skipped element in logging scores', 1)
            #then parse clips for building video sequence
            if len(clips) is 0:
                clips.append(elem)
            elif clips[len(clips) - 1]['index'] != elem['index'] or clips[
                    len(clips) - 1]['rep'] != elem['rep'] or elem['is_buffering'] != clips[len(clips) - 1]['is_buffering']:
                clips.append(elem)
            #exit the iteration when we havethe desired duration
            if (MIN_LENGTH_DATA_S and elem['t_elapsed'] > MIN_LENGTH_DATA_S):
                break
        #flush scores
        with open(OUTDIR + '/' + S_OUT_FILE, 'a') as sfile:
            sfile.write(score_csv)
        clip = {
            'start_vfile': clips[0]['t_abs'] - clips[0]['t_elapsed'],
            'start_abs': 0,
            'filename': construct_filename(clips[0]['id'], clips[0]['rep']),
            'duration': 0,
            'id': clips[0]['id'],
            'rep': clips[0]['rep'],
            'is_buffering': False
        }
        part_count = 0
        pl = ''
        for elem in clips:
            if elem['id'] != clip['id'] or elem['rep'] != clip['rep'] or elem['is_buffering'] != clip['is_buffering']:
                #flush previous clip
                clip['duration'] = elem['t_elapsed'] - clip['start_abs']
                if clip['is_buffering']:
                    #ffmpeg -ss 01:23:45 -i input -vframes 1 -q:v 2 output.jpg
                    extract_frame = 'ffmpeg.exe -i ' + ASSETSDIR + '/' + clip['filename'] + ' -ss ' + str(
                        clip['start_vfile']) + ' -vframes 1 -q:v 1 ' + OUTDIR + '/' + str(part_count) + '.jpg'
                    log(extract_frame, 0)
                    os.system(extract_frame)
                    str_to_run = 'ffmpeg.exe -loop 1 -i ' + OUTDIR + '/' + str(
                        part_count) + '.jpg' + ' -r 30 -preset slow -vf scale=-1:720 -c:v libx264 -b:v 10000k -ss ' + str(
                            clip['start_vfile']) + ' -t ' + str(clip['duration']) + ' ' + OUTDIR + '/' + str(part_count) + '.mp4'
                    pl += 'file ' + str(part_count) + '.mp4 \n'
                else:
                    str_to_run = 'ffmpeg.exe -i ' + ASSETSDIR + '\\' + clip[
                        'filename'] + ' -r 30 -preset slow -vf scale=-1:720 -c:v libx264 -b:v 10000k -c:a copy -ss ' + str(
                            clip['start_vfile']) + ' -t ' + str(clip['duration']) + ' ' + OUTDIR + '/' + str(part_count) + '.mp4'
                    pl += 'file ' + str(part_count) + '.mp4 \n'
                log(str_to_run, 0)
                #os.system('ffmpeg -i '+clip['filaname']+' -ss '+00:09+'' -t 5 guide-out-1.mp4')
                #start new clip
                clip['filename'] = construct_filename(elem['id'], elem['rep'])
                clip['start_vfile'] = elem['t_abs']
                clip['start_abs'] = elem['t_elapsed']
                clip['duration'] = 0
                clip['id'] = elem['id']
                clip['rep'] = elem['rep']
                clip['is_buffering'] = elem['is_buffering']
                part_count += 1
                os.system(str_to_run)
        with open(OUTDIR + '/' + PL_FILE, 'a') as plfile:
            plfile.write(pl)
        if (MIN_VIDEO_LENGTH_S):
            os.system('ffmpeg.exe -f concat -i ' + OUTDIR + '/' + PL_FILE + ' -t ' + str(MIN_VIDEO_LENGTH_S) + ' -c copy ' + OUTDIR + '/' +
                      V_OUT_FILE)
        else:
            os.system('ffmpeg.exe -f concat -i ' + OUTDIR + '/' + PL_FILE + ' -c copy ' + OUTDIR + '/' + V_OUT_FILE)

        #merge here


def main():
    #check if called for specific file
    #check this instead: https://docs.python.org/3/library/fileinput.html#module-fileinput
    file_in = open(OUTDIR + '/' + INFILE, 'r')
    file_name = get_file_name(file_in, '.json')
    if file_name is None:
        exit('Wrong filename')
    else:
        process_file(file_name, '.json')
    file_in.close()
    input('continue?')
    #That's All Folks!
    exit(0)


if __name__ == '__main__':
    main()
