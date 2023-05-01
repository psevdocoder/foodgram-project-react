import io

from django.db.models import Sum
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filter import RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnly
from api.serializers import UserReadSerializer, UserCreateSerializer, \
    SetPasswordSerializer, SubscriptionsSerializer, \
    SubscribeAuthorSerializer, IngredientSerializer, TagSerializer, \
    RecipeReadSerializer, RecipeCreateSerializer, RecipeSerializer
from api.utils import CreateDeleteMixin
from food.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart, \
    IngredientAmount
from foodgram.settings import FILE_NAME
from users.models import User, Subscribe


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet, CreateDeleteMixin):
    """
    ViewSet для создания, получения списка и
    получения информации о пользователе.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        """
        Определяет класс сериализатора, используемый для сериализации
        запросов, основываясь на значении параметра self.action
        @param self: экземпляр класса UserViewSet
        @return: класс сериализатора, используемый для данного действия.
        """
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['GET'], pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """
        Возвращает данные текущего пользователя
        @param self: экземпляр класса UserViewSet
        @param request: объект HttpRequest
        @return: объект Response с данными текущего пользователя и
                 статусом HTTP_200_OK.
        """
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """
        Изменяет пароль текущего пользователя
        @param self: экземпляр класса UserViewSet
        @param request: объект HttpRequest с данными нового пароля
        @return: объект Response с сообщением об успешной смене пароля и
                 статусом HTTP_204_NO_CONTENT.
        """
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        """
        Возвращает список подписок текущего пользователя
        @param self: экземпляр класса UserViewSet
        @param request: объект HttpRequest
        @return: объект Response с данными подписок текущего пользователя и
                 статусом HTTP_200_OK.
        """
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        self.serializer_class = SubscribeAuthorSerializer
        self.lookup_field = 'author'
        return self.create_delete_or_scold(Subscribe, author, request)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = (AllowAny, )
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, CreateDeleteMixin):
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        """
        Получает класс сериализатора в зависимости от типа запроса.
        @return: Класс сериализатора
        """
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        self.lookup_field = 'recipe'
        return self.create_delete_or_scold(Favorite, recipe, request)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        self.lookup_field = 'recipe'
        return self.create_delete_or_scold(ShoppingCart, recipe, request)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        purchases = ShoppingCart.objects.filter(user=user)
        file = 'shopping-list.txt'
        with open(file, 'w') as f:
            shop_cart = dict()
            for purchase in purchases:
                ingredients = IngredientAmount.objects.filter(
                    recipe=purchase.recipe.id
                )
                for r in ingredients:
                    i = Ingredient.objects.get(pk=r.ingredient.id)
                    point_name = f'{i.name} ({i.measurement_unit})'
                    if point_name in shop_cart.keys():
                        shop_cart[point_name] += r.amount
                    else:
                        shop_cart[point_name] = r.amount

            for name, amount in shop_cart.items():
                f.write(f'* {name} - {amount}\n')

        return FileResponse(open(file, 'rb'), as_attachment=True)

    def create_delete_or_scold(self, model, recipe, request):
        instance = model.objects.filter(recipe=recipe, user=request.user)
        name = model.__name__
        if request.method == 'DELETE' and not instance:
            return Response(
                {'errors': f'Этот рецепт не был в вашем {name} листе.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if instance:
            return Response(
                {'errors': f'Этот рецепт уже был в вашем {name} листе.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(
            recipe,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
