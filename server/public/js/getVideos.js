$.get("/videos", function (data, status) {
    console.log("Data: " + data + "\nStatus: " + status);

    html = "";

    data.forEach((video, index) => {
        if (index / 4 === 0) {
            html += "<div class='row'>"
        }

        html += "<div class='col-lg-4 col-md-6 mb-4'>" +
                    "<div class='card h-100'>" +
                        "<a href='/video_player/" + video + "'>" +
                            "<img class='card-img-top' src='/cover/"+ video + "' alt=''>" +
                        "</a>" +
                        "<div class='card-body'>" +
                            "<h4 class='card-title'>" +
                                "<a href='/video_player/" + video + "'>" + video +"</a>" +
                            "</h4>" +
                        "</div>" +
                    "</div>" +
                "</div>";

        if ((index + 1) / 4 === 0) {
            html += "</div>"
        }

    });
    $('#content').append(html);

});
