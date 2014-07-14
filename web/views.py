from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from motion9.const import *
from common_controller.util import helper_get_user, helper_get_product_detail, helper_get_set, helper_make_paging_data, \
    http_response_by_json, helper_get_products, helper_get_set_list, helper_get_blog_reviews, \
    helper_get_custom_set, helper_get_custom_set_list, helper_get_brands
from .models import Product, Category, BlogReview, Set, Brand
from users.models import CustomSet, CustomSetDetail

import math
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def test_view(request):
    return render(request, 'uservoice_test.html')

@csrf_exempt
def index_view(request):
    product_categories = Category.objects.filter(is_set=False).all()
    set_categories = Category.objects.filter(is_set=True).all()

    return render(request, 'index_web.html',
                  {
                      'product_categories': product_categories,
                      'set_categories': set_categories,
                  })

@csrf_exempt
def shop_product_view(request, category_id=None, page_num=1):

    page_num = int(page_num)
    price_max_filter = request.GET.get('price_max', None)
    price_min_filter = request.GET.get('price_min', None)
    brandname_filter = request.GET.get('brandname', None)
    products_ = helper_get_products(helper_get_user(request), category_id, price_max_filter, price_min_filter, brandname_filter)

    if page_num is not None:
        products_ = helper_make_paging_data(len(products_), products_[(page_num-1)*ITEM_COUNT_PER_PAGE_FOR_PRODUCT:page_num*ITEM_COUNT_PER_PAGE_FOR_PRODUCT], ITEM_COUNT_PER_PAGE_FOR_PRODUCT, page_num)
    else:
        products_ = {'data': products_}

    # return http_response_by_json(None, products_ )

    categories = Category.objects.filter(is_set=False).all()

    if category_id is None:
        current_category = 'all'
    else:
        current_category = Category.objects.get(id=category_id).name

    brands = helper_get_brands()

    return render(request, 'shopping_product_web.html',
                  {

                      'products': products_,
                      'current_category': current_category,
                      'categories': categories,
                      'current_page': 'shop_product',
                      'current_brand': brandname_filter,
                      'brands': brands
                  })


def shop_set_view(request, category_id=None, page_num=1):

    page_num = int(page_num)
    price_max_filter = request.GET.get('price_max', None)
    price_min_filter = request.GET.get('price_min', None)
    sets = helper_get_set_list(category_id, helper_get_user(request), price_max_filter, price_min_filter)

    if page_num is not None:
        sets = helper_make_paging_data(len(sets), sets[(page_num-1)*ITEM_COUNT_PER_PAGE_FOR_SET:page_num*ITEM_COUNT_PER_PAGE_FOR_SET], ITEM_COUNT_PER_PAGE_FOR_SET, page_num)
    else:
        sets = {'data': sets}

    categories = Category.objects.filter(is_set=True).all()
    if category_id is None:
        current_category = 'all'
    else:
        current_category = Category.objects.get(id=category_id).name

    brands = helper_get_brands()

    return render(request, 'shopping_set_web.html',
                  {
                      'sets': sets,
                      'current_category': current_category,
                      'current_category_id': category_id,
                      'categories': categories,
                      'current_page': 'shop_set',
                      'brands': brands
                  })

@csrf_exempt
def set_view(request, set_id):
    set = helper_get_set(set_id, helper_get_user(request))

    return render(request, 'set_detail_web.html',
                {
                    'set': set
                })

@csrf_exempt
def product_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))
        blog_reivews = helper_get_blog_reviews(product_id)

        return render(request, "product_detail_web.html",
                      {
                          'product': product,
                          'blog_reviews': blog_reivews
                      })
    else:
        return render(request, "404.html")

@csrf_exempt
def product_modal_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))
        blog_reivews = helper_get_blog_reviews(product_id)

        return render(request, "product_detail_for_modal.html",
                      {
                          'product': product,
                          'blog_reviews': blog_reivews
                      })
    else:
        return render(request, "404.html")

@csrf_exempt
def product_json_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))
        return http_response_by_json(None, product)
    else:
        return render(request, "404.html")

@csrf_exempt
def customize_set_make_view(request, set_id):
    set = helper_get_set(set_id, helper_get_user(request), True)

    return render(request, "change_product_in_set_web.html",
          {
              'set': set
          })

@csrf_exempt
def customize_set_view(request):
    if helper_get_user(request) is None:
        return redirect('login_page')

    custom_sets = helper_get_custom_set_list(helper_get_user(request))

    return render(request, "shopping_custom_web.html",
          {
              'custom_sets': custom_sets
          })

    # set =

@csrf_exempt
def customize_set_detail_view(request, set_id):
    custom_set = helper_get_custom_set(set_id, helper_get_user(request))

    return render(request, "custom_detail_web.html",
          {
              'custom_set': custom_set
          })

@csrf_exempt
def customize_set_save_view(request):
    user = helper_get_user(request)
    data = request.POST.get('data', None)
    post_json = json.loads(data)
    set_id = post_json.get('set_id')
    custom_list = post_json.get('custom_lists')

    if set_id is None:
        return HttpResponse('is error')

    if user is not None:
        custom_set, is_created = CustomSet.objects.get_or_create(user=user, set__id = set_id)
        for custom_item in custom_list:
            original_id = custom_item.get('original_id')
            new_id = custom_item.get('new_id')
            CustomSetDetail.objects.create(custom_set=custom_set, original_product_id=original_id, new_product_id=new_id)
        return http_response_by_json()
    else:
        return http_response_by_json(CODE_LOGIN_REQUIRED)


# render example
# return render_to_response('shopping_product_web.html',
#               {
#                   'products': products_,
#                   'current_category': current_category,
#                   'categories': categories,
#                   'current_page': 'shop_product'
#               }, RequestContext(request))