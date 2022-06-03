function start_long_task() {
    // add task status elements
    div = $('<div class="progress"><div></div><div></div><div>...</div><div></div></div><hr>');
    $('#progress').append(div);
    //&nbsp;
    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });

    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: '/dashboard/longtask',
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, nanobar, div[0]);
        },
        error: function() {
            alert('Unexpected error');
        }
    });
}
function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function(data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);

        var redirectButton = document.getElementsByClassName('redirectButton')[0];

        nanobar.go(percent);
        $(status_div.childNodes[0]).text('');
        $(status_div.childNodes[2]).text(' ' + data['status']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // show result
                //$(status_div.childNodes[3]).text('');
                //progress.style.display = "none";
                redirectButton.style.display = "block";
            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 1 second
            setTimeout(function() {
                update_progress(status_url, nanobar, status_div);
            }, 1000);
        }
    });
}
$(function() {
    $('#start-bg-job').click(start_long_task);
});