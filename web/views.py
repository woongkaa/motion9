#!/usr/bin/env python
# -*- coding: utf-8 -*-
from braces.views._access import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http.request import RAISE_ERROR
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template import Context
from django.views.generic import View, TemplateView
from common.models import NCategory
from common_controller import util
from foradmin.models import MainImage, Advertisement, Preference
from motion9 import settings

from motion9.const import *
from common_controller.util import helper_get_user, helper_get_product_detail, helper_get_set, helper_make_paging_data, \
    http_response_by_json, helper_get_products, helper_get_set_list, helper_get_blog_reviews, \
    helper_get_custom_set, helper_get_custom_set_list, helper_get_brands, helper_get_product_magazines, \
    helper_add_custom_set_cart, helper_get_adarea_items, helper_get_faq_items, helper_get_survey_items, \
    helper_get_survey_list, helper_get_survey_result_item, helper_get_report_count
from .models import Product, Category, BlogReview, Set, Brand
from users.models import CustomSet, CustomSetDetail, Payment, Cart, Purchase, OrderTempInfo, BeforePayment, UserSurvey, \
    SurveyResult

from subprocess import call, Popen, PIPE
import urllib
import json
import logging
from web.models import Faq

logger = logging.getLogger(__name__)

# 여러가지 feasible test를 위해 만들어놓은 view이다.
@csrf_exempt
def test_view(request):
    http_user_agent = request.META.get('HTTP_USER_AGENT').lower()
    # print request.META.get('HTTP_REFERER')


    return HttpResponse('success!')
    # return render(request, 'payment_complete_web.html')
    # return render(request, 'uservoice_test.html')


# payment창으로 넘어가기 전 페이지 이다. 여러가지 정보들을 지정하고 결제창을 호출하는데 넘겨준다.
# 여러가지 정보에는 이름 폰번호 우편번호 주소 등이 있다.
@csrf_exempt
@login_required
def before_payment(request):
    print request.POST

    order_id = request.POST.get('order_id', '')

    name = request.POST.get('name', '')
    phone = request.POST.get('phone', '')
    postcode = request.POST.get('postcode', '')
    basic_address = request.POST.get('basic_address', '')
    detail_address = request.POST.get('detail_address', '')
    shipping_requirement = request.POST.get('shipping_requirement', '')
    mileage = request.POST.get('mileage', '')
    if len(mileage) == 0:
        mileage = 0

    try:
        BeforePayment.objects.create(
            user=request.user,
            order_id=order_id,
            name=name,
            phone=phone,
            postcode=postcode,
            address=basic_address + ' ' + detail_address,
            shipping_requirement=shipping_requirement,
            mileage=mileage
        )
        return http_response_by_json()

    except Exception as e:
        return http_response_by_json(CODE_PARAMS_WRONG)


