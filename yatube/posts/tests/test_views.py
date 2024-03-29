from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from random import randint

from ..models import Group, Post
from ..utils import POST_PER_PAGE
from .constants import (
    AUTHOR_USERNAME,
    GROUP_SLUG,
    URL_INDEX,
    URL_GROUP,
    URL_AUTHOR_PROFILE,
    URL_CREATE_POST,
)

User = get_user_model()

first_page = POST_PER_PAGE
second_page = randint(1, POST_PER_PAGE)
total_posts = POST_PER_PAGE + second_page


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст поста",
            author=cls.author_user,
            group=cls.group,
        )
        cls.POST_URL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT_URL = reverse("posts:post_edit", args=[cls.post.id])

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.author_user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, PostPagesTests.post.text)
            self.assertEqual(post.author, PostPagesTests.post.author)
            self.assertEqual(post.group, PostPagesTests.post.group)
            self.assertEqual(post.pk, PostPagesTests.post.pk)

    def test_index_page_show_correct_context(self):
        response = self.author_client.get(URL_INDEX)
        self.check_post_info(response.context["page_obj"][0])

    def test_group_page_show_correct_context(self):
        response = self.author_client.get(URL_GROUP)
        self.assertEqual(response.context['group'], PostPagesTests.post.group)
        self.check_post_info(response.context["page_obj"][0])

    def test_profile_page_show_correct_context(self):
        response = self.author_client.get(URL_AUTHOR_PROFILE)
        self.assertEqual(
            response.context['author'],
            PostPagesTests.post.author)
        self.check_post_info(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        response = self.author_client.get(PostPagesTests.POST_URL)
        self.check_post_info(response.context["post"])

    def test_create_edit_pages_show_correct_context(self):
        adresses = (URL_CREATE_POST, PostPagesTests.POST_EDIT_URL)
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertIsInstance(
                    response.context["form"].fields["text"],
                    forms.fields.CharField,
                )
                self.assertIsInstance(
                    response.context["form"].fields["group"],
                    forms.fields.ChoiceField,
                )


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title="Тестовое название группы",
            slug=GROUP_SLUG,
            description="Тестовое описание группы",
        )
        cls.PAGES_WITH_PAGINATOR = [URL_INDEX, URL_GROUP, URL_AUTHOR_PROFILE]
        objs = [
            Post(text=f"Пост #{count}", author=cls.user, group=cls.group)
            for count in range(total_posts)
        ]
        Post.objects.bulk_create(objs)

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages_1(self):
        for reverse_address in PaginatorViewsTest.PAGES_WITH_PAGINATOR:
            with self.subTest(reverse_address=reverse_address):
                self.assertEqual(
                    len(
                        self.unauthorized_client.get(
                            reverse_address
                        ).context.get("page_obj")
                    ),
                    POST_PER_PAGE,
                )

    def test_paginator_on_pages_2(self):
        for reverse_address in PaginatorViewsTest.PAGES_WITH_PAGINATOR:
            with self.subTest(reverse_address=reverse_address + "?page=2"):
                self.assertEqual(
                    len(
                        self.unauthorized_client.get(
                            reverse_address + "?page=2"
                        ).context.get("page_obj")
                    ),
                    second_page,
                )
