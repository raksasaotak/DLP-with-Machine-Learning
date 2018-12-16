from keras.models import Sequential
from keras.layers import Dense, Activation
from keras_preprocessing import text
from keras.models import model_from_json
import numpy as np
import pandas as pd
from sklearn import preprocessing
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from tika import parser
import keras
import pickle

##TODO Dokumentasi Codingan, buat variabel rapi

def extract_text(file_path):
    ##Buat ngambil text dari document, inputnya dari file path
    text = parser.from_file(file_path)
    return text['content']

def preprocess_text(text):
    ##Buat mecah kalimat dr text, sekaligus menghilangkan karakter-karakter yg ada di filter
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
    ##Ngebuat dataset dari csv
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
    df.to_csv('test.csv', encoding="utf-8")

def list_dupe_del(seq):
    ##Biar list gaada yang sama, karena kadang file yang sama bisa di modify dan lain2. Fungsinya ini jd biar sekali aja di ceknya
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

##TODO cek bug perbandingan h5 ke inputan
def checker(csv_file='example_test.csv', json_model='model.json', h5_model='model.h5', tokenizer='tokenizer.pickle'):
    predicted_data = {'filename': [], 'tags': []}
    old_data = {'filename': [], 'tags': []}

    try:
        dlp_file = pd.read_csv('dlp.csv', encoding='utf-8')
        old_data['filename'].extend(dlp_file['filename'])
        old_data['tags'].extend(dlp_file['tags'])
    except:
        pass

    data = pd.read_csv(csv_file)
    dictionary = pd.read_csv('example_test.csv', encoding='utf-8')
    json_file = open(json_model, 'r')
    loaded_json_model = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_json_model)
    loaded_model.load_weights(h5_model)

    post = data['documents']
    train_tags = dictionary['tags']
    # loading
    with open(tokenizer, 'rb') as handle:
        tokenizer = pickle.load(handle)

    x_post = tokenizer.texts_to_matrix(post)
    encoder = preprocessing.LabelBinarizer()
    encoder.fit(train_tags)
    text_labels = encoder.classes_
    pred = loaded_model.predict(np.array(x_post))
    for i in range(0, len(post)):
        print("Document %s is %s sentiment; %f%% confidence" % (data['filename'][i], text_labels[np.argmax(pred[i])], pred[i][np.argmax(pred[i])] * 100))
        predicted_data['filename'].append(data['filename'][i].encode("utf-8", "surrogateescape").decode())
        predicted_data['tags'].append(text_labels[np.argmax(pred[i])].encode("utf-8", "surrogateescape").decode())

    df = pd.DataFrame(predicted_data, columns=['filename', 'tags'])
    old_df = pd.DataFrame(old_data, columns=['filename', 'tags'])
    for i in range(0, len(predicted_data['filename'])):
        old_df.loc[old_df.filename == predicted_data['filename'][i], 'tags'] = predicted_data['tags'][i]
    old_df = old_df.append(df)
    old_df = old_df.drop_duplicates()
    old_df = old_df.reset_index(drop=True)
    old_df.to_csv('dlp.csv', encoding="utf-8")

