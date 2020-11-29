from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TestContent(TestCase):
    def create_post_for_tests(self):
        self.authorized_client.post(
            reverse('new_post'),
            {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user,
                'group': self.group.pk
                }
            )

    def setUp(self):
        self.authorized_client = Client()
        self.unauthorized_client = Client()
        self.user = User.objects.create(
            username='arthur', password='12345', email='artkam@yandex.ru'
            )
        self.user.save()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='test_group', slug='testgroup')

    def assert_post_to_url(self, url, base):
        response = self.authorized_client.get(url)
        paginator = response.context.get('page')
        if paginator is not None:     
            post = response.context['page'][0]
        else:
            post = response.context['post']
        self.assertEqual(post.text, base.text)
        self.assertEqual(post.author, base.author)
        self.assertEqual(post.group, base.group)

    def vision_on_page(self, base):
        index_url = reverse('index')
        profile_url = reverse('profile',
                              kwargs={'username': self.user.username}
                             )
        post_url = reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': base.id}
            )
        group_posts_url = reverse('group_posts',
                                  kwargs={'slug': self.group.slug}
                                 )
        if base.group == self.group:
            for url in [index_url, profile_url, post_url, group_posts_url]:
                self.assert_post_to_url(url, base)
        else:
            for url in [index_url, profile_url, post_url]:
                self.assert_post_to_url(url, base)

    def test_profile_page_exists_for_registered_user(self):
        resp = self.authorized_client.get(
            reverse('profile', kwargs={
                'username': self.user.username
                })
            )
        self.assertEqual(resp.status_code, 200)

    def test_new_post_page_exists_for_registered_user(self):        
        self.create_post_for_tests()  # create post
        self.assertEqual(Post.objects.count(), 1)

    def test_unauthorized_user_cannot_create_post(self):
        count_posts1 = Post.objects.count()
        resp = self.unauthorized_client.post(reverse('new_post'),
                {
                'text': "Кто ходит в гости по утрам, тот поступает мудро",
                'author': self.user,
                'group': self.group.pk
                })
        count_posts2 = Post.objects.count()
        login_url = reverse('login')
        new_post_url = reverse('new_post')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(
            resp, target_url,
            status_code=302, target_status_code=200
            )
        self.assertEqual(count_posts1, count_posts2)

    def test_post_visible_on_page(self):
        Post.objects.create(
            text='Кто ходит в гости по утрам, тот поступает мудро',
            author=self.user,
            group=self.group
                        )
        base = Post.objects.first()
        self.vision_on_page(base)

    def test_checking_get_part_edit_form(self):
        self.create_post_for_tests()
        base = Post.objects.first()
        resp = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': base.id}
            ))
        self.assertEqual(resp.status_code, 200)        

    def test_checking_post_part_edit_form(self):
        self.create_post_for_tests()
        base = Post.objects.first()
        base.text = 'Это ж-ж-ж-ж неспроста'
        group2 = Group.objects.create(title='test_group2', slug='testgroup2')
        self.authorized_client.post(
            reverse(
                    'post_edit', kwargs={
                    'username': self.user.username,
                    'post_id': base.id
                    }
                ),
            {
                'text': base.text,
                'author': base.author,
                'group': group2.pk
                }
            )
        new_base = Post.objects.first()
        self.vision_on_page(new_base)
        response = self.authorized_client.get(reverse('group_posts',
                                  kwargs={'slug': group2.slug}
                                 ))
        self.assertContains(response, new_base.text)
        response = self.authorized_client.get(reverse('group_posts',
                                  kwargs={'slug': self.group.slug}
                                 ))
        self.assertNotContains(response, new_base.text)