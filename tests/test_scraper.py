import unittest
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
from source.scraper import Scraper

class TestScraper(unittest.TestCase):
    """Tests for the Scraper class."""

    @patch('source.scraper.requests.get')
    def test_get_html_successful_http_call(self, mock_get):
        """Test method for the get_html function."""
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'Mocked response text'

        scraper = Scraper()
        result = scraper.get_html()

        self.assertEqual(result, 'Mocked response text')

    @patch('source.scraper.requests.get')
    def test_get_html_failed_http_call(self, mock_get):
        """Test method for the get_html function assuming a failed http call."""
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = \
            requests.exceptions.HTTPError('404 Not Found')

        scraper = Scraper()
        self.assertRaises(requests.exceptions.HTTPError, scraper.get_html)

    @patch('source.scraper.requests.get')
    def test_get_field_hours_successful_http_call(self, mock_get):
        """Test method for the get_field_hours function."""
        mock_html = '''
          <html>
            <div class="schedule-zoom">
              <table class="table">
                <thead>
                  <tr>
                    <th>Sunday</th>
                    <th>Monday</th>
                    <th>Tuesday</th>
                    <th>Wednesday</th>
                    <th>Thursday</th>
                    <th>Friday</th>
                    <th>Saturday</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                      <strong>
                        October 18
                      </strong>
                      <br />
                        6am-6:45am
                      <br />
                        (full field)
                      <br />
                      <br />
                        11:30am-2:45pm
                      <br />
                        (full field)
                    </td>
                    <td>
                      <strong>
                        October 19
                      </strong>
                      <br />
                        6am-7:15am
                      <br />
                        (full field)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </html>'''
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        scraper = Scraper()
        results = scraper.get_field_hours()

        expected_datetime_tuples = [
            (
                datetime(2024, 10, 18, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 18, 6, 45, tzinfo=ZoneInfo("America/New_York"))
            ),
            (
                datetime(2024, 10, 18, 11,30, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 18, 14, 45, tzinfo=ZoneInfo("America/New_York"))
            ),
            (
                datetime(2024, 10, 19, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 19, 7, 15, tzinfo=ZoneInfo("America/New_York"))
            )
        ]

        self.assertIsInstance(results, list)

        for result_tuple, expected_tuple in zip(results, expected_datetime_tuples):
            self.assertIsInstance(result_tuple, tuple)
            self.assertEqual(len(result_tuple), 2)
            self.assertTrue(all(isinstance(dt, datetime) for dt in result_tuple))
            self.assertEqual(result_tuple, expected_tuple)

    @unittest.skip("undefined scrape source behavior")
    def test_get_field_hours_new_year(self):
        """Test method for the get_field_hours function assuming new year change."""
        # created the test function signature, but leaving it blank for now
        # not sure yet what this will actually look like in the asphalt green website
        pass

    @patch('source.scraper.requests.get')
    def test_get_field_hours_failed_http_call(self, mock_get):
        """Test method for the get_field_hours function assuming a failed http call."""
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = \
                requests.exceptions.HTTPError('404 Not Found')

        scraper = Scraper()

        self.assertRaises(requests.exceptions.HTTPError, scraper.get_field_hours)

    @patch('source.scraper.requests.get')
    def test_get_field_hours_failed_html_parse(self, mock_get):
        """Test method for the get_field_hours function assuming a failed html parsing."""
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<html></html>'

        scraper = Scraper()

        self.assertRaises(RuntimeError, scraper.get_field_hours)

    @patch('source.scraper.requests.get')
    def test_get_field_hours_html_typo_space_surrounding_dash(self, mock_get):
        """Test method for the get_field_hours function assuming typo spaces around the timeblock dash"""
        mock_html = '''
          <html>
            <div class="schedule-zoom">
              <table class="table">
                <thead>
                  <tr>
                    <th>Sunday</th>
                    <th>Monday</th>
                    <th>Tuesday</th>
                    <th>Wednesday</th>
                    <th>Thursday</th>
                    <th>Friday</th>
                    <th>Saturday</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                      <strong>
                        October 18
                      </strong>
                      <br />
                        6am -6:45am
                      <br />
                        (full field)
                      <br />
                      <br />
                        11:30am- 2:45pm
                      <br />
                        (full field)
                    </td>
                    <td>
                      <strong>
                        October 19
                      </strong>
                      <br />
                        6am - 7:15am
                      <br />
                        (full field)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </html>'''
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        scraper = Scraper()
        results = scraper.get_field_hours()

        expected_datetime_tuples = [
            (
                datetime(2024, 10, 18, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 18, 6, 45, tzinfo=ZoneInfo("America/New_York"))
            ),
            (
                datetime(2024, 10, 18, 11,30, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 18, 14, 45, tzinfo=ZoneInfo("America/New_York"))
            ),
            (
                datetime(2024, 10, 19, 6, 0, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 10, 19, 7, 15, tzinfo=ZoneInfo("America/New_York"))
            )
        ]

        self.assertIsInstance(results, list)

        for result_tuple, expected_tuple in zip(results, expected_datetime_tuples):
            self.assertIsInstance(result_tuple, tuple)
            self.assertEqual(len(result_tuple), 2)
            self.assertTrue(all(isinstance(dt, datetime) for dt in result_tuple))
            self.assertEqual(result_tuple, expected_tuple)

if __name__ == '__main__':
    unittest.main()
