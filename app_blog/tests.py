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
            compiled_html="<p>Python 3.13</p>"
        )
        GlobalSlug.objects.create(slug="python-3-13-released", page=self.page1)

        self.page2 = Page.objects.create(
            category=self.category,
            title="Django 5.1 Updates",
            json_data={"blocks": []},
            compiled_html="<p>Django 5.1</p>"
        )
        GlobalSlug.objects.create(slug="django-5-1-updates", page=self.page2)

        self.page3 = Page.objects.create(
            category=self.other_category,
            title="Top Travel Destinations",
            json_data={"blocks": []},
            compiled_html="<p>Travel destinations</p>"
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
        
        # ViewSet list is paginated (has keys count, next, previous, results)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        titles = [p['title'] for p in results]
        self.assertIn("Python 3.13 Released", titles)
        self.assertIn("Django 5.1 Updates", titles)
        
        # Test other category
        response_other = self.client.get(url, {'category': self.other_category.id})
        self.assertEqual(response_other.status_code, status.HTTP_200_OK)
        results_other = response_other.data['results']
        self.assertEqual(len(results_other), 1)
        self.assertEqual(results_other[0]['title'], "Top Travel Destinations")