# payment를 끝내고 return되는 view이다. 결제모듈쪽에서 이곳으로 redirect하는 http response를 보내준다.
# 그렇기 때문에 before payment에서 이 view를 호출하는 url을 넘겨 주어야 한다.
@csrf_exempt
def payment_return_view(request):
    service_id = request.POST.get('SERVICE_ID')
    order_id = request.POST.get('ORDER_ID')
    order_date = request.POST.get('ORDER_DATE')
    post_response_code = request.POST.get('RESPONSE_CODE')
    check_sum = request.POST.get('CHECK_SUM')
    http_user_agent = request.META.get('HTTP_USER_AGENT').lower()
    if http_user_agent.find('firefox') == -1 and http_user_agent.find('chrome') == -1 and \
                    http_user_agent.find('safari') == -1 and http_user_agent.find('opera') == -1:
        message = request.POST.get('MESSAGE')
    else:
        message = urllib.unquote_plus(request.POST.get('MESSAGE'))

    is_success = False

    if post_response_code == "0000":
        temp = service_id + order_id + order_date
        checksum_command = 'java -cp ./libs/jars/billgateAPI.jar com.galaxia.api.util.ChecksumUtil ' + 'DIFF ' + check_sum + " " + temp
        checksum = (Popen(checksum_command.split(' '), stdout=PIPE).communicate()[0]).strip()
        if checksum == 'SUC':
            credit_card_service_code = '0900'
            broker_message_command = ["java", "-Dfile.encoding=euc-kr", "-cp", "./libs/jars/billgateAPI.jar",
                                      "com.galaxia.api.EncryptServiceBroker", "./libs/config/config.ini",
                                      credit_card_service_code, message]
            return_message = (Popen(broker_message_command, stdout=PIPE).communicate()[0]).strip()
            return_code = return_message[0:5]

            this_data = {}
            if return_code == 'ERROR':
                this_version = "0100"
                this_merchantId = service_id
                this_serviceCode = credit_card_service_code
                this_command = "3011"
                this_orderId = order_id
                this_orderDate = order_date

                util.billgate_put_data(this_data, "1002", return_message[6:10])
                util.billgate_put_data(this_data, "1003", "API error!!")
                util.billgate_put_data(this_data, "1009", return_message[10:12])
                util.billgate_put_data(this_data, "1010", util.billgate_getErrorMessage(return_message[6:12]))
            else:
                # {{ Message.php

                set_data_param = return_message
                VERSION_LENGTH = 10
                MERCHANT_ID_LENGTH = 20
                SERVICE_CODE_LENGTH = 4
                COMMAND_LENGTH = 4
                ORDER_ID_LENGTH = 64
                DATE_LENGTH = 14
                TAG_LENGTH = 4
                COUNT_LENGTH = 4
                VALUE_LENGTH = 4

                VERSION_INDEX = 0
                MERCHANT_ID_INDEX = 10
                SERVICE_CODE_INDEX = 30

                COMMAND_INDEX = 0
                ORDER_ID_INDEX = 4
                ORDER_DATE_INDEX = 68
                DATA_INDEX = 82

                this_version = set_data_param[VERSION_INDEX:VERSION_INDEX + VERSION_LENGTH].strip()
                this_merchantId = set_data_param[MERCHANT_ID_INDEX:MERCHANT_ID_INDEX + MERCHANT_ID_LENGTH].strip()
                this_serviceCode = set_data_param[SERVICE_CODE_INDEX:SERVICE_CODE_INDEX + SERVICE_CODE_LENGTH].strip()

                decrypted = set_data_param[
                            VERSION_LENGTH + MERCHANT_ID_LENGTH + SERVICE_CODE_LENGTH:VERSION_LENGTH + MERCHANT_ID_LENGTH + SERVICE_CODE_LENGTH + len(
                                set_data_param)]

                this_command = decrypted[COMMAND_INDEX:COMMAND_INDEX + COMMAND_LENGTH].strip()
                this_orderId = decrypted[ORDER_ID_INDEX:ORDER_ID_INDEX + ORDER_ID_LENGTH].strip()
                this_orderDate = decrypted[ORDER_DATE_INDEX:ORDER_DATE_INDEX + DATE_LENGTH].strip()

                bodyStr = decrypted[DATA_INDEX:DATA_INDEX + len(decrypted)].strip()
                # this->parseData($bodyStr);
                parse_data_param = bodyStr
                arrData = parse_data_param.split("|")
                for i in range(len(arrData)):
                    if len(arrData[i]) != 0:
                        arrValueData = arrData[i].split("=")
                        tag = arrValueData[0]
                        value = arrValueData[1]

                        if this_data.has_key(tag):
                            vt = this_data.get(tag)
                        else:
                            vt = []

                        vt.append(value)
                        this_data[tag] = vt
                        # Message.php }}

            response_code = this_data.get('1002')[0]
            response_message = this_data.get('1003')

            detail_response_code = this_data.get('1009')
            detail_response_message = this_data.get('1010')

            if response_code == '0000':
                auth_amount = this_data.get('1007')
                transaction_id = this_data.get('1001')
                auth_date = this_data.get('1005')

                is_success = True

    try:
        response_message = map(lambda x: x.decode('euc-kr'), response_message)
        detail_response_message = map(lambda x: x.decode('euc-kr'), detail_response_message)
    except:
        pass

    if is_success:
        beforePayment = BeforePayment.objects.get(order_id=order_id)
        if beforePayment is None:
            raise Http404

        user_ = beforePayment.user
        user_profile = user_.profile

        payment = Payment.objects.create(
            user=user_,
            service_id=service_id,
            order_id=beforePayment.order_id,
            order_date=order_date,
            transaction_id=transaction_id[0],
            auth_amount=auth_amount[0],
            auth_date=auth_date[0],
            response_code=response_code,
            response_message=response_message[0],
            detail_response_code=detail_response_code[0],
            detail_response_message=detail_response_message[0],
            name=beforePayment.name,
            postcode=beforePayment.postcode,
            phone=beforePayment.phone,
            address=beforePayment.address,
            shipping_requirement=beforePayment.shipping_requirement,
            mileage=beforePayment.mileage
        )

        user_profile.mileage = int(user_profile.mileage) - int(beforePayment.mileage) + int(auth_amount[0]) / 100
        user_profile.save()

        carts = Cart.objects.filter(order_id=order_id).all()
        for cart in carts:

            if cart.type == 'p':
                price = cart.product.discount_price
            elif cart.type == 's':
                price = helper_get_set(cart.set).get('discount_price', 0)
            elif cart.type == 'c':
                price = helper_get_custom_set(cart.custom_set).get('discount_price', 0)

            Purchase.objects.create(
                user=user_,
                payment=payment,
                price=price,
                product=cart.product,
                set=cart.set,
                custom_set=cart.custom_set,
                type=cart.type,
                item_count=cart.item_count
            )

        if payment is not None:
            payment_id = payment.id

        Cart.objects.filter(order_id=order_id).delete()

    if http_user_agent.find('firefox') == -1 and http_user_agent.find('chrome') == -1 and \
                    http_user_agent.find('safari') == -1 and http_user_agent.find('opera') == -1:
        return render(request, 'return_explorer.html', {
            'payment_id': payment_id,
            'message': message,
            'return_message': return_message,
            'is_success': is_success,
            'service_id': service_id,
            'order_id': order_id,
            'order_date': order_date,
            'transaction_id': transaction_id,
            'auth_amount': auth_amount,
            'auth_date': auth_date,
            'response_code': response_code,
            'response_message': response_message,
            'detail_response_code': detail_response_code,
            'detail_response_message': detail_response_message
        })
    else:
        if is_success:
            return redirect('payment_complete', payment_id=payment_id)
        else:
            raise Http404


