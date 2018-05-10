var player;

window.onload = () => {
    setVideoURL();
    videoQualityListener();
    getVideoQualities();
}


function getAllUrlParams(url) {

    // get query string from url (optional) or window
    var queryString = url ? url.split('?')[1] : window.location.search.slice(1);

    // we'll store the parameters here
    var obj = {};

    // if query string exists
    if (queryString) {

        // stuff after # is not part of query string, so get rid of it
        queryString = queryString.split('#')[0];

        // split our query string into its component parts
        var arr = queryString.split('&');

        for (var i = 0; i < arr.length; i++) {
            // separate the keys and the values
            var a = arr[i].split('=');

            // in case params look like: list[]=thing1&list[]=thing2
            var paramNum = undefined;
            var paramName = a[0].replace(/\[\d*\]/, function (v) {
                paramNum = v.slice(1, -1);
                return '';
            });

            // set parameter value (use 'true' if empty)
            var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];

            // (optional) keep case consistent
            paramName = paramName.toLowerCase();
            paramValue = paramValue.toLowerCase();

            // if parameter name already exists
            if (obj[paramName]) {
                // convert value to array (if still string)
                if (typeof obj[paramName] === 'string') {
                    obj[paramName] = [obj[paramName]];
                }
                // if no array index number specified...
                if (typeof paramNum === 'undefined') {
                    // put the value on the end of the array
                    obj[paramName].push(paramValue);
                }
                // if array index number specified...
                else {
                    // put the value at that index number
                    obj[paramName][paramNum] = paramValue;
                }
            }
            // if param name doesn't exist yet, set it
            else {
                obj[paramName] = paramValue;
            }
        }
    }

    return obj;
}

function setVideoURL() {
    let url = getAllUrlParams().video;
    player = dashjs.MediaPlayer().create();

    player.initialize(document.querySelector("#videoPlayer"), url, false);
};

function toogleSettings() {
    $('#qualityList').toggle();
}

function addItemToList(elements, list) {
    $.each(elements, function (index, value) {
        $(list).append($('<option/>', {
            value: value.qualityIndex,
            text: value.height
        }));
    });
}

function videoQualityListener(){
    $("#qualityList").bind("change", function () {
        if($(this).val() === 'auto') {
            player.setAutoSwitchQualityFor("video", true);
            player.setBufferAheadToKeep(80);
        } else {
            player.setAutoSwitchQualityFor("video", false);
            player.setQualityFor("video", $(this).val());
            player.setBufferAheadToKeep(2);
        }
        player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, function () {
            console.warn("QUALITY_CHANGE_RENDERED");
            player.setBufferAheadToKeep(80);
        });
    });
}

function getVideoQualities() {
    player.attachVideoContainer(document.getElementById("videoContainer"));
    //player.getDebug().setLogToBrowserConsole(false);

    player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, function () {
        let bitrates = player.getBitrateInfoListFor("video");
        let quality = bitrates[0].qualityIndex; //PRUEBA

        addItemToList(bitrates, '#qualityList');
        player.setQualityFor("video", quality);
        player.setTrackSwitchModeFor("video", "MediaController.TRACK_SWITCH_MODE_ALWAYS_REPLACE");
        player.setFastSwitchEnabled(true);
    });
}
