function start_long_task(task_location, task_data) {
    // add task status elements
    div = $('<div class="progress"><div></div><div></div><div>...</div><div></div></div>');
    var redirectButton = document.getElementsByClassName('redirectButton')[0];
    if ($('#progress')[0].innerHTML.length > 0) {
        redirectButton.style.display = "none";
        $('#progress')[0].innerHTML = "";
        $('#progress').append(div);
    } else {
        $('#progress').append(div);
    }
    
    //&nbsp;
    // create a progress bar
    var nanobar = new Nanobar({
        bg: '#44f',
        target: div[0].childNodes[0]
    });
    
    if (task_location === '/dashboard/longtask') {
        var result_string = "?num_items=";
        result_string += task_data.numberRequested + "&";
        result_string += "start_date=" + task_data.startDate + "&";
        result_string += "end_date=" + task_data.endDate;
    } else {
        var result_string = "?data=";
        var filling_words = ["and", "as well as", "with"];
        // convert task_data to readable form
        for (var i = 0; i < task_data.length; i++) {
            if (i === (task_data.length - 1)) {
                result_string += task_data[i];
            } else {
                result_string += task_data[i] + " " + filling_words[Math.floor(Math.random()*filling_words.length)] + " ";
            }
        }
    }
    
    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: task_location + result_string,
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
//$(function() {
//    $('#start-bg-job').click(start_long_task);
//});