# 위의 view와 같은데
# mobile이냐 web이냐에 따라 넘어오는 params가 조금 달라 따로 만들었다.
@csrf_exempt
def payment_return_mobile_web_view(request):
    transaction_id = None
    auth_amount = None
    auth_date = None
    response_code = None
    response_message = None
    detail_response_code = None
    detail_response_message = None

    service_id = request.POST.get('SERVICE_ID')
    order_id = request.POST.get('ORDER_ID')
    order_date = request.POST.get('ORDER_DATE')
    post_response_code = request.POST.get('RESPONSE_CODE')
    check_sum = request.POST.get('CHECK_SUM')
    message = request.POST.get('MESSAGE')

    is_success = False

    if post_response_code == "0000":
        credit_card_service_code = '0900'
        broker_message_command = ["java", "-Dfile.encoding=euc-kr", "-cp", "./libs/jars/billgateAPI.jar",
                                  "com.galaxia.api.EncryptServiceBroker", "./libs/config/config.ini",
                                  credit_card_service_code, message]
        return_message = Popen(broker_message_command, stdout=PIPE).communicate()[0].strip()
        return_code = return_message[0:5]

        this_data = {}
        if return_code == 'ERROR':
            this_version = "0100"
            this_merchantId = service_id
            this_serviceCode = credit_card_service_code
            this_command = "3011"
            this_orderId = order_id
            this_orderDate = order_date

            util.billgate_put_data(this_data, "1002", return_message[6:10])
            util.billgate_put_data(this_data, "1003", "API error!!")
            util.billgate_put_data(this_data, "1009", return_message[10:12])
            util.billgate_put_data(this_data, "1010", util.billgate_getErrorMessage(return_message[6:12]))
        else:
            # {{ Message.php

            set_data_param = return_message
            VERSION_LENGTH = 10
            MERCHANT_ID_LENGTH = 20
            SERVICE_CODE_LENGTH = 4
            COMMAND_LENGTH = 4
            ORDER_ID_LENGTH = 64
            DATE_LENGTH = 14
            TAG_LENGTH = 4
            COUNT_LENGTH = 4
            VALUE_LENGTH = 4

            VERSION_INDEX = 0
            MERCHANT_ID_INDEX = 10
            SERVICE_CODE_INDEX = 30

            COMMAND_INDEX = 0
            ORDER_ID_INDEX = 4
            ORDER_DATE_INDEX = 68
            DATA_INDEX = 82

            this_version = set_data_param[VERSION_INDEX:VERSION_INDEX + VERSION_LENGTH].strip()
            this_merchantId = set_data_param[MERCHANT_ID_INDEX:MERCHANT_ID_INDEX + MERCHANT_ID_LENGTH].strip()
            this_serviceCode = set_data_param[SERVICE_CODE_INDEX:SERVICE_CODE_INDEX + SERVICE_CODE_LENGTH].strip()

            decrypted = set_data_param[
                        VERSION_LENGTH + MERCHANT_ID_LENGTH + SERVICE_CODE_LENGTH:VERSION_LENGTH + MERCHANT_ID_LENGTH + SERVICE_CODE_LENGTH + len(
                            set_data_param)]

            this_command = decrypted[COMMAND_INDEX:COMMAND_INDEX + COMMAND_LENGTH].strip()
            this_orderId = decrypted[ORDER_ID_INDEX:ORDER_ID_INDEX + ORDER_ID_LENGTH].strip()
            this_orderDate = decrypted[ORDER_DATE_INDEX:ORDER_DATE_INDEX + DATE_LENGTH].strip()

            bodyStr = decrypted[DATA_INDEX:DATA_INDEX + len(decrypted)].strip()
            # this->parseData($bodyStr);
            parse_data_param = bodyStr
            arrData = parse_data_param.split("|")
            for i in range(len(arrData)):
                if len(arrData[i]) != 0:
                    arrValueData = arrData[i].split("=")
                    tag = arrValueData[0]
                    value = arrValueData[1]

                    if this_data.has_key(tag):
                        vt = this_data.get(tag)
                    else:
                        vt = []

                    vt.append(value)
                    this_data[tag] = vt
                    # Message.php }}

        response_code = this_data.get('1002')[0]
        response_message = this_data.get('1003')

        detail_response_code = this_data.get('1009')
        detail_response_message = this_data.get('1010')

        if response_code == '0000':
            auth_amount = this_data.get('1007')
            transaction_id = this_data.get('1001')
            auth_date = this_data.get('1005')

            is_success = True

    try:
        response_message = map(lambda x: x.decode('euc-kr'), response_message)
        detail_response_message = map(lambda x: x.decode('euc-kr'), detail_response_message)
    except:
        pass

    # payment_id=0

    if is_success:
        beforePayment = BeforePayment.objects.get(order_id=order_id)
        if beforePayment is None:
            raise Http404

        user_ = beforePayment.user
        user_profile = user_.profile

        payment = Payment.objects.create(
            user=user_,
            service_id=service_id,
            order_id=beforePayment.order_id,
            order_date=order_date,
            transaction_id=transaction_id[0],
            auth_amount=auth_amount[0],
            auth_date=auth_date[0],
            response_code=response_code,
            response_message=response_message[0],
            detail_response_code=detail_response_code[0],
            detail_response_message=detail_response_message[0],
            name=beforePayment.name,
            postcode=beforePayment.postcode,
            phone=beforePayment.phone,
            address=beforePayment.address,
            shipping_requirement=beforePayment.shipping_requirement,
            mileage=beforePayment.mileage
        )

        user_profile.mileage = int(user_profile.mileage) - int(beforePayment.mileage) + int(auth_amount[0]) / 100
        user_profile.save()

        carts = Cart.objects.filter(order_id=order_id).all()
        for cart in carts:

            if cart.type == 'p':
                price = cart.product.discount_price
            elif cart.type == 's':
                price = helper_get_set(cart.set).get('discount_price', 0)
            elif cart.type == 'c':
                price = helper_get_custom_set(cart.custom_set).get('discount_price', 0)

            Purchase.objects.create(
                user=user_,
                payment=payment,
                price=price,
                product=cart.product,
                set=cart.set,
                custom_set=cart.custom_set,
                type=cart.type,
                item_count=cart.item_count
            )

        if payment is not None:
            payment_id = payment.id

        Cart.objects.filter(order_id=order_id).delete()

    if is_success:
        return redirect('mobile_payment_complete', payment_id=payment_id)
    else:
        return redirect('mobile_mypage_before_purchase')

        # return render(request, 'return_explorer.html', {
        # 'payment_id': payment_id,
        #     'message': message,
        #     'return_message': return_message,
        #     'is_success': is_success,
        #     'service_id': service_id,
        #     'order_id': order_id,
        #     'order_date': order_date,
        #     'transaction_id': transaction_id,
        #     'auth_amount': auth_amount,
        #     'auth_date': auth_date,
        #     'response_code': response_code,
        #     'response_message': response_message,
        #     'detail_response_code': detail_response_code,
        #     'detail_response_message': detail_response_message
        # })


