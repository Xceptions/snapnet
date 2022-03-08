$(document).ready(function(){
    data = {
        "chimamanda": "churn",
        "christian": "no churn",
        "samson": "no churn",
        "fred": "churn",
        "adichie": "no churn",
        "dele": "churn"
    }

    $("#check_churn").click(function(e){
        e.preventDefault();

        person = $("#customer").val()
        
        $('#preds').text(data[person])
        // $.ajax({
        //     url: "http://localhost:5000/predict/",
        //     contentType: 'application/json',
        //     type: 'POST',
        //     dataType: 'json',
        //     data: JSON.stringify(data),
        //     success: function (result) {
        //         $('#preds').text(data["Chimamanda Adichie"])
        //     },
        //     error: function (err) {
        //         console.log(err)
        //     }
        // });
    });

    $("#check_all").click(function(e){
        e.preventDefault();
        
        for (var key in data) {
            document.write(" " + key + " " + data[key] + '&nbsp;');
        }
        // $.ajax({
        //     url: "http://localhost:5000/predict/",
        //     contentType: 'application/json',
        //     type: 'POST',
        //     dataType: 'json',
        //     data: JSON.stringify(data),
        //     success: function (result) {
        //         $('#preds').text(data["Chimamanda Adichie"])
        //     },
        //     error: function (err) {
        //         console.log(err)
        //     }
        // });
    });
})