from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session
from data_collection import get_channel_ids, get_playlist_ids, get_video_details, get_comments, download_video
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
import os

app = Flask(__name__)                                                               ##these lines of code configure the Flask app to use a file-based session storage mechanism, sets a secret key for the app, and defines other important settings that affect the behavior of the application.
app.config["SESSION_PERMANENT"] = False                                             # generally a good practive to set this to 'False' and let the session die as the user closes the web application to prevent session hijacking and protect sensitie data that may have been stored in the session, however sometimes it is important to use session_permanent when the web application requires users to remain login across browsers sessions. In such cases, it is important to use a secure and unique secret key to encrypt the session data, and to set a reasonable expiration time for the session. A good practice is to set the PERMANENT_SESSION_LIFETIME to a value that balances the need for user convenience with the need for security. A duration of a few hours to a day is generally considered to be reasonable.
app.config["SESSION_TYPE"] = "filesystem"                                           # to store session data on the file system. Choice of session storage mechanism depends on the specific requirements of your application. For small-scale applications or during development, the file-based storage mechanism provided by Flask-Session can be useful. However, for large-scale applications or in production environments, it is recommended to use a more scalable and secure storage mechanism such as Redis or Memcached.
Session(app)                                                                        # While it's possible to manage user sessions without using Flask-Session, using it can help simplify your code, improve the security of your application, and make it easier to scale your application as it grows. Additionally, using a widely adopted and well-maintained solution like Flask-Session can help ensure that your session management solution is robust and reliable.
app.secret_key = os.getenv("app_secret_key")


@app.route("/home")
def home():
    return render_template("index.html", GitHubLink=os.getenv("GitHubLink"))


