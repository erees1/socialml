class MessageTree():
    def __init__(self):
        self.db = []

    def __getitem__(self, key):
        return self.db[key]

    def add_node(self, message, parent=None):
        idx = len(self.db)
        node = Node(idx, message, parent, self)
        if parent is not None:
            parent_node = self.db[parent]
            parent_node._add_child(idx)
        self.db.append(node)
        return node

    def add_list(self, ls):
        try:
            node = self.add_node(ls[0])
            for message in ls[1:]:
                node = node.add_child(message)
        except IndexError:
            pass

    def get_parent(self, idx):
        node = self.db[idx]
        parent_node = self.db[node.parent]

    def traverse(self, idx, n):
        pass


class Node():
    def __init__(self, idx, message, parent, msgdb):
        self.idx = idx
        self.message = message
        self.parent = parent
        self.children = []
        self.msgdb = msgdb

    def _add_child(self, idx):
        self.children.append(idx)

    def add_child(self, message):
        return self.msgdb.add_node(message, parent=self.idx)

    def get_parent(self):
        if self.parent is not None:
            return self.msgdb[self.parent]
        else:
            return None

    def get_children(self):
        return [self.msgdb[i] for i in self.children]

    def __repr__(self):
        return f"id: {self.idx}, message: {self.message}"

    def __str__(self):
        return self.message


def verify_node(node, max_length, remove_hyperlinks):
    '''Utility function to check a node is not None and that the message length is below a threshold
    '''
    if (
        node is not None
        and len(node.message) < max_length
        and not (remove_hyperlinks * has_hyperlink(node.message))
    ):
        return True
    else:
        return False


def has_hyperlink(text):
    if 'www' in text or 'http' in text:
        return True
    else:
        return False

def _add_seq_tags(text):
    '''Utility function to add tags to start and end of sequnces
    '''
    return '<SoS> ' + text + ' <EoS>'


def build_dataset_from_tree(msg_tree, max_message_length, max_context_length, remove_hyperlinks, add_seq_tags):
    '''Function to convert tree of conversations examples of (context, response)

    Args:
        msg_tree (MessageTree): tree of conversation turns
        max_message_length (int): maximum number of words in a message to be included
        max_context_length (int): maxium number of message turns to include in context
        remove_hyperlinks (bool): whether to remove messages that have hyperlinks in them
        add_seq_tags (bool): whether to add <SoS> / <EoS> tags at the beginning and end of messages

    Returns:
        dataset: list of [contexts, reponses]
    '''
    contexts = []
    responses = []
    if max_message_length is None:
        max_message_length = float('inf')
    if max_context_length is None:
        max_context_length = float('inf')

    for node in msg_tree:
        # Iterate over nodes of the message tree
        if verify_node(node, max_message_length, remove_hyperlinks) and\
                verify_node(node.get_parent(), max_message_length, remove_hyperlinks):

            response = node.message
            if add_seq_tags:
                response = _add_seq_tags(response)
            context = []
            n = 0
            node = node.get_parent()
            while verify_node(node, max_message_length, remove_hyperlinks) and n < max_context_length:
                if add_seq_tags:
                    msg = _add_seq_tags(node.message)
                else:
                    msg = node.message
                context.insert(0, msg)
                node = node.get_parent()
                n += 1
            responses.append(response)
            contexts.append(context)
    return [contexts, responses]


def make_training_examples(
        source_data,
        max_message_length=None,
        max_context_length=None,
        remove_hyperlinks=False,
        combine_contexts=True,
        add_seq_tags=True
    ):
    '''Function to convert nested conversation lists into examples of (context, response)

    Args:
        source_data (2d array, list[lists]): 2d data structure with data organised by \
            [[conversation1], [conversation2]]
        max_message_length (int): maximum number of words in a message to be included
        max_context_length (int): maxium number of message turns to include in context
        remove_hyperlinks (bool): whether to remove messages that have hyperlinks in them
        combine_contexts (bool): whehter to combine messages in the context into a single string
        add_seq_tags (bool): whether to add <SoS> / <EoS> tags at the beginning and end of messages

    Returns:
        dataset: list of [contexts, reponses]
    '''

    msg_tree = MessageTree()
    for conversation in source_data:
        msg_tree.add_list(conversation)

    message_dataset = build_dataset_from_tree(
        msg_tree,
        max_message_length,
        max_context_length,
        remove_hyperlinks,
        add_seq_tags)

    if combine_contexts == True:
        for i, context in enumerate(message_dataset[0]):
            message_dataset[0][i] = ' '.join(context)

    return message_dataset
