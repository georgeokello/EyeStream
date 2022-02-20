$(document).ready(function(){
    // subscriber button ajax call
    console.log("Am working....")
    $('.subscribe_btn').submit(function(e){
        e.preventDefault()
        const channel_id = $('.sub-btn').val()
        const token = $('input[name=csrfmiddlewaretoken').val()
        const url = $(this).attr('action')
        $.ajax({
            method:"POST",
            url:url,
            headers:{'X-CSRFToken': token},
            data: {
                'channel-id':channel_id
            },
            success:function(response){
                if(response.subscribed==true){
                    $('.sub-btn').removeClass("btn-danger")
                    $('.sub-btn').addClass("disabled")
                }else{
                    $('.sub-btn').removeClass("disabled")
                    $('.sub-btn').addClass("btn-danger")
                }
                $('.sub-count').text(response.num_subscribers)
                console.log(response)
            },
            error:function(error){
                console.log('error occured',error)
            }
        })
    })
})