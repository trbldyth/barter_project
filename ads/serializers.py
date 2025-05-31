from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import base64
from .models import Category, Condition, Ad, ExchangeProposal
from users.serializers import UserDetailSerialzier

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'title', 'slug')


class ConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Condition
        fields = ('id', 'title', 'slug')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AdSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True)
    condition = serializers.PrimaryKeyRelatedField(
        queryset=Condition.objects.all())
    image_url = Base64ImageField(required=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ad
        fields = ('id', 'user', 'title', 'description',
                  'image_url', 'category', 'condition', 'created_at')
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        category = validated_data.pop('category')
        new_ad = Ad.objects.create(**validated_data)
        new_ad.category.set(category)
        return new_ad

    def update(self, instance, validated_data):
        if 'category' not in validated_data:
            raise serializers.ValidationError('Category field is required')
        if 'condition' not in validated_data:
            raise serializers.ValidationError('Condition field is required')
        category_data = validated_data.pop('category')
        validated_data.pop('user', None)
        instance.category.set(category_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(
            instance.category, many=True).data
        representation['condition'] = ConditionSerializer(
            instance.condition).data
        representation['user'] = UserDetailSerialzier(instance.user).data
        return representation

    def validate_category(self, value):
        if not value:
            raise serializers.ValidationError(
                "Category field cannot be empty.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Tags field cannot contain duplicate values.")
        return value

    def validate_condition(self, value):
        if not value:
            raise serializers.ValidationError(
                "Condition field cannot be empty.")
        return value


class ExchangeListSerializer(serializers.ModelSerializer):
    sender_ad_id = serializers.ReadOnlyField(source='ad_sender.id')
    sender_ad_title = serializers.ReadOnlyField(source='ad_sender.title')
    sender_ad_user = serializers.ReadOnlyField(source='ad_sender.user.id')
    sender_ad_description = serializers.ReadOnlyField(
        source='ad_sender.description')
    sender_ad_condition = serializers.ReadOnlyField(
        source='ad_sender.condition.id')
    sender_ad_category = CategorySerializer(
        source='ad_sender.category', many=True, read_only=True)
    sender_ad_image_url = Base64ImageField(
        source='ad_sender.image_url', read_only=True)
    receiver_ad_id = serializers.ReadOnlyField(source='ad_receiver.id')
    receiver_ad_title = serializers.ReadOnlyField(source='ad_receiver.title')
    receiver_ad_user = serializers.ReadOnlyField(source='ad_receiver.user.id')
    receiver_ad_description = serializers.ReadOnlyField(
        source='ad_receiver.description')
    receiver_ad_condition = serializers.ReadOnlyField(
        source='ad_receiver.condition.id')
    receiver_ad_category = CategorySerializer(
        source='ad_receiver.category', many=True, read_only=True)
    receiver_ad_image_url = Base64ImageField(
        source='ad_receiver.image_url', read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = ('sender_ad_id', 'sender_ad_title', 'sender_ad_user',
                  'sender_ad_description', 'sender_ad_condition',
                  'sender_ad_category', 'sender_ad_image_url',
                  'receiver_ad_id', 'receiver_ad_title',
                  'receiver_ad_user', 'receiver_ad_description',
                  'receiver_ad_condition', 'receiver_ad_category',
                  'receiver_ad_image_url',
                  'comment', 'status', 'created_at')
        read_only_fields = ('comment', 'created_at',)


class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.none())
    ad_receiver = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.none())
    status = serializers.ReadOnlyField()

    class Meta:
        model = ExchangeProposal
        fields = ('ad_sender', 'ad_receiver', 'comment', 'status')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request') is not None:
            if self.context.get('request').method == 'POST':
                self.fields['status'] = serializers.ReadOnlyField()
                user = self.context['request'].user
                to_user = self.context.get('user_id')
                target = get_object_or_404(User, id=to_user)
                if user and user.is_authenticated:
                    self.fields['ad_sender'].queryset = Ad.objects.filter(
                        user=user)
                if to_user:
                    self.fields['ad_receiver'].queryset = Ad.objects.filter(
                        user=target)

    def validate(self, data):
        request = self.context.get('request')
        current_user = request.user
        receiver_user = get_object_or_404(User, id=self.context.get('user_id'))

        if data['ad_sender'].user != current_user:
            raise serializers.ValidationError('You are not owner of sended ad')
        if data['ad_receiver'].user != receiver_user:
            raise serializers.ValidationError(
                'This user isnt owner of received ad!')
        if data['ad_sender'].user == data['ad_receiver'].user:
            raise serializers.ValidationError('You cant propose yourself!')
        return data
