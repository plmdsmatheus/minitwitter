from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.follows.models import Follow

User = get_user_model()

class FollowTests(APITestCase):
    def setUp(self):
        # Craete two users
        self.u1 = User.objects.create_user(email='u1@ex.com', username='u1', password='pass1234')
        self.u2 = User.objects.create_user(email='u2@ex.com', username='u2', password='pass1234')

        # Tokens JWT
        login = reverse('token-obtain-pair')
        r1 = self.client.post(login, {'email':self.u1.email,'password':'pass1234'}, format='json')
        r2 = self.client.post(login, {'email':self.u2.email,'password':'pass1234'}, format='json')
        self.token1 = r1.data['access']
        self.token2 = r2.data['access']

        # URLs
        self.follow_url   = lambda uid: reverse('follow',   args=[uid])
        self.unfollow_url = lambda uid: reverse('unfollow', args=[uid])
        self.list_folls   = reverse('followers-list')
        self.list_following = reverse('following-list')

    def auth(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_cannot_follow_self(self):
        """Try to follow yourself should return 400."""
        resp = self.client.post(self.follow_url(self.u1.id), **self.auth(self.token1))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', resp.data)

    def test_follow_and_duplicate(self):
        """Follow a user and check for duplicates."""
        # u1 follows u2
        resp1 = self.client.post(self.follow_url(self.u2.id), **self.auth(self.token1))
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(user=self.u1, following=self.u2).exists())

        # following again should return 400
        resp2 = self.client.post(self.follow_url(self.u2.id), **self.auth(self.token1))
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', resp2.data)

    def test_unfollow_and_invalid(self):
        """Unfollow a user and check for invalid cases."""
        # u1 tries to unfollow u2 without following this should return 400
        resp1 = self.client.delete(self.unfollow_url(self.u2.id), **self.auth(self.token1))
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)

        # u1 follows u2 and then unfollows
        Follow.objects.create(user=self.u1, following=self.u2)
        resp2 = self.client.delete(self.unfollow_url(self.u2.id), **self.auth(self.token1))
        self.assertEqual(resp2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.filter(user=self.u1, following=self.u2).exists())

    def test_list_followers_and_following(self):
        """List followers and following users."""
        # u2 follows u1
        Follow.objects.create(user=self.u2, following=self.u1)
        # u1 follows u2
        Follow.objects.create(user=self.u1, following=self.u2)

        # How many followers does u1 have?
        r_folls = self.client.get(self.list_folls, **self.auth(self.token1))
        self.assertEqual(r_folls.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r_folls.data), 1)
        self.assertEqual(r_folls.data[0]['id'], self.u2.id)

        # How many users does u1 follow?
        r_following = self.client.get(self.list_following, **self.auth(self.token1))
        self.assertEqual(r_following.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r_following.data), 1)
        self.assertEqual(r_following.data[0]['id'], self.u2.id)