##TODO buat trainer nya dulu kalo belom ada h5
def trainer(dict_csv='example_test.csv'):
    data = pd.read_csv(dict_csv)
    train_size = int(len(data) * .7)
    train_posts = data['documents'][:train_size]
    train_tags = data['tags'][:train_size]
    test_posts = data['documents'][train_size:]
    test_tags = data['tags'][train_size:]
    posts = data['documents']
    dlp_data = {'filename': [], 'tags': []}
    vocab_size = 10000
    tokenize = text.Tokenizer(num_words=vocab_size)
    tokenize.fit_on_texts(train_posts)
    #save token
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenize, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("Saving tokenizer with name tokenizer.pickle")

    x_train = tokenize.texts_to_matrix(train_posts)
    x_test = tokenize.texts_to_matrix(test_posts)
    x_post = tokenize.texts_to_matrix(posts)

    encoder = preprocessing.LabelBinarizer()
    encoder.fit(train_tags)
    y_train = encoder.transform(train_tags)
    y_test = encoder.transform(test_tags)
    text_labels = encoder.classes_

    num_labels = len(np.unique(y_train))
    batch_size = 1024
    model = Sequential()

    ##Buat hidden layer, gunanya buat naikin akurasi
    model.add(Dense(256, input_shape=(vocab_size,)))
    model.add(Activation('relu'))
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dense(256))
    model.add(Activation('relu'))

    model.add(Dense(num_labels))
    model.add(Activation('softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    history = model.fit(x_train, y_train,
                        batch_size=batch_size,
                        epochs=256,
                        verbose=1,
                        validation_split=0.1)

    score = model.evaluate(x_test, y_test,batch_size=batch_size, verbose=1)
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
        print("\n Saved h5 json model to disk with name model.json ")

    model.save_weights("model.h5")
    print("\n Saved model to disk with name model.h5")
    print("Training done")

    pred = model.predict(np.array(x_post))
    for i in range(0, len(posts)):
        print('Document name: %s, is %s' % (data['filename'][i], text_labels[np.argmax(pred[i])]))
        dlp_data['filename'].append(data['filename'][i])
        dlp_data['tags'].append(text_labels[np.argmax(pred[i])])

    df = pd.DataFrame(dlp_data, columns=['filename', 'tags'])
    df.to_csv('dlp.csv', encoding="utf-8")

    print('Saved CSV model')
    # loaded_model = model_from_json(loaded_model_json)

    # loaded_model.load_weights("model.h5")
    # print("Loaded model from disk")
    #
    # loaded_model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    # score = loaded_model.evaluate(x_test, y_test, verbose=1)
    # print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))

##TODO ACL

class Watcher:
    ##TODO directorynya dari inputan user
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

    ##Untuk sekarang cuma kalo file di buat, di modify, atau di move baru watchernya logging. Gunanya watcher untuk kalo ada file baru atau yg di edit bakal di extract textnya buat di cek confidential atau enggak
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

        # elif event.event_type == 'deleted':
        #     # Taken any action here when a file is deleted.
        #     print ("Received deleted event - %s." % event.src_path)
        #     new_file.append(event.src_path.split('/')[-1:])
        #     changelog = open('clog.txt', 'a')
        #     changelog.write('deleted, ' + ''.join(event.src_path.split('/')[-1:]) + '\n')
        #     changelog.close()

def dir_watch(dir_to_watch='fix/'):
    w = Watcher()
    w.watch_dir(dir_to_watch)
    w.run()

if __name__ == '__main__':

    changes = []
    ##TODO cek dari config.ini, atau settings.ini
    ##TODO cek ada h5 ga
    h5_file = ''#Kalo ada file h5 masukin kesini
    h5json_file = ''#Kalo ada file h5 json masukin kesini
    tokenizer_file = ''#Kalo ada file tokenizer dalam bentuk .pickle masukin kesini
    files = os.listdir('fix/') #TODO list dir dari inputan user
    list = [file for file in files if ".pdf" in file] #Buat daftar file apa aja yang ada di dalam sebuah directory yang filetypenya pdf
    if h5_file == '' or h5json_file == '':
        print("No H5 model found, training our ML system according to your file")
        make_dataset(list)
        trainer()
        h5_file='model.h5'
        h5json_file='model.json'
        tokenizer_file='tokenizer.pickle'

    try:
        while True:
            list = []
            #TODO kalo dapet file baru dari watcher, dilempar kesini. Sekarang diakalin pake time sleep, timesleep watcher = 1, timesleep dlp 5
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
            print('list making complete, going into checking session')
            checker()
            time.sleep(5)

    except ValueError as e:
        print(e)
