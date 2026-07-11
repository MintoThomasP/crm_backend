from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Category, Page, GlobalSlug

class BlogCategoryPagesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Categories
        self.category = Category.objects.create(
            name="Tech News",
            short_description="Latest tech news",
            description="Detailed tech news"
        )
        self.cat_slug = GlobalSlug.objects.create(slug="tech-news", category=self.category)

        self.other_category = Category.objects.create(
            name="Lifestyle",
            short_description="Lifestyle blog",
            description="Detailed lifestyle blog"
        )
        self.other_cat_slug = GlobalSlug.objects.create(slug="lifestyle", category=self.other_category)

        # Create Pages
        self.page1 = Page.objects.create(
            category=self.category,
            title="Python 3.13 Released",
            json_data={"blocks": []},
            compiled_html="<p>Python 3.13</p>",
            is_featured=True,
            view_count=10
        )
        GlobalSlug.objects.create(slug="python-3-13-released", page=self.page1)

        self.page2 = Page.objects.create(
            category=self.category,
            title="Django 5.1 Updates",
            json_data={"blocks": []},
            compiled_html="<p>Django 5.1</p>",
            is_featured=False,
            view_count=50
        )
        GlobalSlug.objects.create(slug="django-5-1-updates", page=self.page2)

        self.page3 = Page.objects.create(
            category=self.other_category,
            title="Top Travel Destinations",
            json_data={"blocks": []},
            compiled_html="<p>Travel destinations</p>",
            is_featured=True,
            view_count=5
        )
        GlobalSlug.objects.create(slug="top-travel-destinations", page=self.page3)

    def test_pages_by_category_id_path(self):
        url = reverse('pages-by-category', kwargs={'category_id': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [p['title'] for p in response.data]
        self.assertIn("Python 3.13 Released", titles)
        self.assertIn("Django 5.1 Updates", titles)

    def test_pages_by_category_slug_path(self):
        url = reverse('pages-by-category-slug', kwargs={'category_slug': 'tech-news'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [p['title'] for p in response.data]
        self.assertIn("Python 3.13 Released", titles)
        self.assertIn("Django 5.1 Updates", titles)

    def test_pages_by_category_slug_viewset_action(self):
        url = reverse('page-by-category-slug')
        response = self.client.get(url, {'slug': 'tech-news'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_pages_by_category_id_viewset_filter(self):
        url = reverse('page-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)

    def test_retrieve_increments_view_count(self):
        # Initial view count for page1 is 10
        url = reverse('page-detail', kwargs={'pk': self.page1.id})
        
        # Call retrieve
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], 11)
        
        # Call again
        response = self.client.get(url)
        self.assertEqual(response.data['view_count'], 12)

    def test_featured_action_limit(self):
        url = reverse('page-featured')
        
        # Should return both featured pages (page1, page3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # With limit=1, should return exactly 1
        response = self.client.get(url, {'limit': 1})
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_featured'])

    def test_latest_action_limit(self):
        url = reverse('page-latest')
        
        # With limit=2, should return exactly 2 pages in reverse chronological order
        response = self.client.get(url, {'limit': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Latest should be page3, then page2 (created chronologically page1 -> page2 -> page3)
        self.assertEqual(response.data[0]['id'], self.page3.id)
        self.assertEqual(response.data[1]['id'], self.page2.id)

    def test_popular_action_limit(self):
        url = reverse('page-popular')
        
        # Popular order should be: page2 (50 views), page1 (10 views), page3 (5 views)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.page2.id)
        self.assertEqual(response.data[1]['id'], self.page1.id)
        self.assertEqual(response.data[2]['id'], self.page3.id)
        
        # With limit=2, should return page2 and page1
        response_limited = self.client.get(url, {'limit': 2})
        self.assertEqual(len(response_limited.data), 2)
        self.assertEqual(response_limited.data[0]['id'], self.page2.id)
        self.assertEqual(response_limited.data[1]['id'], self.page1.id)
