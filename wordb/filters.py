from django_filters import filters
from django_filters import FilterSet
from .models import Item

class MyCharFilter(filters.CharFilter):
    empty_value = ''

    def filter(self, qs, value):
        print(value)
        if value != self.empty_value:
            return super().filter(qs, value)
        else:
            return super().filter(qs, 'DuMmuY')
        # qs = self.get_method(qs)(**{'%s__%s' % (self.field_name, self.lookup_expr): ""})
        # return qs.distinct() if self.distinct else qs

class MyOrderingFilter(filters.OrderingFilter):
    descending_fmt = '%s (descending)'

class ItemFilterEditkey(FilterSet):
    template_name = "item_filter.html"

    words_text = filters.CharFilter(label='Words', lookup_expr='contains')
    data_text = filters.CharFilter(label='Data', lookup_expr='contains')
    owner = filters.CharFilter(label='Owner', lookup_expr='contains')
    editkey = MyCharFilter(label='Editkey', lookup_expr='exact')
    order_by = MyOrderingFilter(
        fields=(
            ('words_text', 'words_text'),
            ('data_text', 'data_text'),
        ),
        field_labels={
            'words_text': 'words',
            'data_text': 'data',
        },
        label='sorting order'
    )

    class Meta:
        model = Item
        fields = ('editkey','words_text','data_text','owner')

    def __init__(self, *args, **kwargs):
        super(ItemFilterEditkey, self).__init__(*args, **kwargs)
        # at sturtup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()

class ItemFilter(FilterSet):
    words_text = filters.CharFilter(label='Words', lookup_expr='contains')
    data_text = filters.CharFilter(label='Data', lookup_expr='contains')
    owner = filters.CharFilter(label='Owner', lookup_expr='contains')
    order_by = MyOrderingFilter(
        fields=(
            ('words_text', 'words_text'),
            ('data_text', 'data_text'),
        ),
        field_labels={
            'words_text': 'words',
            'data_text': 'data',
        },
        label='sorting order'
    )

    class Meta:
        model = Item
        fields = ('words_text','data_text','owner')
