import factory
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker
from ..models import Ad, Condition, Category

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(lambda _: fake.user_name())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

    class Meta:
        model = User


class AdminFactory(UserFactory):
    is_staff = True
    is_superuser = True


class ConditionFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=16))
    slug = factory.LazyAttribute(lambda _: slugify(_.title))

    class Meta:
        model = Condition


class CategoryFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=16))
    slug = factory.LazyAttribute(lambda _: slugify(_.title))

    class Meta:
        model = Category


class AdFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    image_url = factory.django.ImageField(filename='test_image.jpg')
    condition = factory.SubFactory(ConditionFactory)

    class Meta:
        model = Ad

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category_item in extracted:
                self.category.add(category_item)
        else:
            self.category.add(CategoryFactory())
