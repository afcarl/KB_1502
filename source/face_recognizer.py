# -*- coding: UTF-8 -*-

import matplotlib
matplotlib.use('TkAgg')
import cv2
import math
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

from speech_recognizer import SpeechRecognizer

from Face import GeoInfo,Face

from graph_drawer import GraphDrawer

from word_analyze import WordAnalyze

from omoroi_data import OmoroiData

from fig2img import fig2data,fig2img

import matplotlib.pyplot as plt
import numpy

face_feature_path = "../training_dataset/haarcascade_frontalface_alt.xml"
smile_feature_path = "../training_dataset/smiled_04.xml"


def _rect_parallel_translation(lrect,translation):
    lrect[0:2] = [lrect[0]+translation[0],lrect[1]+translation[1]]

class FaceRecognizer(object):

    def __init__(self,capture):
        self.faces = []
        self.smile_matrix = [[]] * 50
        # カメラからキャプチャー
        self.cap = capture

    def get_features(self, image, feature_path,min_neighbors=1,min_size=(100, 100)):
        """
        与えた特徴量, 教師によって学習したcascade adaboostで領域分割.
        input
            image: cv2.imreadで読み取った変数
            feature_path: trainingデータ
            min_size: 顔判定する最小サイズ指定
        output
            faces: 顔の座標情報
        """
        image = np.array(image)
        cascade = cv2.CascadeClassifier(feature_path)

        #グレースケール
        frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #顔判定
        """
        minSizeで顔判定する際の最小の四角の大きさを指定できる.
        (小さい値を指定し過ぎると顔っぽい小さなシミも顔判定されるので)
        """
        faces = cascade.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=min_neighbors, minSize=min_size)

        return faces

    def update(self, speech, min_size=(300, 300)):
        """
        顔を四角で囲うメソッド.
        input
            image: cv2.imreadで読み取った変数
            speech: 音声認識によって推定されたstringのテキスト
            min_size: 顔判定する最小サイズ指定
        output:
            enclosed_facs: 囲まれた顔画像
        """

        ret, image = self.cap.read()

        # 出力結果を格納する変数
        enclosed_faces = image

        # 顔認識
        face_rects = self.get_features(image, face_feature_path, min_neighbors=1, min_size=min_size)


        # 顔認識の枠の色
        color_face = (255, 0, 0)
        # 笑顔認識の枠の色
        color_smile = (0, 255, 0)

        # 新しい顔
        new_faces = []
        for face_rect in face_rects:
            new_faces.append(Face(geoinfo=GeoInfo(face_rect)))

        # 現在トラッキングしている顔を更新
        self.update_faces(self.faces, new_faces)

        for i, face in enumerate(self.faces):
            image_ = Image.fromarray(np.uint8(image))

            # 笑顔認識 顔の下半分だけ笑顔(笑顔唇)判定
            face_image = image_.crop((face.geoinfo.coordinates[0][0],
                                      face.geoinfo.coordinates[0][1]+face.geoinfo.length[1]/2,
                                      face.geoinfo.coordinates[1][0],
                                      face.geoinfo.coordinates[1][1],))
            smile_rects = self.get_features(face_image, smile_feature_path, min_neighbors=1,min_size=(int(face.geoinfo.length[0]*0.2), int(face.geoinfo.length[1]*0.2)))

            #[For debug]認識している笑顔の唇の枠表示
            for smile_rect in smile_rects:
                _rect_parallel_translation(smile_rect,face.geoinfo.coordinates[0])
                _rect_parallel_translation(smile_rect,(0,face.geoinfo.length[1]/2))
                smile_geoinfo = GeoInfo(smile_rect)
                cv2.rectangle(enclosed_faces,
                              smile_geoinfo.coordinates[0],
                              smile_geoinfo.coordinates[1],
                              (0,0,255), thickness=3)

            #ひとつでも笑顔唇を認識している場合「笑っている」と判定
            if len(smile_rects) > 0:
                face.is_smiling = True
                frame_color = color_smile
            else:
                face.is_smiling = False
                frame_color = color_face

            # 写っている人間ごとの盛り上がり度

            # 笑わせた
            #omorosa.count_smile(face.is_smiling)
            #if speech != "":
            #    omorosa.count_loudness(True)
            #else:
            #    omorosa.count_loudness(False)

        # 顔認識の枠の色
        color_face = (255, 0, 0)
        # 笑顔認識の枠の色
        color_smile = (0, 255, 0)

        # 新しい顔
        new_faces = []
        for face_rect in face_rects:
            new_faces.append(Face(geoinfo=GeoInfo(face_rect)))

        # print "num of past faces = " + str(len(faces))
        # print "num of current faces = " + str(len(new_faces))


        # 現在トラッキングしている顔を更新
        self.update_faces(self.faces, new_faces)

        for i, face in enumerate(self.faces):
            image_ = Image.fromarray(np.uint8(image))

            # 笑顔認識 顔の下半分だけ笑顔(笑顔唇)判定
            face_image = image_.crop((face.geoinfo.coordinates[0][0],
                                      face.geoinfo.coordinates[0][1]+face.geoinfo.length[1]/2,
                                      face.geoinfo.coordinates[1][0],
                                      face.geoinfo.coordinates[1][1],))
            smile_rects = self.get_features(face_image, smile_feature_path, min_neighbors=1,min_size=(int(face.geoinfo.length[0]*0.2), int(face.geoinfo.length[1]*0.2)))

            #[For debug]認識している笑顔の唇の枠表示
            for smile_rect in smile_rects:
                _rect_parallel_translation(smile_rect,face.geoinfo.coordinates[0])
                _rect_parallel_translation(smile_rect,(0,face.geoinfo.length[1]/2))
                smile_geoinfo = GeoInfo(smile_rect)
                cv2.rectangle(enclosed_faces,
                              smile_geoinfo.coordinates[0],
                              smile_geoinfo.coordinates[1],
                              (0,0,255), thickness=3)

            #ひとつでも笑顔唇を認識している場合「笑っている」と判定
            if len(smile_rects) > 0:
                face.is_smiling = True
                frame_color = color_smile
            else:
                face.is_smiling = False
                frame_color = color_face

            # 写っている人間ごとの盛り上がり度

            # 笑わせた
            #omorosa.count_smile(face.is_smiling)
            #if speech != "":
            #    omorosa.count_loudness(True)
            #else:
            #    omorosa.count_loudness(False)

            cv2.rectangle(enclosed_faces,
                          face.geoinfo.coordinates[0],
                          face.geoinfo.coordinates[1],
                          frame_color, thickness=3)
            enclosed_faces = self.write_speech(enclosed_faces,
                                               face.geoinfo.coordinates[0],
                                               face.geoinfo.coordinates[1],
                                               speech, str(i))

            enclosed_faces = face.update(enclosed_faces,color_num=i)

        return enclosed_faces

    def update_faces(self, faces, new_faces):
        """
        顔を更新
        input
            faces:現在tracking中の顔
        output
            new_faces:新たにdetectした顔
        """
        #今現在トラッキングしている顔座標と新たに取得した顔座標同士の距離を計算
        distances_matrix = []
        for face in faces:
            distances = []
            for new_face in new_faces:
                euc_distance = (face.geoinfo.center[0] - new_face.geoinfo.center[0])**2 \
                               + (face.geoinfo.center[1] - new_face.geoinfo.center[1])**2
                distances.append(euc_distance)
            distances_matrix.append(distances)

        face_indexes = [ i for i in xrange(len(faces))]
        new_face_indexes = [ i for i in xrange(len(new_faces))]

        # O( (顔の数)^3 )の計算量。 O(　(顔の数)^2 log(顔の数) )の計算量にできるが。
        while(len(face_indexes)>0):
            if (len(new_face_indexes) == 0):
                face_indexes.reverse()
                for i in face_indexes:
                    del faces[i]
                break
            min_distance = np.inf
            for i in xrange(len(face_indexes)):
                for j in xrange(len(new_face_indexes)):
                    if ( distances_matrix[face_indexes[i]][new_face_indexes[j]] < min_distance):
                        min_distance = distances_matrix[face_indexes[i]][new_face_indexes[j]]
                        min_i = i
                        min_j = j
            faces[face_indexes[min_i]].geoinfo = new_faces[new_face_indexes[min_j]].geoinfo

            del face_indexes[min_i]
            del new_face_indexes[min_j]

        for j in new_face_indexes:
            faces.append(new_faces[j])

    def write_speech(self, image, coordinates, length, speech, label):
        """
        顔枠の下に文字を書き込むメソッド.
        input
            image: 元画像(フレーム)
            coordinates: 顔枠の左上の座標
            length: 縦横の長さ
            speech: 発話内容
            label: 人物分類の結果
        output:
            image: 顔フレームの下に発話を書き込んだもの
        """

        # # イメージをpillowで扱うことのできる形式に変換
        # img_edit = Image.fromarray(image)

        # font = cv2.FONT_HERSHEY_PLAIN
        # font_size = 3.5
        # text = "wei"
        # #文字の書き込み
        # cv2.putText(image, text, (coordinates[0], length[1] + 40), font, font_size,(255,255,0))

        img_edit = Image.fromarray(image)
        font = ImageFont.truetype('../fonts/ヒラギノ角ゴシック W0.ttc',
                                  40, encoding='unic')

        # ポジネガ判定(todo)
        #words = word_analyze.morphological_analysis(speech)

        draw = ImageDraw.Draw(img_edit)
        draw.text((coordinates[0], length[1]), label, font = font, fill='#FFFFFF')
        draw.text((coordinates[0], length[1]), speech, font = font, fill='#FFFFFF')
        image = np.asarray(img_edit)

        return image

    def get_mean_of_smiles(self):
        ret = 0
        for face in self.faces:
            ret += int(face.is_smiling)
        return ret/(len(self.faces)+1e-6)

