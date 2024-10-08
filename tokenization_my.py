# -*- coding: utf-8 -*-
"""Tokenization_My.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-b94MUiOp1h9ubZqna8cDKWsBzF6EPW2

# **Character level tokenization**
"""

#Read the Shakespear data set. You can download it from https://cs.stanford.edu/people/karpathy/char-rnn/shakespear.txt

#read the text file
with open('Shakespear.txt','r') as f:
  text = f.read()

#create a sorted character set
chars = sorted(list(set(text)))
vocab_size = len(chars)
print(''.join(chars))

# create a mapping from the characters to integers
stoi = {ch : i for i , ch in enumerate(chars)}
itos = {i : ch for i , ch in enumerate(chars)}

encode = lambda s : [stoi[c] for c in s] #encoder: take a string, output a list of numbers
decode = lambda l : ''.join([itos[i] for i in l]) #decoder: take a list of numbers, output the string

print(encode("Hi there!"))

string = "안녕하세요 👋 (hello in Korean!)"

print([ord(x) for x in string])

list("안녕하세요 👋 (hello in Korean!)".encode('utf-8'))

"""#**Byte pair encoding**"""

text = "Ｕｎｉｃｏｄｅ! 🅤🅝🅘🅒🅞🅓🅔‽ 🇺‌🇳‌🇮‌🇨‌🇴‌🇩‌🇪! 😄 The very name strikes fear and awe into the hearts of programmers worldwide. We all know we ought to “support Unicode” in our software (whatever that means—like using wchar_t for all the strings, right?). But Unicode can be abstruse, and diving into the thousand-page Unicode Standard plus its dozens of supplementary annexes, reports, and notes can be more than a little intimidating. I don’t blame programmers for still finding the whole thing mysterious, even 30 years after Unicode’s inception."
tokens = text.encode("utf-8") # raw bytes
tokens = list(map(int, tokens)) # convert to a list of integers in range 0..255 for convenience
print('---')
print(text)
print("length:", len(text))
print('---')
print(tokens)
print("length:", len(tokens))

counter = 0

while counter < 10:
  # create a dictionary of token pairs and their counts
  tokenPairCounts = dict()
  for i in range(len(tokens)-1):
    pair = (tokens[i], tokens[i+1])
    if pair in tokenPairCounts:
      tokenPairCounts[pair] += 1
    else:
      tokenPairCounts[pair] = 1

  # order the tokenPairCounts dict based on the value. Get the key with the maximum value
  max_key = max(tokenPairCounts, key=tokenPairCounts.get)
  print(max_key)

  #traverse through the tokens list and replace the max_key with a new token
  i = 0
  while i < len(tokens)-1:
    pair = (tokens[i], tokens[i+1])
    if pair == max_key:
      tokens[i] = 255 + counter
      del tokens[i+1]
    i += 1
  counter +=1

print(tokens)
print(len(tokens))

# Count the consecutive pairs of tokens
def get_stats(ids):
  counts = {}
  for pair in zip(ids,ids[1:]): # create pairs of tokens
    counts[pair] = counts.get(pair,0) + 1
  return counts

print(get_stats(tokens))

# we van reverse the key value pairs and sort the dictionary based on the values
# stats.item() gives you (key,value) tuples

stats = get_stats(tokens)
print(sorted(((v,k) for k,v in stats.items()), reverse=True))

# get the most common token pair
top_pair = max(stats, key = stats.get)
print(top_pair)

def merge(ids, pair, idx):
  # traverse through the ids list and replace the pair with idx
  i = 0
  newids = []
  while i < len(ids):
    #make sure the index do not go out of bound
    if i<len(ids)-1 and (ids[i], ids[i+1]) == pair:
      newids.append(idx)
      i +=2
    else:
      newids.append(ids[i])
      i +=1
  return newids

print(top_pair)
newTokens = merge(tokens, top_pair, 256)
print(newTokens)
print(len(newTokens))

vocab_size = 276
num_merges = vocab_size - 256
ids = list(tokens) #create a copy of the original token list

merges = {}

for i in range(num_merges):
  stats = get_stats(ids)
  pair = max(stats, key = stats.get)
  idx = 256 + i
  print(f"merging {pair} into new token {idx}")
  merges[pair] = idx
  ids = merge(ids, pair, idx)

print(f"token length: {len(tokens)}")
print(f"ids length: {len(ids)}")
print(f"compression ratio: {len(tokens)/len(ids):.2f}X")

"""## **Decoder design**"""

def decoder(ids):
  '''given a list of integers (ids), output a string'''

  # reverse key value pairs of the merges dictionary
  # this helps us to go from the root to the leaves
  reverse_merges = {v:k for k,v in merges.items()}

  for i in range(num_merges):
    new_ids =[]
    for item in ids:
      if item in reverse_merges:
        new_ids.extend(list(reverse_merges[item]))
      else:
        new_ids.append(item)
    ids = new_ids

  # convert the integres back to the characters
  char_list = []
  for j in ids:
    char_list.append(chr(j))
  return "".join(char_list)

print(decoder(ids))

# A mapping from integers to the bytes
vocab = {idx: bytes(idx) for idx in range(256)}
for (p0,p1),idx in merges.items():
  # bytes addition just concatenates them
  vocab[idx] = vocab[p0] + vocab[p1]

