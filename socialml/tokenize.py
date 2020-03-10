# Module to tokenize dataset from specified vocab
import numpy as np
import json
import sys


class Vocab():
    def __init__(self, initial_vocab):
        with open(initial_vocab) as f:
            vocab = json.load(f)
            self.vocab = np.array(list(vocab))
            self._create_word2int()

    def __len__(self):
        return len(self.vocab)

    def add_to_vocab(self, word):
        if word not in self.word2int:
            self.vocab = np.append(self.vocab, word)
            index = len(self.vocab) - 1
            self._add_to_word2int(word, index)

    def save_vocab(self, fname):
        with open(fname, 'w') as f:
            json.dump(list(self.vocab), f)

    def convert2int(self, ls, add_if_not_present):
        '''
        Takes a list and maps it to integers
        '''
        out = []
        for word in ls:
            try:
                out.append(self.word2int[word])
            except:
                if add_if_not_present:
                    self.add_to_vocab(word)
                    int_ = self.word2int[word]
                else:
                    int_ = self.word2int['<unk>']
                out.append(self.word2int[word])
        return out

    def convert2word(self, ls):
        '''
        Takes a list of ints and converts to words
        '''
        return [self.vocab[i] for i in ls]

    def _create_word2int(self):
        self.word2int = {e: i for i, e in enumerate(self.vocab)}

    def _add_to_word2int(self, word, index):
        self.word2int[word] = index

def pad_data(data):
    max_length = max([len(seq) for seq in data])
    padded_data = np.zeros((len(data), max_length))
    for i, example in enumerate(data):
        padded_data[i, :] = np.hstack((np.zeros(max_length - len(example)), example))
    return data

def tokenize(dataset, vocab, add_if_not_present=True):
    '''Pad and tokenize conversations

    Args:
        vocab (int): maximum number of particpants (optional)
        add_if_not_present (bool): Whether to add word to vocab or use <unk> token

    Returns:
        tokens_array: 2d numpy array of zero padded tokenized conversations
    '''

    list_of_tokens = []
    max_length = max([len(i.split(' ')) for i in dataset])
    tokens_array = np.zeros((len(dataset), max_length), dtype=np.int32)
    for i, example in enumerate(dataset):
        # get words in example
        words = example.lower().split(' ')
        tokens = vocab.convert2int(words, add_if_not_present)
        tokens = np.asarray(tokens, dtype=np.int32)
        tokens_array[i, :len(tokens)] = tokens

        proportion_through = 100 * i / (len(dataset) - np.mod(len(dataset), 10))
        markers = [len(dataset) // 10 * i for i in range(0, 10)]
        markers.append(len(dataset) - 1)
        if i in markers:
            print(f'Processed {proportion_through:0.0f}% of {len(dataset)} examples')

    return tokens_array, vocab
