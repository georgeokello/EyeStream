
const progressBar = document.getElementById('progress-bar')
const successMgs = document.getElementById('success')


$(document).ready(function(){
    // subscriber button ajax call
    $('#profileUpdate').submit(function(e){
        e.preventDefault();
        $form = $(this)
        const token = $('input[name=csrfmiddlewaretoken').val()
        const url = $(this).attr('action')
        var formData = new FormData(this);


        // remove progress bar invisible class
        progressBar.classList.remove('invisible')

        $.ajax({
            method:"POST",
            url:url,
            headers:{'X-CSRFToken': token},
            data: formData,
            enctype: 'multipart/form-data',
            beforeSend: function(){

            },
            xhr: function(){
                const xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener('progress', e=>{
                    console.log(e)
                    if(e.lengthComputable){
                        const percent = e.loaded / e.total * 100
                        console.log(percent)
                        successMgs.innerHTML = "updated, refresh to see changes"

                        progressBar.innerHTML = `
                        
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                            <p>${percent.toFixed(1)}%</p>
                        </div>
                        
                        `
                    }
                })
                return xhr
            },
            success:function(response){
                console.log(response)

                console.log('for full image url ' + $('#profileImg').prop('src') );
                console.log('for relative image url ' + $('#profileImg').attr('src'));


            },
            error:function(error){
                console.log('error occured',error)
            },
            processData: false,
            contentType: false,
            cache: false,
        })
    })
})
