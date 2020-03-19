from tqdm import tqdm

class MessageTree():
    def __init__(self):
        self.db = []

    def __getitem__(self, key):
        return self.db[key]

    def __len__(self):
        return len(self.db)

    def add_node(self, message, parent=None):
        idx = len(self.db)
        if message is not None:
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


def verify_node(node):
    '''Utility function to check a node is not None and that the message length is below a threshold
    '''
    if (
        node is not None
    ):
        return True
    else:
        return False

def _add_seq_tags(text):
    '''Utility function to add tags to start and end of sequences
    '''
    return '<sos> ' + text + ' <eos>'


def build_dataset_from_tree(
    msg_tree,
    max_context_length,
    add_seq_tags,
    verbose
):
    '''Function to convert tree of conversations examples of (context, response)

    Args:
        msg_tree (MessageTree): tree of conversation turns
        max_context_length (int): maximum number of message turns to include in context
        add_seq_tags (bool): whether to add <SoS> / <EoS> tags at the beginning and end of messages

    Returns:
        dataset: list of [contexts, responses]
    '''
    contexts = []
    responses = []

    for node in tqdm(msg_tree, desc='Creating dataset', disable=not verbose):
        # Iterate over nodes of the message tree
        if verify_node(node) and\
                verify_node(node.get_parent()):

            response = node.message
            if add_seq_tags:
                response = _add_seq_tags(response)
            context = []
            n = 0
            node = node.get_parent()
            while verify_node(node) and n < max_context_length:
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
        max_context_length=None,
        combine_contexts=True,
        add_seq_tags=True,
        verbose=True
):
    '''Function to convert nested conversation lists into examples of (context, response)

    Args:
        source_data (2d array, list[lists]): 2d data structure with data organised by \
            [[conversation1], [conversation2]]
        max_context_length (int): maximum number of message turns to include in context
        combine_contexts (bool): whether to combine messages in the context into a single string
        add_seq_tags (bool): whether to add <SoS> / <EoS> tags at the beginning and end of messages
        verbose (bool): whether to print progress

    Returns:
        dataset: list of [contexts, responses]
    '''

    msg_tree = MessageTree()
    for conversation in tqdm(source_data, desc='Creating tree', disable=not verbose):
        msg_tree.add_list(conversation)

    message_dataset = build_dataset_from_tree(
        msg_tree,
        max_context_length,
        add_seq_tags,
        verbose)

    if combine_contexts:
        for i, context in enumerate(message_dataset[0]):
            message_dataset[0][i] = ' '.join(context)

    return message_dataset
