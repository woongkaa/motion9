/**
 * Created by Park-Kunbae on 14. 3. 31.
 */

$(function(){

    $('.login-box, .login-form').keypress(function(e){
        if(e.keyCode == 13){
            $(this).find('form').submit();
        }
    });

    $('.login-submit-btn').click(function(e){
        e.preventDefault();
        var formType = $(this).attr('data-form');
        var form = $('form').filter(function(){
           return $(this).attr('data-form') == formType;
        });

        form.submit();
    });

    $('#loginBox').jqm({modal:false});
    $('.login-btn').click(function(e){
        e.preventDefault();
        $('#loginBox').jqmShow();
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
            menuLinks.removeClass('selected');
            $(this).addClass('selected');
            subMenuInitialize();
        });
    };

    subMenuInitialize();
    mainMenuSelection();
});