# payment가 완료되었다는것을 보여주는 view이다.
# 예로 결제가 완료되었습니다. 라는 문구가 사용자에게 뜨는 페이지를 생각하면 된다.
@csrf_exempt
@login_required
def payment_complete_view(request, payment_id=0):
    payment = Payment.objects.get(id=payment_id)

    purchase_products = Purchase.objects.filter(payment_id=payment_id, type='p').all()
    products = []
    for purchase_set in purchase_products:
        product = purchase_set.product
        product_ = helper_get_product_detail(product, request.user)
        product_['item_count'] = purchase_set.item_count
        product_['total_price'] = purchase_set.price
        products.append(product_)

    purchase_sets = Purchase.objects.filter(payment_id=payment_id, type='s').all()
    sets = []
    for purchase_set in purchase_sets:
        set = purchase_set.set
        set_ = helper_get_set(set, request.user)
        set_['item_count'] = purchase_set.item_count
        set_['total_price'] = purchase_set.price
        sets.append(set_)

    purchase_custom_sets = Purchase.objects.filter(payment_id=payment_id, type='c').all()
    custom_sets = []
    for purchase_custom_set in purchase_custom_sets:
        custom_set = purchase_custom_set.custom_set
        custom_set_ = helper_get_custom_set(custom_set, request.user)
        custom_set_['item_count'] = purchase_custom_set.item_count
        custom_set_['total_price'] = purchase_custom_set.price
        custom_sets.append(custom_set_)

    if BeforePayment.objects.filter(order_id=payment.order_id).exists():
        util.send_payment_email(payment_id, request.user)
        BeforePayment.objects.filter(order_id=payment.order_id).delete()

    return render(request, 'payment_complete_web.html', {
        'products': products,
        'sets': sets,
        'custom_sets': custom_sets,
        'payment': payment,
        'user_': request.user
    })


