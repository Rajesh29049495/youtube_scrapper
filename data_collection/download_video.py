import os
from flask import send_file
from pytube import YouTube, exceptions
from io import BytesIO

def resolution_generator(resolutions):             ##it is a good prcatice to use a generator instead of creating a list holding all the resolution values, as the generators are lazily evaluated which means that the values are computed o demand rather tha all at once. If we have large number of resolutions in our list, creating the list will require a significant amount of memory. However when we use generator we can iterate through the values one at a time, and each resolution is generated only when it is needed.. here although resolutions are less i could haev simply created a list of them and called them in teh function below one by one according to teh need, but still using generators is a good practice.
    for res in resolutions:
        yield res


def download_video(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        filename = f"{video_id}.mp4"
        buffer = BytesIO()                                             ##a BytesIP object, which is an im-memory buffer that can eb used to read/write bytes, in this code later on `stream_to_buffer()` method is used to write the content of the videostream to the buffer in memory. the reason for doing this is that it allows the program to read and manipulate the video stream content without writing it to disk first. thsi helpful when writing teh video to disk is not desitable such as when program running on a server with limited disk space
        rgen = resolution_generator(['360p', '480p', '720p', '144p'])

        yt_video = YouTube(url)
        video = None

        while video is None:
            res = next(rgen)
            print('trying ', res)
            try:
                video = yt_video.streams.get_by_resolution(res)
            except StopIteration:
                print('Could not manually select the proper resolution\nRetrying with the highest resolution')
                try:
                    video = yt_video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()                    ##If a StopIteration exception occurs when attempting to retrieve a video stream by resolution, the code will attempt to retrieve the highest resolution stream using this code. This code filters the available video streams to include only those that are progressive MP4 files, and then sorts them by resolution in descending order. The .first() method returns the first stream in the list, which should be the highest resolution stream available.
                except Exception as e:
                    return "Unable to download video"                                               ##if any error occur then due to this return statement the while loop will terminate giving thhis message, even if the condition video = None is still true
            except exceptions.LiveStreamError as e:
                return f"video: {video_id} is streaming live and cannot be loaded"                   ## in this case also if this error occurs then due t teh use of this return statemet teh while loop will terminaet even if the video = None condition is still true
                                                                                                ## Also note if these return statement in executed inside the while loop while handling the exception then the while loop will terminate and also the function will terminate returning the error message and the file variable back at the app.py will be assigned teh error message and taht will be shown to the client who had made this downlaod request, but if the while loop is executed properly then the code written below will be further executed
        video.stream_to_buffer(buffer)                                     ##the `stream_to_buffer()` method is actually a built_in method of the `pytube.Stream` class{which is part of pytube library}. it writes the stream content to a buffer in memory, which can then be read an dmanipulated by the program
        buffer.seek(0)                                                     ##this line sets the buffer's position to the beginning of the buffer so that it can be read from the start

        return send_file(buffer, as_attachment=True, download_name=filename)                ##the `semd_file()` function is used to send the contents of the buffer back to the client as a file attachment. The `as_attachment=True` parameter tells Flask to treat th efile as an attachmnet, which will prompt th euser to download the file instead of displaying it in teh browser. the `download_name` parameter specifies the name of the file that will be downloaded by the user. {in this case, it is set to teh name of the video file with a .mp4 extension}
    except Exception as e:
        print(e)