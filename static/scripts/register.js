$(document).ready(function(){
    $('button').click(function(){
        window.location = "login"
    });
    $('form').keydown(function(e){
        if(e.which == 13){
            $('form').submit();
        }
    });
});