# web용 index page이다.
@csrf_exempt
def index_view(request):
    if request.is_mobile:
        return redirect('mobile:mobile_index')

    product_categories = Category.objects.filter(is_set=False).all()
    set_categories = Category.objects.filter(is_set=True).all()

    set_category_images_row = []
    try:
        set_categorys = Category.objects.filter(is_set=True).all()

        set_category_images = []
        for set_category in set_categorys:
            set_category_images.append({
                'id': set_category.id,
                'image_url': settings.MEDIA_URL + set_category.small_image.name
            })
            if len(set_category_images) == 3:
                set_category_images_row.append(set_category_images)
                set_category_images = []

        if len(set_category_images) != 0:
            set_category_images_row.append(set_category_images)
    except:
        pass

    survey_status = {
        'survey_request_count': UserSurvey.objects.count() + 550,
        'survey_response_count': SurveyResult.objects.count() + 460
    }

    return render(request, 'index_web.html',
                  {
                      'product_categories': product_categories,
                      'set_categories': set_categories,
                      'survey_status': survey_status
                  })


# web용 shop view 이다.
# shop view는 product용과 set용 2개로 나뉘어 지는데 그 중 product용 이다.
@csrf_exempt
def shop_product_view(request, category_id=None, page_num=1):
    page_num = int(page_num)
    price_max_filter = request.GET.get('price_max', None)
    price_min_filter = request.GET.get('price_min', None)
    brandname_filter = request.GET.get('brandname', None)
    products_ = helper_get_products(helper_get_user(request), category_id, price_max_filter, price_min_filter,
                                    brandname_filter)

    if page_num is not None:
        products_ = helper_make_paging_data(len(products_), products_[(
                                                                      page_num - 1) * ITEM_COUNT_PER_PAGE_FOR_PRODUCT:page_num * ITEM_COUNT_PER_PAGE_FOR_PRODUCT],
                                            ITEM_COUNT_PER_PAGE_FOR_PRODUCT, page_num)
    else:
        products_ = {'data': products_}

    # return http_response_by_json(None, products_ )

    categories = Category.objects.filter(is_set=False).all()

    if category_id is None:
        current_category = 'all'
    else:
        current_category = Category.objects.get(id=category_id).name

    brands = helper_get_brands()
    adarea_items = helper_get_adarea_items(request)

    return render(request, 'shopping_product_web.html',
                  {
                      'products': products_,
                      'current_category': current_category,
                      'current_category_id': category_id,
                      'categories': categories,
                      'current_page': 'shop_product',
                      'current_brand': brandname_filter,
                      'brands': brands,
                      'adarea_items': adarea_items
                  })


# web용 shop view 이다.
# shop view는 product용과 set용 2개로 나뉘어 지는데 그 중 set용 이다.
def shop_set_view(request, category_id=None, page_num=1):
    page_num = int(page_num)
    price_max_filter = request.GET.get('price_max', None)
    price_min_filter = request.GET.get('price_min', None)
    sets = helper_get_set_list(category_id, helper_get_user(request), price_max_filter, price_min_filter)

    if page_num is not None:
        sets = helper_make_paging_data(len(sets), sets[(
                                                       page_num - 1) * ITEM_COUNT_PER_PAGE_FOR_SET:page_num * ITEM_COUNT_PER_PAGE_FOR_SET],
                                       ITEM_COUNT_PER_PAGE_FOR_SET, page_num)
    else:
        sets = {'data': sets}

    categories = Category.objects.filter(is_set=True).all()
    if category_id is None:
        current_category = 'all'
    else:
        current_category = Category.objects.get(id=category_id).name

    brands = helper_get_brands()
    adarea_items = helper_get_adarea_items(request)

    # print sets['data'][0].keys()
    # print sets['data'][0]['products']
    # print sets['data'][0]['products'][0]['name']

    return render(request, 'shopping_set_web.html',
                  {
                      'sets': sets,
                      'current_category': current_category,
                      'current_category_id': category_id,
                      'categories': categories,
                      'current_page': 'shop_set',
                      'brands': brands,
                      'adarea_items': adarea_items
                  })