if __name__ == '__main__':

    omorosa = OmoroiData()

    word_analyze = WordAnalyze()

    capture = cv2.VideoCapture(0)
    face_recognizer = FaceRecognizer(capture=capture)

    speech_recognizer = SpeechRecognizer()
    speech_recognizer.start()

    graph_drawer = GraphDrawer(ylabel="Omorosa")

    while(True):

        # 動画ストリームからフレームを取得

        speech = speech_recognizer.get_speech()

        # frameで切り取り画像を受け取る
        frame_face = face_recognizer.update(speech)
        omorosa.update_omoroi_sequence(face_recognizer.get_mean_of_smiles(),int( not (speech == "")))
        # 画像・音声の部分時系列を取得
        length = 20

        omoroi_subsequence = omorosa.get_subsequence(omorosa.omoroi_sequence,length)

        graph_drawer.update_plot1d(np.arange(len(omoroi_subsequence)),omoroi_subsequence,ylim=[omorosa.omoroi_min-1.0,omorosa.omoroi_max+1.0],color_num=-1)
        frame_face = graph_drawer.paste_graph_image(image_data=frame_face,pos=(0,0))

        # 表示
        cv2.imshow('FACE', frame_face)

        # qを押したら終了
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

    print omorosa.smile_sequence
    print omorosa.loudness_sequence

    capture.release()
    cv2.destroyAllWindows()

    speech_recognizer.stop()