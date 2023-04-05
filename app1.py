from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session
from data_collection import get_channel_ids, get_playlist_ids, get_video_details, get_comments, download_video
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.getenv("app_secret_key")


@app.route("/home")
def home():
    return render_template("index.html", GitHubLink=os.getenv("GitHubLink"))


@app.route("/check", methods=["POST", "GET"])
def check():
    try:
        youtube_url = str(request.form['youtube_url'])
        session['username'] = youtube_url.split('/')[4]
        if len(youtube_url) != 0:
            session['channel_id'] = get_channel_ids.get_channel_ids(youtube_url)
            if session['channel_id'] == 'INVALID':
                return redirect(url_for('home'))
            else:
                return render_template("index.html", GitHubLink=os.getenv("GitHubLink"),
                                       status_comments="channel_id found: " + session['channel_id'])
        else:
            return redirect(url_for("home"))
    except Exception as e:
        print(e)
        return redirect(url_for("home"))


@app.route("/submit", methods=["POST", "GET"])
def submit():
    if session['channel_id'] == 'INVALID':
        return redirect(url_for("home"))
    else:
        session['playlist_id'] = get_playlist_ids.get_playlist_ids(session["channel_id"])
        if session['playlist_id'] == "INVALID":
            session["channel_id"] = "INVALID"
            return redirect(url_for("home"))
        else:
            session["videoCountRequest"] = int(request.form['videoCountRequest'])
            session["video_data"], channel_title = get_video_details.get_video_details(session["playlist_id"],
                                                                                       maxResults=session[
                                                                                           "videoCountRequest"])

            if session['video_data'] is None:
                session["channel_id"] = "INVALID"
                session['playlist_id'] = "INVALID"
                return redirect(url_for("home"))



            else:
                video_data = session['video_data']
                return render_template("index_table.html",  # table is rendered using "render_template" function.
                                       tables=[video_data.to_html(escape=False,                                                                                         # the "tables" argument of "render_template" function accepts a list of tables to render on the page. in this case only one table..,,,,#The table is created using the "to_html" method of the pandas DataFrame object. this method convert datafarme into html table.,,,,,,#setting "escape" to False means that any special characters in the table data will be included in the generated HTML code as-is, without being replaced with HTML entities. This can be useful for displaying code or including HTML code within the table data. However, it's important to ensure that the table data is properly sanitized to prevent potential security vulnerabilities. we set it to "True" to replace special characters in the table data (such as '<', '>', and '&') with their corresponding HTML entities for security reasons
                                                                  formatters=dict(
                                                                      thumbnail=path_to_image_html,                                                                     # "formatters" provide formatting option to the 'to_html' method pf pandas, allows user to customize how certai columns are displayed in teh HTML table output,,,,,The path_to_image_html function returns an HTML snippet with an image tag that displays the thumbnail image specified by the path parameter.
                                                                      comments=convert_comment_link,                                                                    # The convert_comment_link function takes a string with a video ID and comment count separated by a #SPLIT# delimiter and returns an HTML snippet with a link that opens the comments page for that video
                                                                      video_title=convert_title_link,                                                                   # convert_title_link function takes a string with video title and link separated by a #SPLIT# delimiter and returns an HTML snippet with a link that opens the video page
                                                                      download_link=create_download_urls                                                                # the create_download_urls function takes a video ID and returns an HTML snippet with a link that allows the user to download the video.
                                                                  ),
                                                                  render_links=True,                                                                                    # "render_links" argument is set to True, which tells the "to_html" method to render the formatted links as HTML.
                                                                  bold_rows=True,                                                                                       # "bold_rows" argument is set to True, which bolds the table's header row.
                                                                  justify='center',                                                                                     # "justify" argument is set to 'center', which centers the table data.
                                                                  index=False,                                                                                          # "index_names" argument is set to False, which suppresses the display of the DataFrame's index in the table.
                                                                  columns=['thumbnail',                                                                                 # "columns" argument is a list of column names to include in the table.
                                                                           'video_title',
                                                                           'publishedAt',
                                                                           'view_count',
                                                                           'like_count',
                                                                           'comments',
                                                                           'download_link'
                                                                           ]
                                                                  )
                                               ],
                                       titles=[''],                                                                                                                     # The "titles" argument is a list of titles to display above each table. In this case, the list contains only one empty string, so no title is displayed.
                                       channelTitle=channel_title                                                                                                       # The "channelTitle" argument is a string representing the title of the YouTube channel. This value is passed to the template and can be used to display the channel title on the page
                                       )


def convert_comment_link(var):
    video_id, comment_count = var.split('#SPLIT#')
    return f'''
                <a target = "_blank" href="/comments?video_id= {video_id}">{comment_count} </a>
            '''


@app.route("/comments", methods=["POST", "GET"])
def comments():
    video_id = request.args.get('video_id')
    video_data = session["video_data"]
    video_title = video_data[video_data["video_id"] == video_id]["title"].values[0]
    comment_data = get_comments.get_comments(video_id, video_title)
    return jsonify(comment_data)


def create_download_urls(video_id):
    return f'''
            <a target="_blank" href="/download?video_id={video_id}"> Download </a>
            '''


@app.route("/download", methods=["POST", "GET"])
def downloads():
    video_id = request.args.get('video_id')
    file = download_video.download_video(video_id)
    return file


def path_to_image_html(path):
    return f'''
                <a>
                        <img src = "{path}" alt = "thumbnail"
                        width = "200" height = "150" align = "left"/>
                </a>
            '''


def convert_title_link(var):
    title, videoLink = var.split('#SPLIT#')
    return f'''
            <a target="_blank" href="{videoLink}"> {title} </a>
            '''


@app.route('/')
def go_to_home():
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
