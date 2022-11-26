from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import TEXT_LIMIT, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_post_have_correct_object_names(self):
        post = PostModelTest.post
        expected_object_name = post.text[:TEXT_LIMIT]
        self.assertEqual(expected_object_name, post.text)