# web용 set view 이다.
# 넘어온 set_id에 대한 set의 상세 정보를 보여준다.
@csrf_exempt
def set_view(request, set_id):
    set = helper_get_set(set_id, helper_get_user(request))

    return render(request, 'set_detail_web.html',
                  {
                      'set': set
                  })


# web용 product view 이다.
# 넘어온 product_id에 대한 product의 상세 정보를 보여준다.
@csrf_exempt
def product_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))

        product['category_guide_image'] = MainImage.objects.filter(name=product['category_name']).first()
        if product['category_guide_image'] is not None:
            product['category_guide_image'] = settings.MEDIA_URL + product['category_guide_image'].image.name

        blog_reivews = helper_get_blog_reviews(product_id)
        magazines = helper_get_product_magazines(product_id)
        magazines_fold = magazines[4:]
        magazines = magazines[:4]

        return render(request, "product_detail_web.html",
                      {
                          'product': product,
                          'magazines': magazines,
                          'magazines_fold': magazines_fold,
                          'blog_reviews': blog_reivews
                      })
    else:
        return render(request, "404.html")


# web용 product view for modal 이다.
# 넘어온 product_id에 대한 product의 상세 정보를 보여주는데 modal을 띄워서 보여준다.
# modal은 dialog라고 생각하면 된다.
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


# web용 product api이다.
# product_id에 대한 상세 정보를 보여주는데, 상세 정보를 보여주는 page를 만들어서 돌려주는거이 아니라
# 상세 정보만은 json으로 보내준다.
@csrf_exempt
def product_json_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))
        return http_response_by_json(None, product)
    else:
        return render(request, "404.html")


# web용 set custom을 하기위한(make) view
# set_id에 대한 set의 상세 product들을 custom하는 page를 돌려준다.
@csrf_exempt
def customize_set_make_view(request, set_id):
    set = helper_get_set(set_id, helper_get_user(request), True)

    return render(request, "change_product_in_set_web.html",
                  {
                      'set': set
                  })


# web용 custom set view
# custom된 set들을 모아서 보여준다.
@csrf_exempt
def customize_set_view(request):
    if helper_get_user(request) is None:
        return redirect('login_page')

    custom_sets = helper_get_custom_set_list(helper_get_user(request))
    adarea_items = helper_get_adarea_items(request)

    return render(request, "shopping_custom_web.html",
                  {
                      'custom_sets': custom_sets,
                      'adarea_items': adarea_items
                  })

    # set =


# web용 custom set detail view
# set_id에 대한 set의 custom된 set의 상세 정보를 보여준다.
@csrf_exempt
def customize_set_detail_view(request, set_id):
    custom_set = helper_get_custom_set(set_id, helper_get_user(request))

    return render(request, "custom_detail_web.html",
                  {
                      'custom_set': custom_set
                  })


# customize make view에서 customizing을 완료 한 후에
# save버튼을 눌러서 저장할 때 불리는 view 이다.
@csrf_exempt
def customize_set_save_view(request):
    user = helper_get_user(request)
    data = request.POST.get('data', None)
    will_added = request.POST.get('addToCart', False)

    post_json = json.loads(data)
    set_id = post_json.get('set_id')
    custom_list = post_json.get('custom_lists')

    if set_id is None:
        return HttpResponse('is error')

    if user is not None:
        custom_set, is_created = CustomSet.objects.get_or_create(user=user, set_id=set_id)
        if not (is_created):
            Cart.objects.filter(custom_set=custom_set).delete()

        for custom_item in custom_list:
            original_id = custom_item.get('original_id')
            new_id = custom_item.get('new_id')
            if CustomSetDetail.objects.filter(custom_set=custom_set, original_product_id=original_id).exists():
                CustomSetDetail.objects.filter(custom_set=custom_set, original_product_id=original_id).update(
                    new_product=new_id)
            else:
                CustomSetDetail.objects.create(custom_set=custom_set, original_product_id=original_id,
                                               new_product_id=new_id)

        if will_added:
            helper_add_custom_set_cart(user, custom_set.id)
        return http_response_by_json()
    else:
        return http_response_by_json(CODE_LOGIN_REQUIRED)


# help faq view이다. 전형적인 자주 묻는 질문과 답변을 적어놓는 page이다.
@csrf_exempt
def help_faq_view(request):
    faqs = helper_get_faq_items(request)
    return render(request, 'help_faq.html', {
        'faqs': faqs
    })


