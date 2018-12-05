from keras.models import Sequential
from keras.layers import Dense, Activation
from keras_preprocessing import text
from keras.models import model_from_json
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.externals import joblib
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from taki import parser
import keras

def extract_text(file_path):
    text = parser.from_file(file_path)
    return text['content']

def preprocess_text(text):
    texts = []
    text = keras.preprocessing.text.text_to_word_sequence(text, filters='`!"#$%&()*+,-./:;<=>?@[\]^_{|}~€£“', lower=True, split=' ')

    for line in text:
        line = line.strip()
        if "\n" not in line:
            texts.append(line)
        else:
            line = line.replace("\n", " ")
            line = line.split(" ")
            texts.extend(line)

    texts[:] = [item for item in texts if item != '']
    return texts

def make_dataset(list_of_file):
    raw_data = {'documents': [], 'file_name': []}
    for file in list_of_file:
        try:
            a = extract_text('fix/'+file) ##TODO ambil fullpath dari user input
            a = preprocess_text(a)
            b = ''
            for word in a:
                b += word + ' '
            raw_data['documents'].append(b)
            raw_data['file_name'].append(file)
        except ValueError as e:
            print(e)
    df = pd.DataFrame(raw_data, columns=['documents', 'file_name'])
    df.to_csv('test.csv')

##Biar list gaada yang sama
def list_dupe_del(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

##TODO cek bug perbandingan h5 ke inputan
##TODO buat threshold?
def checker(csv_file='test.csv', json_model='model.json', h5_model='model.h5'):
    data = pd.read_csv(csv_file)
    dictionary = pd.read_csv('example_test.csv')
    json_file = open(json_model, 'r')
    loaded_json_model = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_json_model)
    loaded_model.load_weights(h5_model)
    loaded_model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    post = data['documents']
    train_post = dictionary['documents']
    train_tags = dictionary['tags']
    tokenizer = text.Tokenizer(num_words=1000)
    tokenizer.fit_on_texts(train_post)
    x_post = tokenizer.texts_to_matrix(post)
    encoder = preprocessing.LabelBinarizer()
    encoder.fit(train_tags)
    text_labels = encoder.classes_
    pred = loaded_model.predict(x_post)
    for i in range(0, len(post)):
        print("Document %s is %s sentiment; %f%% confidence" % (data['file_name'][i], text_labels[i], pred[i][np.argmax(pred[i], axis=None)] * 100))

##TODO buat trainer nya dulu kalo belom ada h5

##TODO Document tagging

##TODO ACL

class Watcher:

    DIRECTORY_TO_WATCH = ''

    def __init__(self):
        self.observer = Observer()

    def watch_dir(self, what_dir):
        self.DIRECTORY_TO_WATCH = what_dir

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print ("Error")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        new_file = []
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print ("Received created event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt','a')
            changelog.write('created, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print ("Received modified event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt', 'a')
            changelog.write('modified, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        elif event.event_type == 'moved':
            # Taken any action here when a file is moved.
            print ("Received moved event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt', 'a')
            changelog.write('moved, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

        elif event.event_type == 'deleted':
            # Taken any action here when a file is deleted.
            print ("Received deleted event - %s." % event.src_path)
            new_file.append(event.src_path.split('/')[-1:])
            changelog = open('clog.txt', 'a')
            changelog.write('deleted, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
            changelog.close()

if __name__ == '__main__':
    # w = Watcher()
    # w.watch_dir('fix/')
    # w.run()
    changes = []
    # files = os.listdir('fix/') #TODO list dir dari inputan user
    # list = [file for file in files if ".pdf" in file]
    # # make_dataset(list)
    #
    try:
        while True:
            list = []
            #TODO kalo dapet file baru dari watcher, dilempar kesini. Sekarang diakalin pake time sleep, timesleep watcher = 1, timesleep dlp 5
            time.sleep(5)
            clog = open('clog.txt','r')
            for line in clog:
                line = line.split(', ')
                line = ''.join(line[-1:])
                line = line.replace('\n','')
                changes.append(line)
            changes = list_dupe_del(changes)
            clog.close()
            #biar clog.txt-nya bersih
            # clog = open('clog.txt','w')
            # clog.close()

            list.extend(file for file in changes if ".pdf" in file)
            make_dataset(list)
            print(list)
            print('list making complete, going into checking session')
            checker()

    except ValueError as e:
        print(e)
