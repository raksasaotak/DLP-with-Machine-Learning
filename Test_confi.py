from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, Activation
from keras_preprocessing import text

import numpy as np
import pandas as pd
from sklearn import preprocessing


data = pd.read_csv("example_test.csv")

train_size = int(len(data) * .7 )
train_posts = data['documents'][:train_size]
train_tags = data['tags'][:train_size]
test_posts = data['documents'][train_size:]
test_tags = data['tags'][train_size:]

print("Training entries: {}, labels: {}".format(len(train_posts), len(train_tags)))
print(train_tags[0])

vocab_size = 10000
tokenize = text.Tokenizer(num_words=vocab_size)
tokenize.fit_on_texts(train_posts)

x_train = tokenize.texts_to_matrix(train_posts)
x_test = tokenize.texts_to_matrix(test_posts)

encoder = preprocessing.LabelBinarizer()
encoder.fit(train_tags)
y_train = encoder.transform(train_tags)
y_test = encoder.transform(test_tags)

num_labels = len(np.unique(y_train))
batch_size = 1024

model = Sequential()

model.add(Dense(512, input_shape=(vocab_size,)))
model.add(Activation('relu'))

model.add(Dense(num_labels))
model.add(Activation('softmax'))

model.compile(loss='sparse_categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

history = model.fit(x_train, y_train,
                    batch_size=batch_size,
                    epochs=200,
                    verbose=1,
                    validation_split=0.1)

score = model.evaluate(x_test, y_test,
                       batch_size=batch_size, verbose=1)
print('Test score:', score[0])
print('Test accuracy:', score[1])

for i in range(30):
    prediction = model.predict(np.array([x_test[i]]))

text_labels = encoder.classes_
predicted_label = text_labels[np.argmax(prediction[0])]
print(test_posts.iloc[i][:50], "...")
print('Actual label:' + test_tags.iloc[i])
print("Predicted label: " + predicted_label)

model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)

model.save_weights("model.h5")
print("\n Saved model to disk")



json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

loaded_model.load_weights("model.h5")
print("Loaded model from disk")


loaded_model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
score = loaded_model.evaluate(x_test, y_test, verbose=1)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1] * 100))