# report view이다. 우리가 입력한 report를 사용자에게 보여준다.
# 예전에 만들고 한참동안 사용하지 않아 제대로 작동하지 않을지도 모른다.
@login_required
def report_view(request, category_id=None, page_num=1):
    user = helper_get_user(request)
    user_profile = user.profile
    page_num = int(page_num)
    price_max_filter = request.GET.get('price_max', None)
    price_min_filter = request.GET.get('price_min', None)
    brandname_filter = request.GET.get('brandname', None)
    products_ = helper_get_products(helper_get_user(request), category_id, price_max_filter, price_min_filter,
                                    brandname_filter)

    if page_num is not None:
        products_ = helper_make_paging_data(len(products_), products_[(
                                                                      page_num - 1) * ITEM_COUNT_PER_PAGE_FOR_PRODUCT:page_num * ITEM_COUNT_PER_PAGE_FOR_PRODUCT],
                                            ITEM_COUNT_PER_PAGE_FOR_PRODUCT, page_num)
    else:
        products_ = {'data': products_}

    # return http_response_by_json(None, products_ )

    categories = Category.objects.filter(is_set=False).all()

    if category_id is None:
        current_category = 'all'
    else:
        current_category = Category.objects.get(id=category_id).name

    brands = helper_get_brands()
    adarea_items = helper_get_adarea_items(request)
    phone = user_profile.phone
    phones = phone.split("-")
    phone1 = phone2 = phone3 = ''

    if user is not None:

        return render(request, 'report_web.html',
                      {
                          'products': products_,
                          'current_category': current_category,
                          'current_category_id': category_id,
                          'categories': categories,
                          'current_page': 'shop_product',
                          'current_brand': brandname_filter,
                          'brands': brands,
                          'adarea_items': adarea_items,
                          'tab_name': 'myinfo',
                          'next': next
                      })

    else:
        logger.error('have_to_login')


# report view이다. 해당하는 product_id에 대한하는 잡지 정보와 blog review를
# 한꺼번에 보여준다.
@login_required
def report_detail_view(request, product_id=None):
    if product_id is not None:
        product = helper_get_product_detail(product_id, helper_get_user(request))

        product['category_guide_image'] = MainImage.objects.filter(name=product['category_name']).first()
        if product['category_guide_image'] is not None:
            product['category_guide_image'] = settings.MEDIA_URL + product['category_guide_image'].image.name

        blog_reivews = helper_get_blog_reviews(product_id)
        magazines = helper_get_product_magazines(product_id)
        magazines_fold = magazines[4:]
        magazines = magazines[:4]

        return render(request, "report_detail_web.html",
                      {
                          'product': product,
                          'magazines': magazines,
                          'magazines_fold': magazines_fold,
                          'blog_reviews': blog_reivews
                      })
    else:
        return render(request, "404.html")


# 위의 report_detail_view와 똑같은데 modal로 뜬다는것만 다르다.
@login_required
def report_detail_modal_view(request, category_id=None, page_num=1, product_id=None):
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


# report를 시작하기 전 안내 페이지 이다.
@csrf_exempt
def report_form_index_view(request):
    return render(request, 'report_form_index_web.html',
                  {
                      'next': reverse('report_form'),
                  })


# report를 시작한 후의 페이지이다.
@login_required
def report_form_view(request):
    survey = helper_get_survey_items(request)

    survey_ = []
    survey_group = []
    survey_range = len(survey['survey_items']) + 1

    for i in range(len(survey['survey_items'])):
        survey['survey_items'][i].update({
            'label_index': str(i + 1)
        })
        survey_group.append(survey['survey_items'][i])
        if (i + 1) % 2 == 0:
            survey_.append(survey_group)
            survey_group = []

    if len(survey_group) != 0:
        survey_.append(survey_group)

    return render(request, 'report_form_web.html',
                  {
                      'next': reverse('report_form'),
                      'survey': survey_,
                      'survey_id': survey['survey_id'],
                      'survey_range': survey_range
                  })


@csrf_exempt
def survey_detail_view(request):
    return render(request, 'survey_detail_web.html',
                  {
                      'next': reverse('report_form'),
                  })


# 설문조사 내용을 json으로 return해 준다.
@login_required
def survey_list_in_json(request):
    survey_list = request.user.get_survey_list.all()
    survey_list_ = []
    for survey_item in survey_list:
        survey_item_ = {
            'id': survey_item.id,
            'created_display': survey_item.created_display,
            'is_analysis_finish': survey_item.is_analysis_finish
        }
        survey_list_.append(survey_item_)

    return http_response_by_json(None, {'data': survey_list_})


