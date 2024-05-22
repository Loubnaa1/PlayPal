from django.test import TestCase, RequestFactory, Client
from unittest.mock import patch
import requests_mock

from .views import TrendingGamesView

# Create your tests here.

class TrendingGamesView(TestCase):
  def test_get_from_cache(self):
    request = RequestFactory().get('/trending-games/')
    with patch('django.core.cache.cache.get') as mock_cache_get:
      mock_cache_get.return_value = ['Game 1', 'Game 2', 'Game3']
      response = TrendingGamesView.as_View()(request)
      self.assertContains(response, 'Game 1')
      self.assertContains(response, 'Game 2')
      self.assertContains(response, 'Game 3')

  def test_trending_games_view(self):
    with requests_mock.Mocker() as m:
      m.get('https://www.reddit.com/r/gaming/new.json?limit=10', json={
        'data': {
          'children': [
            {'data': {'title': 'Game 1'}},
            {'data': {'title': 'Game 2'}},
            {'data': {'title': 'Game 3'}}
          ]
        }
      })

      client = Client()
      response = client.get('/trending-games/')
      self.assertContains(response, 'Game 1')
      self.assertContains(response, 'Game 2')
      self.assertContains(response, 'Game 3')

      response = client.get('/trending-games/')
      self.assertContains(response, 'Game 1')
      self.assertContains(response, 'Game 2')
      self.assertContains(response, 'Game 3')

      m.get('https://www.reddit.com/r/gaming/new.json?limit=10', status_code=500)
      response = client.get('/trending-games/')
      self.assertContains(response, 'Error')