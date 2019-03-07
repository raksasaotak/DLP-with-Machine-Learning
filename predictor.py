from keras.models import Sequential
from keras.layers import *
from keras_preprocessing import text
from keras.models import model_from_json
import numpy as np
import pandas as pd
from sklearn import preprocessing
import time
import os
from tika import parser
import keras
import pickle
import configparser
import csv
import sys
import win32security
import ntsecuritycon as con

ps = configparser.ConfigParser()
ps.read('testong.ini')

maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt / 10)
        decrement = True


##TODO Dokumentasi Codingan, buat variabel rapi

class dlp():
    def is_first_run():
        h5_file = ''
        h5json_file = ''
        tokenizer_file = ''
        try:
            h5_file = ps.get('machine_learning', 'h5')  # Kalo ada file h5 masukin kesini
            h5json_file = ps.get('machine_learning', 'weight')  # Kalo ada file h5 json masukin kesini
            tokenizer_file = ps.get('pickle_file',
                                    'pickle')  # Kalo ada file tokenizer dalam bentuk .pickle masukin kesini
        except:
            pass
        if h5_file == '' or h5json_file == '' or tokenizer_file == '':
            return True
        elif h5_file != '' and h5json_file != '' and tokenizer_file != '':
            return False

    def extract_text(file_path):
        ##Buat ngambil text dari document, inputnya dari file path
        text = parser.from_file(file_path)
        return text['content']

    def preprocess_text(text):
        ##Buat mecah kalimat dr text, sekaligus menghilangkan karakter-karakter yg ada di filter
        texts = []
        text = keras.preprocessing.text.text_to_word_sequence(text, filters='`!"#$%&()*+,-./:;<=>?@[\]^_{|}~€£“',
                                                              lower=True, split=' ')

        for line in text:
            line = line.strip()
            if "\n" not in line:
                texts.append(line)
            else:
                line = line.replace("\n", " ")
                line = line.split(" ")
                texts.extend(line)

        texts[:] = [item for item in texts if item is not '' and item is not ' ' and item is not None]
        return texts

    def make_dataset(list_of_file):
        ##Ngebuat dataset dari csv
        raw_data = {'documents': [], 'filename': [], 'tags': []}
        i = 0
        if "tags" in list_of_file:
            for file in list_of_file['filename']:
                if os.path.isfile(ps.get('folder_protect', 'folder') + '/' + list_of_file['tags'][i] + '/' + file):
                    try:
                        a = dlp.extract_text(
                            ps.get('folder_protect', 'folder') + '/' + list_of_file['tags'][i] + '/' + file)
                        a = dlp.preprocess_text(a)
                        b = ''
                        for word in a:
                            b += word + ' '
                        raw_data['documents'].append(b)
                        raw_data['filename'].append(file)
                        raw_data['tags'].append(list_of_file['tags'][i])
                        i += 1
                    except ValueError as e:
                        print(e)
                else:
                    try:
                        a = dlp.extract_text(ps.get('folder_protect', 'folder') + '/' + file)
                        a = dlp.preprocess_text(a)
                        b = ''
                        for word in a:
                            b += word + ' '
                        raw_data['documents'].append(b)
                        raw_data['filename'].append(file)
                        raw_data['tags'].append(list_of_file['tags'][i])
                        i += 1
                    except ValueError as e:
                        print(e)
            df = pd.DataFrame(raw_data, columns=['documents', 'tags', 'filename'])
        else:
            for file in list_of_file:
                try:
                    a = dlp.extract_text(ps.get('folder_protect', 'folder') + '/' + file)
                    a = dlp.preprocess_text(a)
                    b = ''
                    for word in a:
                        b += word + ' '
                    raw_data['documents'].append(b)
                    raw_data['filename'].append(file)
                except ValueError as e:
                    print(e)
            df = pd.DataFrame(raw_data, columns=['documents', 'filename'])

        df.to_csv('test.csv', encoding="utf-8")

    def list_dupe_del(seq):
        ##Biar list gaada yang sama, karena kadang file yang sama bisa di modify dan lain2. Fungsinya ini jd biar sekali aja di ceknya
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    ##TODO cek bug perbandingan h5 ke inputan
    def checker(csv_file='test.csv', json_model='model.json', h5_model='model.h5', tokenizer='tokenizer.pickle'):
        predicted_data = {'filename': [], 'tags': []}
        old_data = {'filename': [], 'tags': []}

        try:
            dlp_file = pd.read_csv('dlp.csv', encoding='utf-8', engine='python')
            old_data['filename'].extend(dlp_file['filename'])
            old_data['tags'].extend(dlp_file['tags'])
        except:
            pass

        data = pd.read_csv(csv_file, engine='python')
        dictionary = pd.read_csv('dlp.csv', encoding='utf-8', engine='python')
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
            print("Document %s is %s sentiment; %f%% confidence" % (
                data['filename'][i], text_labels[np.argmax(pred[i])], pred[i][np.argmax(pred[i])] * 100))
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
        df.to_csv('acl.csv', encoding='utf-8')

    ##TODO buat trainer nya dulu kalo belom ada h5
    def trainer(dict_csv='test.csv'):
        data = pd.read_csv(dict_csv, engine='python')
        train_size = int(len(data) * .7)
        train_posts = data['documents']
        train_tags = data['tags']
        test_posts = data['documents'][train_size:]
        test_tags = data['tags'][train_size:]
        posts = data['documents']
        dlp_data = {'filename': [], 'tags': []}
        vocab_size = 10000
        tokenize = text.Tokenizer(num_words=vocab_size)
        tokenize.fit_on_texts(train_posts)
        # save token
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
        model.add(Dense(512, input_shape=(vocab_size,)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Dense(128))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Dense(512))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Dense(128))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(Dense(64))
        model.add(BatchNormalization())
        model.add(Activation('relu'))

        model.add(Dense(num_labels))
        model.add(BatchNormalization())
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        history = model.fit(x_train, y_train,
                            batch_size=batch_size,
                            epochs=256,
                            verbose=1,
                            validation_split=0.1)

        score = model.evaluate(x_test, y_test, batch_size=batch_size, verbose=1)
        model_json = model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
            print("\n Saved h5 json model to disk with name model.json ")

        model.save_weights("model.h5")
        print("\n Saved model to disk with name model.h5")
        print("Training done")

        pred = model.predict(np.array(x_post))
        pred = pred > 0.5
        for i in range(0, len(posts)):
            print('Document name: %s, is %s' % (data['filename'][i], text_labels[np.argmax(pred[i])]))
            dlp_data['filename'].append(data['filename'][i])
            dlp_data['tags'].append(text_labels[np.argmax(pred[i])])

        df = pd.DataFrame(dlp_data, columns=['filename', 'tags'])
        df.to_csv('dlp.csv', encoding="utf-8")

        print('Saved CSV model')
        json_file = open('model.json', 'r')
        loaded_json_model = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_json_model)

        loaded_model.load_weights("model.h5")
        print("Loaded model from disk")

        loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        score = loaded_model.evaluate(x_test, y_test, verbose=1)
        print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))

    def relearn(dict_csv='dlp.csv', acl_csv='acl.csv'):
        old_lists = pd.read_csv(dict_csv, engine='python')
        new_lists = pd.read_csv(acl_csv, engine='python')
        new_dict = {'filename': [], 'tags': []}
        new_dict['filename'].extend(old_lists['filename'])
        new_dict['tags'].extend(old_lists['tags'])
        dlp.make_dataset(new_dict)
        dlp.trainer()

    def acl(dlp_file="acl.csv"):
        dlp_file = pd.read_csv(dlp_file)
        directory = ps.get('folder_protect', 'folder') + '/'
        for row in range(0, len(dlp_file)):
            if dlp_file['tags'][row] == 'confidential':
                # function to get and set ACL
                access_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],
                                                            win32security.DACL_SECURITY_INFORMATION)
                # function to get owner info of a file
                owner_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],
                                                           win32security.OWNER_SECURITY_INFORMATION)

                # lookup for SID of user
                everyone, domain, type = win32security.LookupAccountName("", "Everyone")
                admins, domain, type = win32security.LookupAccountName("", "Administrators")
                owner_sid = owner_info.GetSecurityDescriptorOwner()

                # set permission
                dacl = win32security.ACL()
                dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.SECURITY_NULL_RID, everyone)
                dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE,
                                         owner_sid)
                dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)

                # EXECUTE ORDER 66!!!
                access_info.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(directory + dlp_file['filename'][row],
                                              win32security.DACL_SECURITY_INFORMATION, access_info)
                print("File %s is now protected." % dlp_file['filename'][row])

            elif dlp_file['tags'][row] == 'public':
                # function to get and set ACL
                access_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],
                                                            win32security.DACL_SECURITY_INFORMATION)
                # function to get owner info of a file
                owner_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],
                                                           win32security.OWNER_SECURITY_INFORMATION)

                # lookup for SID of user
                everyone, domain, type = win32security.LookupAccountName("", "Everyone")
                admins, domain, type = win32security.LookupAccountName("", "Administrators")
                owner_sid = owner_info.GetSecurityDescriptorOwner()

                # set permission
                dacl = win32security.ACL()
                dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, everyone)

                # EXECUTE ORDER 66!!!
                access_info.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(directory + dlp_file['filename'][row],
                                              win32security.DACL_SECURITY_INFORMATION, access_info)

    def run_all():
        changes = []
        list_files = {'filename': [], 'tags': []}
        files = ''

        # Training
        if dlp.is_first_run():
            print("No H5 model found, training our ML system according to your file")
            try:
                files = ps.get('folder_protect', 'folder')  # TODO list dir dari inputan user
                if os.path.isdir(files + '/confidential'):
                    temp1 = os.listdir(files + '/confidential')
                    for file in temp1:
                        list_files['tags'].append('confidential')
                    list_files['filename'].extend(file for file in temp1 if ".pdf" in file)
                if os.path.isdir(files + '/public'):
                    temp1 = os.listdir(files + '/public')
                    for file in temp1:
                        list_files['tags'].append('public')
                    list_files['filename'].extend(file for file in temp1 if ".pdf" in file)
            except:
                pass
            dlp.make_dataset(list_files)
            dlp.trainer()
            h5_file = ps.get('machine_learning', 'h5')
            h5json_file = ps.get('machine_learning', 'weight')
            tokenizer_file = ps.get('pickle_file', 'pickle')

        # Checking
        try:
            while True:
                list = []
                clog = open('clog.txt', 'r')
                for line in clog:
                    line = line.split(', ')
                    line = ''.join(line[-1:]).strip()
                    changes.append(line)
                changes = dlp.list_dupe_del(changes)
                # biar clog.txt-nya bersih
                clog = open('clog.txt', 'w')
                clog.close()

                list.extend(file for file in changes if ".pdf" in file)
                dlp.make_dataset(list)
                print('list making complete, going into checking session')
                dlp.checker()
                dlp.acl()
                time.sleep(600)

        except ValueError as e:
            print(e)


if __name__ == '__main__':
    dlp.run_all()
