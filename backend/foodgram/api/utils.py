import dataclasses

from rest_framework import status
from rest_framework.response import Response


@dataclasses.dataclass
class CreateDeleteMixin:
    lookup_field = None
    serializer_class = None
    format_kwarg = None

    def create_delete_or_scold(self, model, obj, request):
        instance = model.objects.filter(user=request.user,
                                        **{self.lookup_field: obj})
        name = model.__name__

        if request.method == 'DELETE' and not instance:
            return Response(
                {'errors': f'Этот объект не был в вашем {name} листе.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            instance.delete()
            return Response({'detail': f'Успешное удаление из {name} листа.'},
                            status=status.HTTP_204_NO_CONTENT)

        if instance:
            return Response(
                {'errors': f'Этот объект уже был в вашем {name} листе.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.create(user=request.user, **{self.lookup_field: obj})
        serializer = self.serializer_class(
            obj,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
