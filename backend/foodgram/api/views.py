from django.db.models import Sum
from django.http import HttpResponse
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
from food.models import Ingredient, Tag, Recipe, Favorite, Shopping_cart, \
    Recipe_ingredient
from foodgram.settings import FILE_NAME
from users.models import User, Subscribe


"""================================= users ================================="""


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
    def subscribe(self, request, **kwargs):
        """
        Подписывает или отписывает текущего пользователя на/от указанного
        автора
        @param self: экземпляр класса UserViewSet
        @param request: объект HttpRequest с данными подписки/отписки
        @param kwargs: словарь, содержащий идентификатор автора, на/от которого
                       выполняется подписка/отписка
        @return: объект Response с данными подписки/отписки и соответствующим
                 статусом HTTP.
        """
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = SubscribeAuthorSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


"""================================= food =================================="""


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


class RecipeViewSet(viewsets.ModelViewSet):
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
    def favorite(self, request, **kwargs):
        """
        Добавляет рецепт в избранное или удаляет его из избранного
        :param request: запрос с данными
        :param kwargs: параметры маршрута
        :return: возвращает сериализованные данные рецепта или ошибку
        """
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        """
        Добавляет рецепт в список покупок или удаляет его из списка
        :param request: запрос с данными
        :param kwargs: параметры маршрута
        :return: возвращает сериализованные данные рецепта или ошибку
        """
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Shopping_cart.objects.filter(user=request.user,
                                                recipe=recipe).exists():
                Shopping_cart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Shopping_cart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        """
        Возвращает файл с текстом, содержащим список покупок пользователя
        :param request: запрос с данными
        :param kwargs: параметры маршрута
        :return: возвращает файл в формате 'text/plain'
        """
        ingredients = (
            Recipe_ingredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Список покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = f'attachment; filename={FILE_NAME}'
        return file
