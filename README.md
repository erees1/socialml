# socialml
Package to convert social media message exports to a dataset suitable for seq2seq modelling.

Currently supports:
* Facebook messenger (json archive)

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

# Convert the array of conversations into training examples in the form of (context, response), 
# context is a n number of messages that will be used to predict the response up to a maxium of 7 in this 
# case
dataset = socialml.make_training_examples(
        arr,
        max_message_length=128,
        max_context_length=7,
        remove_hyperlinks=False,
        combine_contexts=True,
        add_seq_tags=True
    ):

```
