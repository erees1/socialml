# Module to extract data from social media message exports
import json
import os
import sqlite3

class MessageExtractor():
    '''Base class for social media message extractors with common functions
    '''


class FbMessenger(MessageExtractor):
    '''Extract facebook messenger json data into a useable format for machine learning

        Args:
            filepath (str): filepath to facebook messenger download
    '''
    def __init__(self, filepath):
        self.filepath = filepath

    def _get_conversation_paths(self, inbox_folder):
        '''Create a list of filepaths for each conversation in the form (path, conversation_name)
        '''
        conversation_folders = os.listdir(inbox_folder)
        conversations = []
        for folder in conversation_folders:
            path = inbox_folder + '/' + folder + '/message_1.json'
            conversations.append((path, folder))
        return conversations

    def _load_data(self, conversations):
        '''Returns a list of json objects, one for each conversation
        '''
        json_list = []
        for conv_path, conv_name in conversations:
            with open(conv_path, 'r') as f:
                # fb json_object is dict of conversation with, participants, messages, title, etc
                json_object = json.load(f)
            json_list.append(json_object)
        return json_list

    def _process_data(self, json_list, max_participants, min_messages=1):
        '''Convert list of json objects into lists of messages
        '''
        dataset = []

        if max_participants is None:
            max_participants = float('inf')

        for json_object in json_list:
            if len(json_object['participants']) > max_participants:
                continue
            else:
                contents = []
                time = []
                for message_object in json_object['messages']:
                    # content is a single message in a conversation
                    if 'content' in message_object:
                        # Facebook data badly encoded which this fixes
                        content = message_object['content'].encode('latin-1').decode('utf-8')
                        contents.append(content)
                        time.append(message_object['timestamp_ms'])
                    else:
                        continue
                # Put messages into time order
                content_of_messages = [content for content, _ in sorted(zip(contents, time), key=lambda pair: pair[1])]
                if len(content_of_messages) > min_messages:
                    dataset.append(content_of_messages)
        return dataset

    def extract(self, max_participants=None, min_messages=1):
        '''Extract dataset from self.filepath location

        Args:
            max_participants (int): maximum number of particpants (optional)
            min_messages (int): conversation must have at least this number of messages

        Returns:
            arr: List of conversations each with a list of messages
            '''
        if 'inbox' in self.filepath:
            inbox_folder = self.filepath
        else:
            inbox_folder = self.filepath + '/' + 'inbox'
        conversations = self._get_conversation_paths(inbox_folder)
        json_list = self._load_data(conversations)
        data = self._process_data(json_list, max_participants, min_messages)
        return data

class IMessage(MessageExtractor):
    def __init__(self, filepath):
        self.filepath = filepath
        self._connect_to_databse()

    def _connect_to_databse(self):
        self.con = sqlite3.connect(self.filepath)

    def _get_conversation(self, i):
        c = self.con.cursor()
        sql = f'SELECT text, handle_id \
                    FROM message T1 \
                    INNER JOIN chat_message_join T2 \
                        ON T2.chat_id={i} \
                        AND T1.ROWID=T2.message_id \
                    ORDER BY T1.date'
        c.execute(sql)
        messages = c.fetchall()
        message_text = [i[0] for i in messages if i[0] is not None]
        return message_text

    def _get_number_conversations(self):
        sql = 'select ROWID from chat'
        c = self.con.cursor()
        c.execute(sql)
        return max(c.fetchall())[0]

    def _filter_conversations(self, conversations, max_participants, min_messages):
        filtered_conversations = []
        for conversation in conversations:
            if len(conversation) >= min_messages:
                filtered_conversations.append(conversation)
        return filtered_conversations

    def extract(self, max_participants=None, min_messages=1):
        '''Extract dataset from self.filepath location

        Args:
            max_participants (int): maximum number of particpants (optional)
            min_messages (int): conversation must have at least this number of messages

        Returns:
            arr: List of conversations each with a list of messages
        '''

        n_conversations = self._get_number_conversations()
        conversations = [self._get_conversation(i + 1) for i in range(n_conversations)]
        conversations = self._filter_conversations(conversations, max_participants, min_messages)
        return conversations
