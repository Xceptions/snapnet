$(document).ready(function(){
    $("#predict").click(function(e){
        e.preventDefault();

        start_date = $('#start_date').val()
        end_date = $('#end_date').val()
        data = {
            start_date: start_date,
            end_date: end_date
        }
        $.ajax({
            url: "http://localhost:5000/predict/",
            contentType: 'application/json',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function (result) {
                list_items(result);
                // $('#preds').text(JSON.stringify(result))
            },
            error: function (err) {
                alert(err)
            }
        });

        function list_items(result) {
        //  const test = result.map(item => '<li>' + item.date + '</li>')
            // console.log(test);

            let el = '<tbody>'
            const res = result.map(
                item =>
                '<tr>' + 
                '<td>' + item.index + '</td>'
                + '<td>' + item.date + '</td>'
                + '<td>' + item['ticket type'] + '</td>'
                + '<td>' + item['ticket class'] + '</td>'
                + '<td>' + item.sales + '</td>'
                + '</tr>'
            )
            el = el + '</tbody>';

            $('#preds').html(res);
        }
    });
})