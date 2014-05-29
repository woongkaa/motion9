from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^shop/product/$', 'web.views.shop_product_view', name='shop_product'),
    url(r'^shop/product/(?P<category_id>(\d+))/$', 'web.views.shop_product_view', name='shop_product'),
    url(r'^shop/product/page/(?P<page_num>(\d+))/$', 'web.views.shop_product_view', name='shop_product'),
    url(r'^shop/product/(?P<category_id>(\d+))/(?P<page_num>(\d+))/$', 'web.views.shop_product_view', name='shop_product'),
)