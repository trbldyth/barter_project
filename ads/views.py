from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, response, permissions, filters, pagination
from rest_framework.decorators import action
from rest_framework.status import (HTTP_403_FORBIDDEN, HTTP_200_OK,
                                   HTTP_201_CREATED, HTTP_400_BAD_REQUEST)
from .models import (Ad, ExchangeProposal,
                     Category, Condition)
from .serializers import (AdSerializer,
                          ExchangeProposalSerializer, CategorySerializer,
                          ConditionSerializer, ExchangeListSerializer)

User = get_user_model()


def user_check(request, object):
    if object.user != request.user:
        return False


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('category__slug', 'condition__slug')
    search_fields = ('title', 'description')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        ad = get_object_or_404(Ad, id=kwargs['pk'])
        if user_check(request, ad) is False:
            return response.Response(
                {'error': 'You are not the author of this ad!'},
                status=HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        ad = get_object_or_404(Ad, id=kwargs['pk'])
        if user_check(request, ad) is False:
            return response.Response(
                {'error': 'You are not the author of this ad!'},
                status=HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAdminUser,)


class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    permission_classes = (permissions.IsAdminUser,)


class ExchangeListViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('ad_sender__user', 'ad_receiver__user', 'status')

    def get_queryset(self):
        own_ads = Ad.objects.filter(user=self.request.user)
        if self.action == 'sended_exchange':
            queryset = ExchangeProposal.objects.filter(
                ad_sender_id__in=own_ads.values_list('id'))
            ad_sender = self.request.query_params.get('ad_sender__user')
            ad_receiver = self.request.query_params.get('ad_receiver__user')
            status = self.request.query_params.get('status')
            if ad_sender:
                queryset = queryset.filter(ad_sender__user=ad_sender)
            if ad_receiver:
                queryset = queryset.filter(ad_receiver__user=ad_receiver)
            if status:
                queryset = queryset.filter(status=status)
            return queryset
        elif self.action == 'received_exchange':
            queryset = ExchangeProposal.objects.filter(
                ad_receiver_id__in=own_ads.values_list('id'))
            status = self.request.query_params.get('status')
            if status:
                queryset = queryset.filter(status=status)
            return queryset

    @action(detail=False, methods=['get'], url_path='sended')
    def sended_exchange(self, request):
        serializer = ExchangeListSerializer(self.get_queryset(), many=True)
        return response.Response(serializer.data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='received')
    def received_exchange(self, request):
        serializer = ExchangeListSerializer(self.get_queryset(), many=True)
        return response.Response(serializer.data, status=HTTP_200_OK)


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExchangeProposalSerializer
        else:
            return ExchangeListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method == 'POST':
            user_id = self.kwargs.get('user_id')
            context['user_id'] = user_id
        return context

    @action(detail=False, methods=['post'], url_path='propose')
    def propose_exchange(self, request, user_id):
        user = request.user.id
        if user == user_id:
            return response.Response({'errors':
                                     ('You cannot propose'
                                      'exchange to yourself')},
                                     status=HTTP_400_BAD_REQUEST)
        data = {'ad_sender': request.data['ad_sender'],
                'ad_receiver': request.data['ad_receiver'],
                'comment': request.data['comment']}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data, status=HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put'], url_path='exchanges')
    def pending_exchanges(self, request, exchange):
        exchange_detail = get_object_or_404(ExchangeProposal, id=exchange)
        if request.method == 'GET':
            serializer = ExchangeListSerializer(exchange_detail)
            return response.Response(serializer.data)
        if request.method == 'PUT':
            if request.user.id == exchange_detail.ad_receiver.user.id:
                ExchangeProposal.objects.filter(id=exchange).update(
                    status=request.data['status'])
                serializer = ExchangeListSerializer(exchange_detail)
                return response.Response(serializer.data,
                                         status=HTTP_201_CREATED)
            else:
                return response.Response(
                    {'error': 'You may not change status!'},
                    status=HTTP_400_BAD_REQUEST)