def decoder(ids):
  '''given a list of integers (ids), output a string'''

  # concatenate the bytes
  tokens = b"".join(vocab[idx] for idx in ids)
  # decode the byte sequence
  text = tokens.decode("utf-8",errors='replace')
  return text

print(decoder([128]))

vocab = {idx: bytes([idx]) for idx in range(256)}
for (p0, p1), idx in merges.items():
    vocab[idx] = vocab[p0] + vocab[p1]

def decode(ids):
  # given ids (list of integers), return Python string
  tokens = b"".join(vocab[idx] for idx in ids)
  text = tokens.decode("utf-8", errors="replace")
  return text

print(decode([128]))

bin(128)

"""## **Encoder design**"""

def encoder(text):
  '''given a string, output a list of integers (ids)'''
  tokens = text.encode("utf-8")
  ids = list(map(int, tokens))

  vocab_size = 276
  num_merges = vocab_size - 256

  for i in range(num_merges):
    stats = get_stats(ids)
    #pair = max(stats, key = stats.get)
    idx = 256 + i
    ids = merge(ids, pair, idx)
  return ids

print(encoder("Hi there!"))

def encoder_new(text):
  '''given a string, output a list of integers (ids)'''

  # Get a list of raw bytes
  tokens = list(text.encode("utf-8"))

  while len(tokens)>=2: # when the text is a single character or an empty string, the stats is empty
    # get the set of all pairs
    stats = get_stats(tokens)

    # get the pair with the least index
    pair = min(stats, key= lambda p: stats.get(p, float('inf')))

    # if there are no more merging pairs, break the loop
    if pair not in merges:
      break

    # merge the pair
    idx = merges[pair]
    tokens = merge(tokens, pair, idx)
  return tokens

print(encoder_new("Hi there!"))

"""## **Regex**"""

import regex as re

# create the regex pattern
gpt2pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")

# match the pattern aginst the sequence left to right
print(re.findall(gpt2pat, "Hello've world123 how's are you!!!?"))

"""## **tiktoken**"""

!pip install tiktoken

import tiktoken

#GPT-2 (spaces does not merge)
enc = tiktoken.get_encoding("gpt2")
print(enc.encode("    Hello world"))

#GPT-4 (spaces merge)
enc = tiktoken.get_encoding("cl100k_base")
print(enc.encode("    Hello world"))

gpt4pat = re.compile(r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+""")

!wget https://openaipublic.blob.core.windows.net/gpt-2/models/1558M/vocab.bpe
!wget https://openaipublic.blob.core.windows.net/gpt-2/models/1558M/encoder.json

import os, json

with open('encoder.json', 'r') as f:
    encoder = json.load(f) # <--- ~equivalent to our "vocab"

with open('vocab.bpe', 'r', encoding="utf-8") as f:
    bpe_data = f.read()
bpe_merges = [tuple(merge_str.split()) for merge_str in bpe_data.split('\n')[1:-1]]

"""## **Sentencepiece**"""

import sentencepiece as spm

# write a toy.txt file with some random text
with open("toy.txt", "w", encoding="utf-8") as f:
  f.write("SentencePiece is an unsupervised text tokenizer and detokenizer mainly for Neural Network-based text generation systems where the vocabulary size is predetermined prior to the neural model training. SentencePiece implements subword units (e.g., byte-pair-encoding (BPE) [Sennrich et al.]) and unigram language model [Kudo.]) with the extension of direct training from raw sentences. SentencePiece allows us to make a purely end-to-end system that does not depend on language-specific pre/postprocessing.")

# train a sentencepiece model on it
# the settings here are (best effort) those used for training Llama 2
import os

options = dict(
  # input spec
  input="toy.txt",
  input_format="text",
  # output spec
  model_prefix="tok400", # output filename prefix
  # algorithm spec
  # BPE alg
  model_type="bpe",
  vocab_size=400,
  # normalization
  normalization_rule_name="identity", # ew, turn off normalization
  remove_extra_whitespaces=False,
  input_sentence_size=200000000, # max number of training sentences
  max_sentence_length=4192, # max number of bytes per sentence
  seed_sentencepiece_size=1000000,
  shuffle_input_sentence=True,
  # rare word treatment
  character_coverage=0.99995,
  byte_fallback=True,
  # merge rules
  split_digits=True,
  split_by_unicode_script=True,
  split_by_whitespace=True,
  split_by_number=True,
  max_sentencepiece_length=16,
  add_dummy_prefix=True,
  allow_whitespace_only_pieces=True,
  # special tokens
  unk_id=0, # the UNK token MUST exist
  bos_id=1, # the others are optional, set to -1 to turn off
  eos_id=2,
  pad_id=-1,
  # systems
  num_threads=os.cpu_count(), # use ~all system resources
)

spm.SentencePieceTrainer.train(**options)

sp = spm.SentencePieceProcessor()
sp.load('tok400.model')
vocab = [[sp.id_to_piece(idx), idx] for idx in range(sp.get_piece_size())]
vocab

ids = sp.encode("hello 안녕하세요")
print([sp.id_to_piece(idx) for idx in ids])