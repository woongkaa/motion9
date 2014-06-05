from django.http.response import HttpResponse
from web.models import Product, Set, ChangeableProduct, ChangeableProductInfo
from users.models import Interest, Cart, Purchase
from django.core.exceptions import ObjectDoesNotExist

from motion9.const import ITEM_COUNT_PER_PAGE, PAGER_INDICATOR_LENGTH, ERROR_CODE_AND_MESSAGE_DICT
import logging
import math
import json

logger = logging.getLogger(__name__)

def http_response_by_json(error=None, json_={}):
    if error is None:
        json_.update({
            'success': True
        })
    else:
        json_.update({
            'success': False,
            'message': ERROR_CODE_AND_MESSAGE_DICT[error],
        })

    return HttpResponse(json.dumps(json_, ensure_ascii=False), content_type="application/json; charset=utf-8")

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

def helper_get_set(set_id_or_object, user=None, with_custom_info=False):

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

        if with_custom_info:
            try:
                changeable_product = ChangeableProduct.objects.get(set_id=set_id, product_id=product.id)
                changeable_product_infos = changeable_product.changeableproductinfo_set.all()

                changeable_products = []
                for changeable_product_info in changeable_product_infos:
                    product_ = helper_get_product(changeable_product_info.product, user)
                    changeable_products.append(product_)

                product_.update({
                    'is_changeable': True,
                    'changeable_products': changeable_products
                })

            except Exception as e:
                product_.update({
                    'is_changeable': False
                })

        set_['products'].append(product_)

    set_.update({
        'original_price': original_price,
        'discount_price': discount_price
    })

    return set_

# def helper_get_changeable_product_list(set_id):
#     changeable_products = ChangeableProduct.objects.filter(set_id=set_id)
#     for changeable_product in changeable_products:
#         changeableproductinfos = changeable_product.changeableproductinfo_set.all()
#         changeable_product.product_id -> changeableproductinfos items product_id

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

# interest

def helper_add_product_interest(user, product_id):
    try:
        Interest.objects.create(user=user, product_id=product_id, type='p')
    except Exception as e:
        logger.error(e)

def helper_add_set_interest(user, set_id):
    try:
        Interest.objects.create(user=user, set_id=set_id, type='s')
    except Exception as e:
        logger.error(e)

def helper_delete_product_interest(user, product_id):
    try:
        interest = Interest.objects.get(user=user, product_id=product_id, type='p')
        interest.delete()
    except Exception as e:
        logger.error(e)

def helper_delete_set_interest(user, set_id):
    try:
        interest = Interest.objects.get(user=user, set_id=set_id, type='s')
        interest.delete()
    except Exception as e:
        logger.error(e)

# cart

def helper_add_product_cart(user, product_id):
    try:
        Cart.objects.create(user=user, product_id=product_id, type='p')
    except Exception as e:
        logger.error(e)

def helper_add_set_cart(user, set_id):
    try:
        Cart.objects.create(user=user, set_id=set_id, type='s')
    except Exception as e:
        logger.error(e)

def helper_add_custom_set_cart(user, custom_set_id):
    try:
        Cart.objects.create(user=user, custom_set_id=custom_set_id, type='c')
    except Exception as e:
        logger.error(e)

def helper_delete_product_cart(user, product_id):
    try:
        cart = Cart.objects.get(user=user, product_id=product_id, type='p')
        cart.delete()
    except Exception as e:
        logger.error(e)

def helper_delete_set_cart(user, set_id):
    try:
        cart = Cart.objects.get(user=user, set_id=set_id, type='s')
        cart.delete()
    except Exception as e:
        logger.error(e)

def helper_delete_custom_set_cart(user, custom_set_id):
    try:
        cart = Cart.objects.get(user=user, custom_set_id=custom_set_id, type='c')
        cart.delete()
    except Exception as e:
        logger.error(e)

# purchase

def helper_add_product_purchase(user, address, product_id):
    try:
        Purchase.objects.create(user=user, address=address, product_id=product_id, type='p')
    except Exception as e:
        logger.error(e)

def helper_add_set_purchase(user, address, set_id):
    try:
        Purchase.objects.create(user=user, address=address, set_id=set_id, type='s')
    except Exception as e:
        logger.error(e)

def helper_add_custom_set_purchase(user, address, custom_set_id):
    try:
        Purchase.objects.create(user=user, address=address, custom_set_id=custom_set_id, type='c')
    except Exception as e:
        logger.error(e)

def helper_delete_product_purchase(user, address, product_id):
    try:
        purchase = Purchase.objects.get(user=user, product_id=product_id, type='p')
        purchase.delete()
    except Exception as e:
        logger.error(e)

def helper_delete_set_purchase(user, address, set_id):
    try:
        purchase = Purchase.objects.get(user=user, set_id=set_id, type='s')
        purchase.delete()
    except Exception as e:
        logger.error(e)

def helper_delete_custom_set_purchase(user, address, custom_set_id):
    try:
        purchase = Purchase.objects.get(user=user, custom_set_id=custom_set_id, type='c')
        purchase.delete()
    except Exception as e:
        logger.error(e)

