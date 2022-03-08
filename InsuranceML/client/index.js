$(document).ready(all)

function all () {
    $('#predict').on('click', function(e){
        e.preventDefault();

        var data = {
            minkgem: $('#minkgem').val(),
            ppersaut: $('#ppersaut').val(),
            mrelge: $('#mrelge').val(),
            mink: $('#mink7512').val(),
            moplhoog: $('#moplhoog').val(),
            pbrand: $('#pbrand').val(),
            mkoopkla: $('#mkoopkla').val(),
            mgemomv: $('#mgemomv').val()
        }
        
        $.ajax({
            type: 'POST',
            url: 'http://localhost:5000/pred/',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function (result) {
                var prediction = result.prediction
                console.log(prediction)
                if (prediction == 1) {
                    prediction = 'will buy'
                }
                else {
                    prediction = 'will not buy'
                }
                window.alert(prediction)
                $('#prediction').text(prediction)
            },
            error: function (error) {
                console.log("error" + error);
            }
        });
    });
}