# survey에 대한 결과를 관리자가 입력한것을 보는 페이지이다.
@login_required
def survey_result_view(request, pk):
    survey_result_item = helper_get_survey_result_item(request, pk)
    return render(request, 'web/survey_result.html', {
        'survey_result_item': survey_result_item
    })


# survey에 대한 결과를 관리자가 입력한것을 보는 페이지이다. v2
class SurveyResultView(LoginRequiredMixin, TemplateView):
    template_name = "web/survey2_result.html"

    def dispatch(self, request, *args, **kwargs):
        if not (self.request.user.is_superuser) and self.request.user != UserSurvey.objects.get(pk=kwargs['pk']).user:
            return redirect('index')

        return super(SurveyResultView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SurveyResultView, self).get_context_data(**kwargs)
        print kwargs['pk']
        self.request.pk = kwargs['pk']
        user_survey = UserSurvey.objects.get(pk=kwargs['pk'])
        user_survey_result = user_survey.result
        survey_result_detail = user_survey_result.details.select_related('product')

        survey_result_detail_ = {}

        for item in survey_result_detail:
            if item.product.ninterest_set.filter(user_survey_id=self.request.pk).exists():
                item.product.is_interested = True

            item_ = {
                'product': item.product
            }
            if not (survey_result_detail_.has_key(item.product.category.name)):
                survey_result_detail_.update({item.product.category.name: []})

            survey_result_detail_[item.product.category.name].append(item_)

        context["user_survey"] = user_survey
        context["user_survey_result"] = user_survey_result
        context["survey_result_detail"] = survey_result_detail_

        graphs_min_data = {
            "category": "최소예산"
        }
        graphs_max_data = {
            "category": "최대예산"
        }

        graphs_data = []

        index = 1
        min_price_sum = 0
        max_price_sum = 0
        for key in survey_result_detail_:
            min_price = 1987654321
            max_price = 0
            for item in survey_result_detail_[key]:
                min_price = item['product'].price if min_price > item['product'].price else min_price
                max_price = item['product'].price if max_price < item['product'].price else max_price

            min_price_sum += min_price
            max_price_sum += max_price
            graphs_min_data.update({"column-" + str(index): min_price})
            graphs_max_data.update({"column-" + str(index): max_price})

            graphs_data.append({
                "balloonText": "[[title]] : [[value]] 원",
                "columnWidth": 0.5,
                "fillAlphas": 1,
                "id": "AmGraph-" + str(index),
                "title": survey_result_detail_[key][0]['product'].category.name_for_kor.encode('utf-8'),
                "type": "column",
                "valueField": "column-" + str(index)
            })

            index += 1

        context["min_price_sum"] = min_price_sum
        context["max_price_sum"] = max_price_sum
        context["graphs_data"] = graphs_data
        context["graphs_min_data"] = graphs_min_data
        context["graphs_max_data"] = graphs_max_data

        context["categories"] = NCategory.objects.all()

        return context


# survey에 대한 결과를 관리자가 입력한것을 보는 페이지인데, 그 중 상세 제품의 결과를 보는 페이지 이다.
class SurveyResultDetailView(LoginRequiredMixin, TemplateView):
    template_name = "web/survey2_result_detail.html"

    def dispatch(self, request, *args, **kwargs):
        if not (self.request.user.is_superuser) and self.request.user != UserSurvey.objects.get(pk=kwargs['pk']).user:
            return redirect('index')

        return super(SurveyResultDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.request.pk = kwargs['pk']
        context = super(SurveyResultDetailView, self).get_context_data(**kwargs)
        survey_result_detail = UserSurvey.objects.get(pk=kwargs['pk']).result.details.select_related(
            'product', ).filter(product__category__name=kwargs['product_type'])
        survey_result_detail_ = []
        for item in survey_result_detail:
            item.product.detail = item.product.productdetail if hasattr(item.product, 'productdetail') else None
            item.product.analysis_ = item.product.productanalysis
            item.product.analysis_.detail_skintype = item.product.productanalysis.details.filter(type='skintype')[:3]
            item.product.analysis_.detail_feature = item.product.productanalysis.details.filter(type='feature')[:3]
            item.product.analysis_.detail_effect = item.product.productanalysis.details.filter(type='effect')[:3]
            item.product.analysis_.detail_etc = item.product.productanalysis.details.filter(type='etc')[:3]
            if item.product.ninterest_set.filter(user_survey_id=self.request.pk).exists():
                item.product.is_interested = True

            survey_result_detail_.append({
                'product': item.product
            })

        context['survey_result_detail'] = survey_result_detail_
        return context


# 차트 테스트용
@login_required
def chart_view(request):
    return render(request, 'chart_test/charts_flotcharts.html')