@app.route("/check", methods=["POST", "GET"])
def check():
    try:
        youtube_url = str(request.form['youtube_url'])
        session['username'] = youtube_url.split('/')[4]                             # using `session` module of Flask{{However, note that Flask-Session is a separate extension that can be used in addition to teh 'session' module to provide additional session storage options}}, it is extracting the username from the URL and storing it in session variable named `username`, the reason for storing this value in the session instead of a simple variable is that sessions provide a way to store data extracted in teh user's session that is associated with a specific user across multiple requests, by doing so this data will be available to teh server for duration of the user's session, which may span multiple requests. Otherwise if data stored in a simple variable , the value of the variable would be lost at the end of each request, and teh server would need to extract the usernamme again from the URL on subsequent requests.
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
    if session['channel_id'] == 'INVALID':                                          ##this condition i used if in case someone still click on submit without seeing that the "channe_id" has come "INVALID", then this condition will work
        return redirect(url_for("home"))
    else:
        session['playlist_id'] = get_playlist_ids.get_playlist_ids(session["channel_id"])
        if session['playlist_id'] == "INVALID":
            session["channel_id"] = "INVALID"                                       #setting all related session variables to an invalid value when any of them are found to be "INVALID" is a good practice to maintain code consistency and avoid unexpected behavior.
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
                ##1. using a web framework and rendering a template to display the dataframe can offer more flexibility and control over how the data is presented on the webpage. It can also make it easier to add additional features or functionality to the webpage, such as filtering or sorting the data, or providing interactive visualizations.
                # df = session["video_data"]         #assigning the dataframe that we got earlier to a variable "df"
                # return render_template('index_table.html', data = df)

                ##2. this way can be simpler in some cases because it is a straightforward way to convert the data into a format that can be easily serialized and sent to the webpage. This can be useful if the webpage needs to be updated frequently with new data
                # data_list = df.to_dict('records')
                # return render_template("index_table.html", data_list = data_list)

                ##3. the code creates a n html table with data from "video_data" session variable.
                return render_template("index_table.html",  # table is rendered using "render_template" function.
                                       tables=[video_data.to_html(escape=False,                                                                  # the "tables" argument of "render_template" function accepts a list of tables to render on the page. in this case only one table..,,,,#The table is created using the "to_html" method of the pandas DataFrame object. this method convert datafarme into html table.,,,,,,#setting "escape" to False means that any special characters in the table data will be included in the generated HTML code as-is, without being replaced with HTML entities. This can be useful for displaying code or including HTML code within the table data. However, it's important to ensure that the table data is properly sanitized to prevent potential security vulnerabilities. we set it to "True" to replace special characters in the table data (such as '<', '>', and '&') with their corresponding HTML entities for security reasons
                                                                             formatters=dict(
                                                                                            thumbnail=path_to_image_html,                                              # "formatters" provide formatting option to the 'to_html' method pf pandas, allows user to customize how certai columns are displayed in teh HTML table output,,,,,The path_to_image_html function returns an HTML snippet with an image tag that displays the thumbnail image specified by the path parameter.
                                                                                            comments=convert_comment_link,                                             # The convert_comment_link function takes a string with a video ID and comment count separated by a #SPLIT# delimiter and returns an HTML snippet with a link that opens the comments page for that video
                                                                                            video_title=convert_title_link,                                            # convert_title_link function takes a string with video title and link separated by a #SPLIT# delimiter and returns an HTML snippet with a link that opens the video page
                                                                                            download_link=create_download_urls                                         # the create_download_urls function takes a video ID and returns an HTML snippet with a link that allows the user to download the video.
                                                                                            ),
                                                                             render_links=True,                                                                         # "render_links" argument is set to True, which tells the "to_html" method to render the formatted links as HTML.
                                                                             bold_rows=True,                                                                            # "bold_rows" argument is set to True, which bolds the table's header row.
                                                                             justify='center',                                                                          # "justify" argument is set to 'center', which centers the table data.
                                                                             index=False,                                                                         # "index_names" argument is set to False, which suppresses the display of the DataFrame's index in the table.
                                                                             columns=['thumbnail',                                                                      # "columns" argument is a list of column names to include in the table.
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


def convert_comment_link(var):                                                                                                              ##"var" from teh particular column is a string separated y "#SPLIT#", first it si splitted and then assigned to two vrabales "video_id" and "comment_count", so that these two can be used to open up a "/comment" page. now `<a>` is a strt tag of anchor element to create hyperlink, in it the `target="_blank"` attribute specifies that the link should open in a new browser tab or window when clicked, `href="/comments?videoId={video_id}"` is the URL that the hyperlink points to. In this case, teh URL is `/comments` with a query parameter `videoId` set to `video_id`. so when thi scode exceuted , it generates amn HTML hyperlink that opens teh `/commnets` page with a `videoId` query parameter set to the value of `video_id` and displays teh `commne_count` value as teh hyperlink text
    video_id, comment_count = var.split('#SPLIT#')
    return f'''
                <a target = "_blank" href="/comments?video_id= {video_id}">{comment_count} </a>
            '''


@app.route("/comments", methods=["POST", "GET"])
def comments():
    video_id = request.args.get('video_id')
    video_data = session["video_data"]
    video_title = video_data[video_data["video_id"] == video_id]["title"].values[0]                                                           ##when using booleaan mask to index a pandas dataframe , the resulting object is a series object that contains the matching rows foe the consition . by using teh "values" attribute with an index of 0 , we can extract the first {and in this case only one is there } value in teh resulting series object , which is the title of the video,,,,alternatively can use teh "loc" accessor to directly access the value without creating a pandas series object, using `video_data.loc[video_data['videoId'] == videoId, 'title'].iloc[0]` accomplishes the same thing ,,,,,although "video_data[video_data["video_id"]==video_id]["title"][0]" will also give same result but using chained indexing sometimes creates a copy of the dataframe which can be slow and use up memory, therefore using ".values[0]" or ".iloc[0]" avoids the potential issue.
    comment_data = get_comments.get_comments(video_id, video_title)
    return jsonify(comment_data)


def create_download_urls(video_id):                                                                                                         ##thsi function returns an HTML hyperlink element that, when clicked, downloads a video with the given `video_id`. the returned string ia a multi-line f string that includes an HTML anchor(`<a>`) tag with a target attribute set to `_blanl` to open the link in a new window. the `href` attribute of the anchor tag i sset to `/download?videoId={video_id}`, which is a URL that the web application can use to initiate a download of the video with the given `video_id`. text inside teh anchor tag says "Download", which is displayed to user as hyperlink text
    return f'''
            <a target="_blank" href="/download?video_id={video_id}"> Download </a>
            '''


@app.route("/comments", methods=["POST", "GET"])
def downloads():
    video_id = request.args.get('video_id')
    file = download_video.download_video(video_id)
    return file


def path_to_image_html(path):                                                                                                           ##this function returns a multiline string that contains an HTML code. `<a>` creates a hyperlink tag, then `<img>` tag displays an image with a source `src` attribute set to the `path` parameter passed to the function, the `alt` attribute sets teh alernative text for the image if it is not displayed and rest other attributes `width`, `height`, and `align` specift the sie and alignmet of the image.
    return f'''
                <a>
                        <img src = "{path}" alt = "thumbnail"
                        width = "200" height = "150" align = "left"/>
                </a>
            '''


def convert_title_link(var):                                                                                                            ## this function converts a string of the format "title#SPLIT#videoLink" into an HTML anchor tag that links to the specified video.
    title, videoLink = var.split('#SPLIT#')
    return f'''
            <a target="_blank" href="{videoLink}"> {title} </a>
            '''


@app.route('/')                                                                                                                          ## When users access the root URL of the application (e.g. http://localhost:5000/), they will be automatically redirected to the home page defined in the home() function, which is more user-friendly than showing a blank page or an error message. Although not necessary as they simply redirect the user to the '/home' route. Th e'/home' route is alreday defined and will b ethe default route that the user i sredirected to when they first access the application. In general, it's a good practice to define a default or root route for web applications, so that users can access the application's main page without having to remember a specific URL.
def go_to_home():
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
