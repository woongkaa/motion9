from web.models import Product, Set
from django.core.exceptions import ObjectDoesNotExist

from motion9.const import *
import logging
import math

logger = logging.getLogger(__name__)

def helper_get_user(request):
    if request.user and request.user.is_authenticated():
        return request.user
    else:
        return None

def helper_get_product(product_id_or_object, user=None):

    if isinstance(product_id_or_object, unicode) or isinstance(product_id_or_object, int):
        product_id = product_id_or_object
        product_object = None
    elif isinstance(product_id_or_object, Product):
        product_object = product_id_or_object

    try:
        if product_object is None:
            product = Product.objects.get(id=product_id)
        else:
            product = product_object

        product_ = {
            'id': product.id,
            'name': product.name,
            'category_name': product.category.name,
            'description': product.description,
            'big_img_url': product.big_img_url,
            'small_img_url': product.small_img_url,
            'video_url': product.description,
            'brandname': product.brandname,
            'maker': product.maker,
            'capacity': product.capacity,
            'original_price': product.original_price,
            'discount_price': product.discount_price,
            'fit_skin_type': product.fit_skin_type,
            'color_description': product.color_description,
            'color_rgb': product.color_rgb,
            'is_interested': True if user is not None and product.interest_set.filter(user=user).count()>0 else False
        }

        return product_

    except ObjectDoesNotExist as e:
        logger.error(e)

def helper_get_set(set_id_or_object, user=None):

    print set_id_or_object

    if isinstance(set_id_or_object, unicode) or isinstance(set_id_or_object, int):
        set_id = set_id_or_object
        set_object = None
    elif isinstance(set_id_or_object, Set):
        set_object = set_id_or_object

    if set_object is None:
        set = Set.objects.get(id=set_id)
    else:
        set = set_object

    set_ = {}
    set_.update({
        'id': set.id,
        'name': set.name,
        'category_name': set.category.name,
        'description': set.description,
        'big_img_url': set.big_img_url,
        'small_img_url': set.small_img_url,
        'discount_difference': set.discount_difference,
        'products': []
    })

    set_products = set.setproduct_set.all()
    original_price = 0
    discount_price = 0
    for set_product in set_products:
        product = set_product.product

        original_price += product.original_price
        discount_price += product.discount_price

        product_ = helper_get_product( product.id, user)
        set_['products'].append(product_)

    set_.update({
        'original_price': original_price,
        'discount_price': discount_price
    })

    return set_

def helper_make_paging_data( all_object_length, lists, page_num):
    pager_total_length = math.ceil( all_object_length/float(ITEM_COUNT_PER_PAGE))
    lists = {
        'data': lists,
        'page_total_count': pager_total_length,
        'page_left_count': page_num-(page_num%PAGER_INDICATOR_LENGTH)+1,
        'page_right_count': pager_total_length
        if pager_total_length < page_num-(page_num%PAGER_INDICATOR_LENGTH)+PAGER_INDICATOR_LENGTH
        else page_num-(page_num%PAGER_INDICATOR_LENGTH)+PAGER_INDICATOR_LENGTH,
    }
    lists.update({
        'page_hasPrev': True if lists['page_left_count'] is not 1 else False,
        'page_hasNext': True if lists['page_right_count'] is not pager_total_length else False,
        'page_range': range(lists['page_left_count'], lists['page_right_count']+1)
    })
    return lists