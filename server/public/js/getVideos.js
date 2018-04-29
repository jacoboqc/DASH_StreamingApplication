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
                            "<img class='card-img-top' src='http://placehold.it/700x400' alt=''>" +
                        "</a>" +
                        "<div class='card-body'>" +
                            "<h4 class='card-title'>" +
                                "<a href='/video_player/" + video + "'>Item One</a>" +
                            "</h4>" +
                            "<p class='card-text'>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Amet numquam aspernatur!</p>" +
                        "</div>" +
                    "</div>" +
                "</div>";

        if ((index + 1) / 4 === 0) {
            html += "</div>"
        }

    });
    $('#content').append(html);

});

/*
data ="<div class='row'>" +
        "<div class='col-lg-4 col-md-6 mb-4'>" +
            "<div class='card h-100'>" +
                "<a href='/video_player/jellyfish-25-mbps-hd-hevc'>" +
                    "<img class='card-img-top' src='http://placehold.it/700x400' alt=''>" +
                "</a>" +
                "<div class='card-body'>" +
                    "<h4 class='card-title'>"
                        "<a href='/video_player/jellyfish-25-mbps-hd-hevc'>Item One</a>" +
                    "</h4>"+
                    "<p class='card-text'>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Amet numquam aspernatur!</p>"+
                "</div>"+
            "</div>" +
        "</div>" +

*/
