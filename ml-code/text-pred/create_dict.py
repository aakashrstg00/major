import collections
import json

with open('data/train.txt','r',encoding='utf-8') as f:
    data = f.read().replace("\n"," _eos_ ").split()

counter = collections.Counter(data)
count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

words, _ = list(zip(*count_pairs))
word_to_id = dict(zip(words, range(len(words))))

k = json.dumps(word_to_id)

with open('data/dictionary.json', 'w') as f:
    f.write(k)