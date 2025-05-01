from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.posts.models import Post
from apps.follows.models import Follow

User = get_user_model()

class PostTests(APITestCase):
    def setUp(self):
        # Ceate two users
        self.u1 = User.objects.create_user(email='u1@ex.com', username='u1', password='pass1234')
        self.u2 = User.objects.create_user(email='u2@ex.com', username='u2', password='pass1234')

        # get tokens for both users
        login_url = reverse('token-obtain-pair')
        resp1 = self.client.post(login_url, {'email': self.u1.email, 'password': 'pass1234'}, format='json')
        resp2 = self.client.post(login_url, {'email': self.u2.email, 'password': 'pass1234'}, format='json')
        self.token1 = resp1.data['access']
        self.token2 = resp2.data['access']

        # url base for posts
        self.list_url   = reverse('post-list')
    
    def auth(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_create_post(self):
        """ Create post with only text field should return 201. """
        # u1 create a post
        data = {'text': 'Hello world!'}
        resp = self.client.post(self.list_url, data, format='json', **self.auth(self.token1))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'Hello world!')
        self.assertEqual(post.author, self.u1)

    def test_list_feed_only_followed(self):
        """Feed should return only posts from followed users."""
        # u2 create a post
        p = Post.objects.create(text='Post of u2', author=self.u2)
        # if u1 is not following u2, the post should not appear in the feed
        resp = self.client.get(self.list_url, **self.auth(self.token1))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['results']), 0)

        # u1 follows u2
        Follow.objects.create(user=self.u1, following=self.u2)
        resp = self.client.get(self.list_url, **self.auth(self.token1))
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['text'], 'Post of u2')

    def test_update_and_delete_permissions(self):
        """Only the author of the post should be able to update or delete it."""
        # u1 create a post
        resp = self.client.post(self.list_url, {'text':'Original'}, **self.auth(self.token1), format='json')
        post_id = resp.data['id']
        detail = reverse('post-detail', args=[post_id])

        # u2 try update a post → 403
        resp = self.client.patch(detail, {'text':'Hack'}, **self.auth(self.token2), format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # u1 update → 200
        resp = self.client.patch(detail, {'text':'Updated'}, **self.auth(self.token1), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['text'], 'Updated')

        # u2 try deleting → 403
        resp = self.client.delete(detail, **self.auth(self.token2))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # u1 deleted a post → 204 and post should not exist
        resp = self.client.delete(detail, **self.auth(self.token1))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post_id).exists())
