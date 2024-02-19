import numpy as np
import cv2
import os
import pickle
import face_recognition
import cvzone
import firebase_admin
from datetime import datetime
from gtts import gTTS
import pyttsx3
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "",
})


def check_if_already_seen(repeat_counter, user_info, engine):
    speech_var = f"You are still looking at your, {user_info['name']}"
    engine.say(speech_var)
    engine.runAndWait()
    repeat_counter = 0

def load_user_image(user_id, bucket):
    user_image = None
    image_extensions = ['png', 'jpg', 'jpeg']
    for ext in image_extensions:
        blob = bucket.get_blob(f'Images/{user_id}.{ext}')
        if blob:
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            user_image = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            break
    return user_image

def main():
    speech_var = ""
    repeat_counter = 0
    engine = pyttsx3.init()

    bucket = storage.Client().bucket()

    cap = cv2.VideoCapture(0)
    cap.set(3, 360)
    cap.set(4, 490)

    img_background = cv2.imread('Resources/background.png')

    folder_mode_path = 'Resources/Modes'
    mode_path_list = os.listdir(folder_mode_path)
    img_mode_list = [cv2.imread(os.path.join(folder_mode_path, path)) for path in mode_path_list]

    print("Loading Encode File")
    speech_var = "Loading Encode File"
    engine.say(speech_var)
    engine.runAndWait()

    encoded_list_with_ids = pickle.load(open('EncodedFile.p', 'rb'))
    encoded_list_known, user_ids = encoded_list_with_ids

    user_images = {user_id: load_user_image(user_id, bucket) for user_id in user_ids}

    mode_type = 0
    counter = 0
    current_user_id = -1
    img_user = None

    while True:
        success, img = cap.read()
        img_rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        img_resized = cv2.resize(img_rotated, (340, 400))

        face_cur_frame = face_recognition.face_locations(img_resized)
        encode_cur_frame = face_recognition.face_encodings(img_resized, face_cur_frame)

        img_background[162:162 + 480, 55:55 + 340] = img_resized
        img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

        if face_cur_frame:
            img_user = None
            for encode_face, face_loc in zip(encode_cur_frame, face_cur_frame):
                matches = face_recognition.compare_faces(encoded_list_known, encode_face)
                face_dis = face_recognition.face_distance(encoded_list_known, encode_face)

                match_index = np.argmin(face_dis)

                if matches[match_index]:
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    img_background = cvzone.cornerRect(img_background, bbox, rt=0)

                    current_user_id = user_ids[match_index]
                    if counter == 0:
                        cvzone.putTextRect(img_background, "Loading", (274, 370))
                        cv2.imshow("SAIGHT face detection", img_background)
                        cv2.waitKey(1)
                        counter = 1
                        mode_type = 1

                    if img_user is None:
                        img_user = load_user_image(current_user_id, bucket)

            if counter != 0:
                if counter == 1:
                    user_info = db.reference(f'Users/{current_user_id}').get()

                    if user_info is None:
                        print(f"User information not found for id: {current_user_id}")
                        continue  # Skip the rest of the loop iteration

                    last_seen = user_info.get('last_seen')
                    if last_seen:
                        datetime_object = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
                        seconds_elapsed = (datetime.now() - datetime_object).total_seconds()
                        print(seconds_elapsed)
                        if seconds_elapsed > 30:
                            ref = db.reference(f'Users/{current_user_id}')
                            user_info['times_seen'] += 1

                            ref.child('times_seen').set(user_info['times_seen'])
                            ref.child('last_seen').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                            speech_var = f"You are approaching your {user_info['relation']}, {user_info['name']}"
                            engine.say(speech_var)
                            engine.runAndWait()
                        else:
                            cvzone.putTextRect(img_background, "Already Seen. Skipping.", (75, 600), 1, 1, (255, 255, 255), (0, 0, 0))

                            # repeat_counter += 1
                            # if repeat_counter <= 500:
                            #     check_if_already_seen()

                            counter = 0
                            img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]
                    else:
                        print(f"Last seen timestamp not found for user id: {current_user_id}")
                        mode_type = 3
                        counter = 0
                        img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

                if mode_type != 3:
                    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

                    if counter <= 10:
                        cv2.putText(img_background, str(user_info['name']), (870, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(img_background, "User email: "+str(user_info['email']), (880, 450),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(img_background, "User ID: "+str(current_user_id), (880, 500),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(img_background, "Birth Date: "+str(user_info['birth_date']), (880, 530),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(img_background, "Phone: "+str(user_info['phone_number']), (880, 560),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(img_background, "Times Seen: "+str(user_info['times_seen']), (880, 590),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        if img_user is not None:
                            img_user = cv2.resize(img_user, (216, 216))
                            img_background[175:175 + 216, 909:909 + 216] = img_user

                    counter += 1

                    if counter >= 40:
                        counter = 0
                        mode_type = 0
                        user_info = None
                        img_user = None
                        img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]
        else:
            mode_type = 0
            counter = 0

        cv2.imshow("Face detection saight", img_background)
        cv2.waitKey(1)

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()