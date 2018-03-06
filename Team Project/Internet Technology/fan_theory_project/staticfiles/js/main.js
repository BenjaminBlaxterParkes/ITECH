$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Submit post on submit
    $('.vote-plus').on('click', function(){
        form = $($(this)[0].form)
        $.ajax({
            method: 'GET',
            url: '/fan_theory/vote',
            data: {
                    'comment': form.children('input[name="comment"]').val(),
                    'direction': 1,
                    'user': form.children('input[name="user"]').val()
            },
            success: function (data) {
                 //this gets called when server returns an OK response
                 form.children('p[class="count"]').text(parseInt(form.children('p[class="count"]').text())+1)
                 //alert(data);
            },
            error: function (data) {
                 alert(JSON.stringify(data));
            }
        });
        console.log(form.children('input[name="comment"]').val()+' '+form.children('input[name="user"]').val()+' plus')  // sanity check
    });

    $('.vote-minus').on('click', function(){
        console.log($(this).class+' minus')  // sanity check
    });

});