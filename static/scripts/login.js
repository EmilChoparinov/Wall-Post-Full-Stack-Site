$(document).ready(function(){
    $('button').click(function(){
        window.location = "register"
    });
    $('form').keydown(function(e){
        if(e.which == 13){
            $('form').submit();
        }
    })
});