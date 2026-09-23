"""
Scaffold de um módulo de API (BE-02) — apps/customers/api/.

Copie cada bloco para o arquivo indicado e substitua Customer pelo recurso real.
Divisão de responsabilidades: serializer declara o contrato, view coordena HTTP,
service/selector do core (BE-01) carregam domínio, permissão e visibilidade.

Convenções da família (backend-core/references/contratos-entre-skills.md):
- services  `<entidade>_<ação>`   → customer_create, customer_deactivate
- selectors `<entidade>_list_for` / `<entidade>_get`
- a view passa IDs e kwargs; nunca instância de model para o service
- tenant e visibilidade ficam no selector (scope_to_tenant); a view não filtra à mão
- erro de domínio sobe como DomainError; o handler central traduz
"""

# =========================================================
# apps/customers/api/serializers.py
# =========================================================
from rest_framework import serializers


class CustomerCreateSerializer(serializers.Serializer):
    """Entrada: só o que o cliente pode controlar. Tenant NUNCA vem do payload."""

    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()


class CustomerUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)


class CustomerListSerializer(serializers.Serializer):
    """Saída enxuta para listagem."""

    id = serializers.IntegerField()  # use public_id (UUID) se o recurso exigir anti-enumeração
    name = serializers.CharField()
    status = serializers.CharField()


class CustomerDetailSerializer(serializers.Serializer):
    """Saída de detalhe — sem campos internos, sem segredos."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


# =========================================================
# apps/customers/api/filters.py
# =========================================================
import django_filters

from apps.customers.models import Customer


class CustomerFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")

    class Meta:
        model = Customer
        fields = ["status"]


# =========================================================
# apps/customers/api/permissions.py
# =========================================================
# Normalmente VAZIO: a autorização real é require_perm no service e a visibilidade
# (tenant/dono) é o selector. Crie permission class só para barrar cedo algo que
# não depende do objeto (ex.: feature desligada para o plano do tenant).
from rest_framework.permissions import BasePermission


class HasCustomerModule(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("customers.view_customer")


# =========================================================
# apps/customers/api/views.py
# =========================================================
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.customers.selectors import customer_get, customer_list_for
from apps.customers.services import customer_create, customer_deactivate


class CustomerListCreateView(GenericAPIView):
    # GenericAPIView (não APIView): é ela que tem paginate_queryset/filter_queryset.
    permission_classes = [IsAuthenticated, HasCustomerModule]
    filterset_class = CustomerFilter
    ordering_fields = ["created_at", "name"]  # restrito e indexado
    search_fields = ["name", "email"]

    def get_queryset(self):
        # Leitura → selector, que devolve o queryset já escopado (tenant + visibilidade).
        return customer_list_for(actor=self.request.user)

    @extend_schema(responses={200: CustomerListSerializer(many=True)})
    def get(self, request):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        return self.get_paginated_response(CustomerListSerializer(page, many=True).data)

    @extend_schema(request=CustomerCreateSerializer, responses={201: CustomerDetailSerializer})
    def post(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # formato → 400 VALIDATION_ERROR

        # Escrita → service. Regra violada sobe como DomainError (409/422/403...).
        customer = customer_create(actor=request.user, **serializer.validated_data)
        return Response(CustomerDetailSerializer(customer).data, status=status.HTTP_201_CREATED)


class CustomerDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CustomerDetailSerializer})
    def get(self, request, customer_id: int):
        # Objeto de outro tenant → CustomerNotFound → 404 (não confirma existência).
        customer = customer_get(actor=request.user, customer_id=customer_id)
        return Response(CustomerDetailSerializer(customer).data)


class CustomerDeactivateView(GenericAPIView):
    """Transição de negócio tem ação nomeada, não DELETE."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={200: CustomerDetailSerializer})
    def post(self, request, customer_id: int):
        customer = customer_deactivate(actor=request.user, customer_id=customer_id)
        return Response(CustomerDetailSerializer(customer).data)


# =========================================================
# apps/customers/api/urls.py
# =========================================================
from django.urls import path

app_name = "customers"

urlpatterns = [
    path("customers/", CustomerListCreateView.as_view(), name="customer-list"),
    path("customers/<int:customer_id>/", CustomerDetailView.as_view(), name="customer-detail"),
    path(
        "customers/<int:customer_id>/deactivate/",
        CustomerDeactivateView.as_view(),
        name="customer-deactivate",
    ),
]

# =========================================================
# config/urls.py
# =========================================================
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
# from config.api.health import health_live, health_ready
#
# urlpatterns = [
#     path("api/v1/auth/", include("apps.accounts.api.urls")),      # ver references/autenticacao.md
#     path("api/v1/", include("apps.customers.api.urls")),
#     path("api/v1/", include("apps.integrations.webhooks.urls")),   # webhooks: dono é a BE-05
#     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
#     path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
#     path("health/live/", health_live),
#     path("health/ready/", health_ready),
# ]
