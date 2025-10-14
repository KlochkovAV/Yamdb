from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from api.utils import generate_confirmation_code, send_code_email
from api.validations import UsernameValidationMixin
from reviews.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категории без поля id."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        source='genres'
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле жанров не может быть пустым.'
            )
        return value

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели произведения c категорией без поля id."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True, source='genres')
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва на произведение."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date',)
        model = Review

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                    title_id=self.context['view'].kwargs.get('title_id'),
                    author=self.context['request'].user
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв к этому произведению.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария к отзыву."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date',)
        model = Comment


class SignUpSerializer(
    serializers.Serializer,
    UsernameValidationMixin
):
    """Сериализатор для самостоятельной регистрации."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH, required=True)
    username = serializers.CharField(max_length=MAX_NAME_LENGTH, required=True)

    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {
            'email': {
                'validators': (),
            },
            'username': {
                'validators': (),
            },
        }

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email, username=username):
            return data

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует, '
                'но email не совпадает'
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует, '
                'но username не совпадает'
            )
        return data

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        confirmation_code = generate_confirmation_code()
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'confirmation_code': confirmation_code
            }
        )
        send_code_email(email, confirmation_code)
        return user


class AdminCreateUserSerializer(
    serializers.ModelSerializer,
    UsernameValidationMixin
):
    """Сериализатор для регистрации пользователя админом."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(write_only=True)
    confirmation_code = serializers.CharField(required=True,
                                              write_only=True)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if (not confirmation_code
           or confirmation_code != user.confirmation_code):
            raise serializers.ValidationError(
                {'non_field_errors': ['Неверный код подтверждения']},
                code='invalid_code'
            )
        return data

    def create(self, validated_data):
        user = User.objects.get(username=validated_data['username'])
        user.is_active = True
        token = RefreshToken.for_user(user)
        user.confirmation_code = None
        user.save()
        return {
            'access': str(token.access_token),
        }


class UserSerializer(AdminCreateUserSerializer):
    """Сериализатор для модели пользователя."""

    class Meta(AdminCreateUserSerializer.Meta):
        read_only_fields = ('role',)
