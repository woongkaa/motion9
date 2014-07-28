/**
 * Created by Park-Kunbae on 14. 3. 31.
 */

$(function(){

    var fixDiv = function() {
        var b = $(window).scrollTop();
        var d = $("#header").offset().top + 80;
        var c = $("#nav-top-btn");
        if (b > d) {
            c.css({position:"fixed", top:"90%", display:"block"});
        } else {
            c.css({position:"absolute",top:"0px", display : 'none'});
        }
    };

    $(window).scroll(fixDiv);

    $('.login-box, .login-form').keypress(function(e){
        if(e.keyCode == 13){
            $(this).find('form').submit();
        }
    });


    $('.login-submit-btn').click(function(e){
        e.preventDefault();

        var isEnable = $(this).attr('data-enable');

        if(isEnable && isEnable == 'false'){
            alert('이메일을 확인하세요.');
        }else{
            var formType = $(this).attr('data-form');
            var form = $('form').filter(function(){
               return $(this).attr('data-form') == formType;
            });

            var formType = $(this).attr('data-form');
            var form = $('form').filter(function(){
               return $(this).attr('data-form') == formType;
            });

            form.submit();
        }


    });

    $('#loginBox').jqm({modal:false});
    $('.login-btn').click(function(e){
        e.preventDefault();
        $('#loginBox').jqmShow();


    });

    function loginCheck(email){
        $.ajax({
              url: "/user/logincheck/",
              dataType: 'json',
              async : true,
              type:'POST',
              data:{email : email},
              success: function(data){
                  if(data == 'valid')
                    location.href= 'login success url';
                  else
                    location.href= '/user/registration_page';
              },
              error:function(jqXHR, textStatus, errorThrown){
                  console.log(textStatus);
              }
		});
    }


    function fbLoginCallback(response) {
        console.log(response);
        if (response.status === 'connected') {
          // Logged into your app and Facebook.
            //testAPI();
            $('#fbToken').val(response.access_token);
            $('#facebookLoginForm').submit();

        } else if (response.status === 'not_authorized') {

            window.location = encodeURI("https://www.facebook.com/dialog/oauth?client_id=1450591788523941&redirect_uri=http://"+location.host+'/user/registration_page'+"&response_type=token&scope=public_profile,email,user_friends");

            /*
            FB.login(function(response) {
              if (response.status === 'connected') {
                // Logged into your app and Facebook.
                 console.log('logged in');
              } else if (response.status === 'not_authorized') {
                // The person is logged into Facebook, but not your app.
                console.log('facebook logged in but not the app');
              } else {
                // The person is not logged into Facebook, so we're not sure if
                // they are logged into this app or not.
                  console.log('wtff');
              }
            }, {scope: 'public_profile,email,user_friends'});
            */
        } else {
          // The person is not logged into Facebook, so we're not sure if
          // they are logged into this app or not.
        }
    }


    $('.fb-login-btn').click(function(e){
        e.preventDefault();

        FB.getLoginStatus(fbLoginCallback);
    });


    var subMenuInitialize = function(){

        $('.header-sub-menu').removeClass('header-sub-menu-selected');

        var selectedMainMenu = $('#header-main-menu-list a').filter(function(){
            return $(this).hasClass('selected');
        }).attr('data-attr');

        $('#'+selectedMainMenu).addClass('header-sub-menu-selected');
    };

    var mainMenuSelection = function(){
        var menuLinks = $('#header-main-menu-list a');
        menuLinks.click(function(e){
            e.preventDefault();

            if($(this).attr('data-directly') == 'true')
                location.href=$(this).attr('href');

            menuLinks.removeClass('selected');
            $(this).addClass('selected');
            subMenuInitialize();
        });

        $('#headerSearchBtn').click(function(e){
            e.preventDefault();
            menuLinks.removeClass('selected');
            subMenuInitialize();
            $('#headerSearch').addClass('header-sub-menu-selected');
        });
    };

    subMenuInitialize();
    mainMenuSelection();
});