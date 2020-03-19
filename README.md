# socialml
Package to convert social media message exports to a dataset suitable for seq2seq modelling.

Currently supports:
* Facebook messenger, *inbox folder* (json archive)
* IMessage archive, *chat.db* (sql archive)

## Quick Start

To install run
```
$ python3 -m pip install -U git+git://github.com/erees1/socialml.git
```

## Example usage

```python
fb_message_extractor = socialml.FbMessenger(path_to_fb_archive)
# Extract list of conversations with max of 3 participants that contain at least 2 messages
arr = fb_message_extractor.extract(max_participants=3, min_messages=2)

# Filter the array, produced by the extractor, this will remove *messages* (denoated by the 2) that have hyperlinks, 
# words specified or more than 128 messages. Specifying 1 will remove just the word / hyperlink / truncate the message and 3 will remove the whole conversation
arr = arr2 = socialml.filter_array(arr, remove_hyperlinks=2, remove_words=(2, ['bad_word1', 'bad_word_2']), max_message_length=(2, 128))

# Convert the array of conversations into training examples in the form of (context, response), 
# context is a n number of messages that will be used to predict the response up to a maxium of 7 in this 
# case
dataset = socialml.make_training_examples(
        arr,
        max_context_length=7,
        combine_contexts=True,
        add_seq_tags=True
    ):

```
