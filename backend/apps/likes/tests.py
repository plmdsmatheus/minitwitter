from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.posts.models import Post
from apps.likes.models import Like

User = get_user_model()

class LikeTests(APITestCase):
    def setUp(self):
        # Create two users and a post
        self.u1 = User.objects.create_user(email='u1@ex.com', username='u1', password='pass1234')
        self.u2 = User.objects.create_user(email='u2@ex.com', username='u2', password='pass1234')
        self.post = Post.objects.create(text='Test Post', author=self.u1)

        # Obtain JWT tokens
        login_url = reverse('token-obtain-pair')
        resp1 = self.client.post(login_url, {'email': self.u1.email, 'password': 'pass1234'}, format='json')
        resp2 = self.client.post(login_url, {'email': self.u2.email, 'password': 'pass1234'}, format='json')
        self.token1 = resp1.data['access']
        self.token2 = resp2.data['access']

        # URLs
        self.like_url    = reverse('post-like', args=[self.post.id])
        self.unlike_url  = reverse('post-unlike', args=[self.post.id])
        self.list_likes  = reverse('post-likes-list', args=[self.post.id])

    def auth(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_like_and_duplicate(self):
        """Authenticated user can like a post and avoid duplicates"""
        # First like
        r1 = self.client.post(self.like_url, **self.auth(self.token2))
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.u2, post=self.post).exists())

        # Duplicate like should fail
        r2 = self.client.post(self.like_url, **self.auth(self.token2))
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', r2.data)

    def test_unlike_and_invalid(self):
        """Authenticated user can unlike a post and cannot unlike if not liked"""
        # Unlike without liking first
        r1 = self.client.delete(self.unlike_url, **self.auth(self.token2))
        self.assertEqual(r1.status_code, status.HTTP_400_BAD_REQUEST)

        # Like then unlike
        Like.objects.create(user=self.u2, post=self.post)
        r2 = self.client.delete(self.unlike_url, **self.auth(self.token2))
        self.assertEqual(r2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(user=self.u2, post=self.post).exists())

    def test_list_likes(self):
        """Anyone can list the likes of a post"""
        # Create multiple likes
        Like.objects.create(user=self.u1, post=self.post)
        Like.objects.create(user=self.u2, post=self.post)

        r = self.client.get(self.list_likes)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # Should return two like objects
        self.assertEqual(len(r.data), 2)
