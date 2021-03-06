$( document ).on( "pageinit", function( event ) {
    function fbLoginCallback(response) {
        if (response.status === 'connected') {
            FB.api('/me', function(user_info) {
                $('#fbEmail').val(user_info.email);
                $('#fbToken').val(response.authResponse.accessToken);
                $('#facebookLoginForm').submit();
            });
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
            FB.login( fbLoginCallback, {scope: 'public_profile,email,user_friends' });
        }
    }


    $('.fb-login-btn').click(function(e){
        e.preventDefault();

        FB.getLoginStatus(fbLoginCallback);
    });
});

$(function(){

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
                    location.href= '/user/mobile_registration_page';
              },
              error:function(jqXHR, textStatus, errorThrown){
                  console.log(textStatus);
              }
		});
    }

    $('.login-box, .login-form').keypress(function(e){
        if(e.keyCode == 13){
            $(this).find('form').submit();
        }
    });

    $('#loginBtn').click(function(e){
        e.preventDefault();
        $('form').submit();
    });
});