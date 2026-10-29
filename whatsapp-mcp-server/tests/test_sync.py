import unittest
from unittest.mock import Mock, patch

import requests
import main


class SyncCheckTest(unittest.TestCase):
    def test_all_tools_expose_opt_in_flag(self):
        for tool in main.mcp._tool_manager.list_tools():
            with self.subTest(tool=tool.name):
                flag = tool.parameters['properties']['skip_sync_check']
                self.assertEqual(flag['type'], 'boolean')
                self.assertIs(flag['default'], False)

    def test_default_rejects_unhealthy_status(self):
        response = Mock()
        response.json.return_value = {'healthy': False, 'reasons': ['disconnected']}
        with patch.object(main.requests, 'get', return_value=response), patch.object(main, 'whatsapp_search_contacts') as search:
            with self.assertRaisesRegex(RuntimeError, 'disconnected'):
                main.search_contacts('Alice')
            search.assert_not_called()

    def test_bypass_reads_without_status_request(self):
        with patch.object(main.requests, 'get', side_effect=requests.ConnectionError) as status, patch.object(main, 'whatsapp_search_contacts', return_value=['stored']) as search:
            self.assertEqual(main.search_contacts('Alice', skip_sync_check=True), ['stored'])
            self.assertEqual(main.search_contacts('Alice', True), ['stored'])
            self.assertEqual(search.call_count, 2)
            status.assert_not_called()

    def test_unavailable_status_still_fails_by_default(self):
        with patch.object(main.requests, 'get', side_effect=requests.ConnectionError):
            with self.assertRaisesRegex(RuntimeError, 'status unavailable'):
                main.search_contacts('Alice')


if __name__ == '__main__':
    unittest.main()
