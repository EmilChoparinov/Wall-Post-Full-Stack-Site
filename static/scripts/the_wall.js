$(document).ready(function(){
    $('#post').keydown(function(e){
        if(e.which == 13){
            $('#process_post_post').submit();
        }
    });
    $('#comment_text').keydown(function(e){
        if(e.which == 13){
            $('#process_post_comment').submit();
        }
    });
});