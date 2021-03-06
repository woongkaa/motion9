/**
 * Created by Park-Kunbae on 14. 4. 3.
 */



$(function(){

    $.fn.scrollView = function () {
        return this.each(function () {
        $('html, body').animate({
              scrollTop: $(this).offset().top-100
            }, 500);
        });
    };


    $('.product-info-btn').click(function(e){
        e.preventDefault();

        var productKey =$(this).attr('data-product');
        var productImg = $('#productModalImg');
        var productName = $('#productModalName');
        var productPrice = $('#productModalPrice');
        var cartBtn = $('#productModalCartBtn');
        var interestBtn = $('#productModalInterestBtn');

         $.ajax({
				  url: '/product/json/'+productKey,
				  dataType: 'json',
				  async : true,
				  type:'POST',
				  success: function(data){
                      var product = data.data;
					  if(product != null){
                          productImg.attr('src', product.big_img_url);
                          productName.text(product.name);
                          productPrice.text(product.discount_price);
                          cartBtn.attr('data-product', product.key);
                          interestBtn.attr('data-product', product.key);

                          $('#product-detail-modal').modal('show');
                      }else{
                          alert('에러가 발생하였습니다. 관리자에게 문의 해주세요.');
                      }
				  },
				  error:function(jqXHR, textStatus, errorThrown){
					  alert('에러가 발생하였습니다. 관리자에게 문의 해주세요.');
				  }
		});


    });

/*
    $('.product-x-img-gallery').magnificPopup({
		delegate: 'a',
		type: 'image',
		tLoading: 'Loading image #%curr%...',
		mainClass: 'mfp-img-mobile',
		gallery: {
			enabled: true,
			navigateByImgClick: true,
			preload: [0,1] // Will preload 0 - before current, and 1 after the current image
		},
		image: {
			tError: '<a href="%url%">The image #%curr%</a> could not be loaded.'
		}
	});
*/



    $('.cnt-spinner').spinner({value:1, min : 1, afterChange: function(val){
        var price = parsePrice($('#productPrice').text());
        var final = price * parseInt(val);
        $('#productFinalPrice').text(numberFormatter(final));
    }});

    $("#product-xTabs").easyResponsiveTabs({
        type: 'default', //Types: default, vertical, accordion
        width: 'auto', //auto or any custom width
        fit: true,   // 100% fits in a container
        activate: function() {}  // Callback function, gets called if tab is switched
    });

    $('.btn-magazine-fold').click(function(e) {
        e.preventDefault();

        var magazine_fold = $('.magazine-fold');
        if ( magazine_fold.css('display') == 'none' ) {
            magazine_fold.css('display',"block");
            magazine_fold.scrollView();
            $(this).text('닫기');
        } else {
            magazine_fold.css('display',"none");
            $(this).text('더보기');
            $(".magazine-wrapper").scrollView();
        }
        $(this).scroll();
    });
});