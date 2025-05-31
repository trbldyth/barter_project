from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (AdViewSet, CategoryViewSet, ConditionViewSet,
                    ExchangeListViewSet, ExchangeProposalViewSet)

app_name = 'ads'

router = DefaultRouter()
router.register('ads', AdViewSet)
router.register('categories', CategoryViewSet)
router.register('conditions', ConditionViewSet)
router.register('exchanges', ExchangeListViewSet, basename='exchanges')

urlpatterns = [
    re_path(r'^propose/(?P<user_id>\d+)/$',
            ExchangeProposalViewSet.as_view({'post': 'propose_exchange'})),
    re_path(r'^exchanges/(?P<exchange>\d+)/$',
            ExchangeProposalViewSet.as_view({
                'get': 'pending_exchanges',
                'put': 'pending_exchanges'})),
    path('', include(router.urls)),
]
