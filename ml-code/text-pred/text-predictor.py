import collections
import numpy as np
np.random.seed(42)
import pprint
import json
import tensorflow as tf
tf.set_random_seed(42)
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.layers import LSTM, Dropout
from keras.callbacks import ModelCheckpoint
from keras.layers.core import Dense, Activation, Dropout, RepeatVector
from keras.optimizers import RMSprop
import argparse
import heapq

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser()
parser.add_argument('op', type=str, default="train", help='An integer: 1 to train, 2 to test')
parser.add_argument('textdata', type=str, help='text')
args = parser.parse_args()
quotes = args.textdata

with open('data/train.txt','r',encoding='utf-8') as f:
    data = f.read().replace("\n"," _eos_ ").lower().split()

word_to_id = dict()
with open('data/dictionary.json','r') as wti:
    word_to_id = json.loads(wti.read())

id_to_word = dict({(i,c) for c,i in word_to_id.items()})

tr_data = [word_to_id[word] for word in data if word in word_to_id]
print(word_to_id)
EOS_INDEX = word_to_id["_eos_"]
HOTEL_INDEX = word_to_id["_hotel_"]
CITY_INDEX = word_to_id["_city_"]
print("vocablury: ",len(word_to_id))
l = np.split(tr_data,[i for i,x in enumerate(tr_data) if x==EOS_INDEX])

ml=0

for k in range(len(l)):
    l[k] = l[k].tolist()
    if l[k][0] == EOS_INDEX:
        l[k].remove(l[k][0])

    if len(l[k])>ml:
        ml = len(l[k])

for k in range(len(l)):
    for o in range(len(l[k]),ml):
        l[k].append(-1)
pp.pprint(l)

# main = []
# for ll in l:
#     x = []
#     x.append(ll)
#     c1 = collections.Counter(ll)
#     x.append(c1[HOTEL_INDEX])
#     x.append(c1[CITY_INDEX])
#     main.append(x)

# pp.pprint(main)
unique_words = [k for k,v in word_to_id.items()]
SEQUENCE_LENGTH = ml
step=1
sentences = []
next_word = []
for i in range(0,len(data) - SEQUENCE_LENGTH,step):
    sentences.append(data[i : i + SEQUENCE_LENGTH])
    next_word.append(data[i + SEQUENCE_LENGTH])
print("training examples length: ",len(sentences))

X = np.zeros((len(sentences), SEQUENCE_LENGTH, len(unique_words)), dtype=np.int32)
y = np.zeros((len(sentences), len(unique_words)), dtype=np.int32)
for i, sentence in enumerate(sentences):
    for t, ww in enumerate(sentence):
        X[i, t, word_to_id[ww]] = 1
    y[i, word_to_id[next_word[i]]] = 1

def prepare_input(text):
    text = text.lower()
    text = text.split(" ")
    x = np.zeros((1, SEQUENCE_LENGTH, len(unique_words)))
    for t, char in enumerate(text):
        x[0, t, word_to_id[char]] = 1
    return x

def sample(preds, top_n=3):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds)
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    return heapq.nlargest(top_n, range(len(preds)), preds.take)
    
def predict_completion(text):
    original_text = text
    completion = ''
    while True:
        x = prepare_input(text)
        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, top_n=1)[0]
        next_w = id_to_word[next_index]
        text = text[1:] + next_w
        completion += next_w + ' '
        
        if len(original_text + completion) + 2 > len(original_text) and next_w == '_eos_':
            return completion

def predict_completions(text, n=3):
    x = prepare_input(text)
    preds = model.predict(x, verbose=0)[0]
    proba = sample(model.predict_proba(x,verbose=0)[0],n)
    # print("proba: ",proba)
    next_indices = sample(preds, n)
    # return [id_to_word[idx] + predict_completion(text[1:] + id_to_word[idx]) for idx in next_indices]
    # print("next indices : ",next_indices)
    words = [id_to_word[i] for i in next_indices]
    lis = sorted(list(zip(words,proba)),key=lambda q: q[1],reverse=True)
    ccc = [a for a,b in lis]
    return ccc



# print("X : ",X)
# print("y : ",y)
BATCH_SIZE = 4
EPOCHS = 15000

chkptr = ModelCheckpoint(filepath='models/model-{epoch:02d}.hdf5', verbose=1)

model = Sequential()
model.add(LSTM(256, input_shape=(ml,len(word_to_id))))
model.add(Dropout(0.2))
model.add(Dense(len(word_to_id)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['categorical_accuracy'])
print(model.summary())

if args.op == "train":
    history = model.fit(X,y,validation_split=0.05,batch_size=BATCH_SIZE,epochs=EPOCHS,shuffle=True, callbacks=[chkptr]).history
# elif args.op == "test":
#     model = load_model('models/model-200.hdf5')
#     for q in quotes:
#         v = ""
#         seq = q.lower()
#         print(seq)
#         print(predict_completions(seq,8))
#         print("")

elif args.op == "test":
    model = load_model('models/model-200.hdf5')
    v = ""
    seq = quotes.lower()
    print(seq)
    for i in range(8):
        x=predict_completions(seq, 1)
        v += x[0] + " "
        seq=x[0]
    print(" ",v)