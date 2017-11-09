$(document).ready(function(){
    $('#post').keydown(function(e){
        if(e.which == 13){
            $('#process_post_post').submit();
        }
    });
    $('form').keydown(function(e){
        console.log('key pressed')
        if(e.which == 13){
            $(this).submit();
        }
    });
});