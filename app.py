from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import re
from datetime import datetime
from ultralytics import YOLO
from config import bucket, db
from Controllers import PredictModel, AuthModel
import os
import cv2
#from apscheduler.schedulers.background import BackgroundScheduler
#import requests

app = Flask(__name__)
app.secret_key = '1a2b3c4d5e6d7g8h9i10'
#app.app_context()

#def ping():
#    with app.app_context():
#        print("Keep alive")
#        requests.get('https://dog-breed-ai.onrender.com')
#        return jsonify({'message' : 'keep alive'})

#scheduler = BackgroundScheduler()
#scheduler.add_job(ping, 'interval', seconds=300)
#scheduler.start()

@app.route('/dogbreed/', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        params = (username, password)
        account = AuthModel.login(params)
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['email'] = account[2]
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html', title="Login")


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/dogbreed/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/dogbreed/register
# This will be the registration page, we need to use both GET and POST requests
@app.route('/dogbreed/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        params = (username, email, password)
        account = AuthModel.has_user(username)
        if account:
            flash("Account already exists!", "danger")
        else:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash("Invalid email address!", "danger")
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash("Username must contain only characters and numbers!", "danger")
            elif not username or not password or not email:
                flash("Incorrect username/password!", "danger")
            else:
                AuthModel.register(params=params)
                flash("You have successfully registered!", "success")
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html', title="Register")

# http://localhost:5000/pythinlogin/home
# This will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home/home.html', username=session['username'], title="Home")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/api/get-predictions', methods=['GET'])
def predictionHistory():
    if 'loggedin' in session:
        docs = PredictModel.get_data(session['id'])
        data = []
        for i, doc in enumerate(docs):
            d = doc.to_dict()
            item = (i, d['top_one'], d['image'], d['confidence'], d['created_at'] )
            data.append(item)
        return jsonify(
            {'data' :data }
        )
    else:
        return jsonify(
            {'message' : 'Unauthorized', 'status' : 401, 'data' : []}
        )

@app.route('/predictions')
def predictions():
    # Check if user is loggedin
    if 'loggedin' in session:
        template_data = {
            'title': 'Prediction History',
            'columns': ['#', 'Breed', 'Image', 'Prediction Result', 'Link']
        }
        return render_template('auth/predictions.html', username=session['username'], data=template_data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        account = (session['id'], session['username'], session['email'])
        return render_template('auth/profile.html', account=account)
    else:
        return redirect(url_for('login'))
def upload_to_storage(filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename, content_type='image/jpeg')
    blob.make_public()
    global image_predict
    image_predict = blob.public_url
    return image_predict

@app.route("/", methods=["GET", "POST"])
def predict_img():
    if request.method == "POST":
        if 'file' in request.files:
            file = request.files['file'] or request.files['captured_image']
            # basepath = os.path.dirname(__file__)
            # filepath = os.path.join(basepath, 'uploads', f.filename)
            # f.save(filepath)
            # global imgpath
            # predict_img.imgpath = f.filename
            timestamp = datetime.now()
            formatted = int(timestamp.timestamp())
            filename = f"temp/{formatted}_{file.filename}"
            file_extension = file.filename.rsplit('.', 1)[1].lower()

            destination_path = f'temp/{formatted}_{file.filename}'
            file.save(destination_path)
            filepath = destination_path
            
            if file_extension == 'jpg' or file_extension == "png":
                
                model = YOLO('classify.pt')
                results = model(filepath, verbose=False,conf=0.25, show_boxes=True, box=True, line_width=2, imgsz=640)
                result = results[0]

                orig_image = cv2.imread(filepath)
                font = cv2.FONT_HERSHEY_SIMPLEX
                img = cv2.resize(orig_image, (540, 640))
                # image = Image.open(filepath).convert('RGB').resize((480, 640))
                # draw = ImageDraw.Draw(image)
                
                probs = result.probs.top5[:3][::-1]
                conf = sorted(result.probs.top5conf.tolist())
                confidences = conf[::2]
                for i in range(len(probs)):
                    class_id = probs[i]
                    name = result.names[class_id]
                    confidence = format(confidences[i], '.2f')
                    y = i + 10
                    label_text = f"{name} {confidence}"
                    height, width, channels = img.shape
                    new_y = (height - y)
                    position = (20, new_y - 27 * i)
                    font_scale = 1
                    font_color = (64, 64, 239)
                    thickness = 2

                    cv2.putText(img, label_text, position, font, font_scale, font_color, thickness)

                    # Save the resulting image
                cv2.imwrite(filename, img)
                
                # for i in range(len(probs)):
                #     class_id = probs[i]
                #     name = result.names[class_id]
                #     confidence = format(confidences[i], '.2f')
                #     y = i + 1

                #     label_text = f"{name} {confidence}"
                #     image_width, image_height = image.size

                #     font = ImageFont.truetype("arial.ttf", 20)
                #     new_y = (image_height - y * 24) - 25
                #     draw.text((10, new_y), label_text ,fill="yellow", font=font, stroke_width=1, stroke_fill="red")
                
                # image.save(filename)
                file_url = upload_to_storage(filename=filename)
                
                prediction_name = result.names[result.probs.top1]
                prediction_conf = format(result.probs.top1conf.clone().item(), '.2f')
                params = (prediction_name, file_url, prediction_conf, session['id'])
                PredictModel.save(params)

            elif file_extension == 'mp4':
                return redirect('https://firebasestorage.googleapis.com/v0/b/arctic-math-338423.appspot.com/o/404_page.jpg?alt=media&token=aeba01ee-1a90-4715-8b04-ec7b792b279f')
                # cap = cv2.VideoCapture(filepath)

                # # get video dimensions
                # frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                # frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # # initialize the yolov8 model
                # model = YOLO('classify.pt')
                # results = model(cap, save=True, stream=True)  # working
                # cap = cv2.VideoCapture(filepath)

                # # Loop through the video frames
                # while cap.isOpened():
                #     # Read a frame from the video
                #     success, frame = cap.read()

                #     if success:
                #         # Run YOLOv8 inference on the frame
                #         results = model(frame)

                #         # Visualize the results on the frame
                #         annotated_frame = results[0].plot()

                #         # Display the annotated frame
                #         cv2.imshow("YOLOv8 Inference", annotated_frame)

                #         # Break the loop if 'q' is pressed
                #         if cv2.waitKey(1) & 0xFF == ord("q"):
                #             break
                #     else:
                #         # Break the loop if the end of the video is reached
                #         break

                # # Release the video capture object and close the display window
                # cap.release()
                # cv2.destroyAllWindows()
    # blob = bucket.blob(filename)
    # blob.make_public()
    # prediction = blob.public_url
    return redirect(image_predict)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
