import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import whatsapp


class IdentityTest(unittest.TestCase):
    def test_phone_chat_includes_new_lid_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            messages = os.path.join(directory, 'messages.db')
            session = os.path.join(directory, 'whatsapp.db')
            with sqlite3.connect(messages) as db:
                db.executescript('''CREATE TABLE chats (jid TEXT, name TEXT, last_message_time TEXT);
                    CREATE TABLE messages (id TEXT, chat_jid TEXT, sender TEXT, content TEXT, timestamp TEXT, is_from_me INTEGER, media_type TEXT);
                    INSERT INTO chats VALUES ('123@s.whatsapp.net','123','2026-01-01T00:00:00');
                    INSERT INTO chats VALUES ('456@lid','456','2026-01-02T00:00:00');
                    INSERT INTO messages VALUES ('old','123@s.whatsapp.net','123','old','2026-01-01T00:00:00',0,'');
                    INSERT INTO messages VALUES ('new','456@lid','456','new','2026-01-02T00:00:00',0,'');''')
            with sqlite3.connect(session) as db:
                db.executescript("CREATE TABLE whatsmeow_lid_map (lid TEXT, pn TEXT); INSERT INTO whatsmeow_lid_map VALUES ('456','123');")
            with patch.object(whatsapp, 'MESSAGES_DB_PATH', messages), patch.object(whatsapp, 'SESSION_DB_PATH', session, create=True):
                result = whatsapp.list_messages(chat_jid='123@s.whatsapp.net', include_context=False)
                self.assertIn('new', result)
                self.assertIn('old', result)
                self.assertEqual(whatsapp.get_direct_chat_by_contact('123').jid, '456@lid')

if __name__ == '__main__':
    unittest.main()
