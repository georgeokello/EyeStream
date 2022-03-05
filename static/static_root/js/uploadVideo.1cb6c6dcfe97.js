
// form upload
$('#id_ajax_upload_form').submit(function (e) {
    e.preventDefault();
    $form = $(this)
    const token = $('input[name=csrfmiddlewaretoken').val()
    const url = $(this).attr('action')
    var formData = new FormData(this);
    $.ajax({
        url: url,
        type: 'POST',
        headers:{'X-CSRFToken': token},
        data: formData,
        success: function (response) {
            $('.error').remove();
            console.log(response)
            if (response.error) {
                $.each(response.errors, function (name, error) {
                    error = '<small class="text-muted error">' + error + '</small>'
                    $form.find('[name=' + name + ']').after(error);
                })
            }
            else {
                alert(response.message)
                window.location = ""
            }
        },
        cache: false,
        contentType: false,
        processData: false
    });
});
    // end
