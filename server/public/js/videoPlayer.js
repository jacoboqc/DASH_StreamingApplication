var player, 
    videoController, //DONDE VA LA LISTA, JUSTO DEBAJO DEL VIDEO
    bitrateListBtn, 
    bitrateListMenu = null,
    menuHandlersList = [];


window.onload = () => {
    setVideoURL();
    videoController = document.getElementById("videoController");
    bitrateListBtn = document.getElementById("bitrateListBtn");
    player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, onStreamInitialized, this);

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

function setVideoURL () {

    var url = getAllUrlParams().video;
    player = dashjs.MediaPlayer().create();
    player.initialize(document.querySelector("#videoPlayer"), url, false);
    
    player.attachVideoContainer(document.getElementById("videoContainer"));
    player.getDebug().setLogToBrowserConsole(false);
    player.setAutoSwitchQualityFor("video", false);

    player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED,function(){
        var bitrates = player.getBitrateInfoListFor("video"),
        quality = bitrates[0].qualityIndex; //PRUEBA
        player.setQualityFor("video", quality);
    });

};


onStreamInitialized = function(e) { //SE LLAMA CUANDO SE INICIALIZA EL PLAYER

    var availableBitrates = {menuType: 'bitrate'};
    availableBitrates.video = player.getBitrateInfoListFor("video") || []; //ESTO TE DA LA LISTA DE BITRATES ETC
    if (availableBitrates.video.length > 1) { //OBVIAMENTE SI NO ES MAS DE UNO NO PUEDES CAMBIAR
        contentFunc = function (element, index) {
            return isNaN(index) ? "Auto" : element.height; // AQUI SE GENERAN LOS DIFERENTES ELEMENTOS, UNO AUTO Y EL RESTO CON EL HEIGHT QUE ES EL MITICO DE YOUTUBE
        }

        // SI SE QUEDA MARCADO LA CALIDAD ESCOGIDA COJONUDO ;)
        bitrateListMenu = createMenu(availableBitrates, contentFunc);
        var func = function () {
            onMenuClick(bitrateListMenu, bitrateListBtn);
        };
        menuHandlersList.push(func);
        bitrateListBtn.addEventListener("click", func);
        bitrateListBtn.classList.remove("hide");

    } else {
        bitrateListBtn.classList.add("hide");
    }

}

createMenu = function (info, contentFunc) {

    var menuType = info.menuType;
    var el = document.createElement("div");
    el.id = menuType + "Menu";
    el.classList.add("menu");
    videoController.appendChild(el);

    if (info.video.length > 1) {
        el.appendChild(createMediaTypeMenu("video"));
        el = createMenuContent(el, getMenuContent(menuType, info.video, contentFunc), 'video', 'video-' + menuType + '-list');
        setMenuItemsState(getMenuInitialIndex(info.video, menuType, 'video'), 'video-' + menuType + '-list');
    }

}

getMenuContent = function (type, arr, contentFunc) {

    var content = [];
    arr.forEach(function (element, index) {
        content.push(contentFunc(element, index));
    })
    if (type !== 'track') {
        content.unshift(contentFunc(null, NaN));
    }
    return content;
}

createMediaTypeMenu = function (type) {

    var div = document.createElement("div");
    var title = document.createElement("div");
    var content = document.createElement("ul");

    div.id = type;

    title.textContent = type === 'video' ? 'Video' : 'Audio';
    title.classList.add('menu-sub-menu-title');

    content.id = type + "Content";
    content.classList.add(type + "-menu-content");

    div.appendChild(title);
    div.appendChild(content);

    return div;
}

createMenuContent = function (menu, arr, mediaType, name) {

    for (var i = 0; i < arr.length; i++) {

        var item = document.createElement("li");
        item.id = name + "Item_" + i;
        item.index = i;
        item.mediaType = mediaType;
        item.name = name;
        item.selected = false;
        item.textContent = arr[i];

        item.onmouseover = function (e) {
            if (this.selected !== true) {
                this.classList.add("menu-item-over");
            }
        };
        item.onmouseout = function (e) {
            this.classList.remove("menu-item-over");
        };
        item.onclick = setMenuItemsState.bind(item);

        var el;
        if (mediaType === 'caption') {
            el = menu.querySelector("ul");
        } else {
            el = menu.querySelector('.' + mediaType + "-menu-content");
        }

        el.appendChild(item);
    }

    return menu;
}

setMenuItemsState = function (value, type) {

    var self = typeof value === 'number' ? document.getElementById(type + "Item_" + value) : this,
        nodes = self.parentElement.children;

    for (var i = 0; i < nodes.length; i++) {
        nodes[i].selected = false;
        nodes[i].classList.remove("menu-item-selected");
        nodes[i].classList.add("menu-item-unselected");
    }
    self.selected = true;
    self.classList.remove("menu-item-over");
    self.classList.remove("menu-item-unselected");
    self.classList.add("menu-item-selected");


    if (type === undefined) { // User clicked so type is part of item binding.
        switch (self.name) {
            case 'video-bitrate-list':
            case 'audio-bitrate-list':
                if (self.index > 0) {
                    if (player.getAutoSwitchQualityFor(self.mediaType)) {
                        player.setAutoSwitchQualityFor(self.mediaType, false);
                    }
                    player.setQualityFor(self.mediaType, self.index - 1);
                } else {
                    player.setAutoSwitchQualityFor(self.mediaType, true);
                }
                break;
            case 'caption-list' :
                player.setTextTrack(self.index - 1);
                break
            case 'video-track-list' :
            case 'audio-track-list' :
                player.setCurrentTrack(player.getTracksFor(self.mediaType)[self.index]);
                break;
        }
    }
}

getMenuInitialIndex = function(info, menuType, mediaType) {
    if (menuType === 'track') {

        var mediaInfo = player.getCurrentTrackFor(mediaType);
        var idx = 0
        info.some(function(element, index){
            if (isTracksEqual(element, mediaInfo)) {
                idx = index;
                return true;
            }
        })
        return idx;

    } else if (menuType === "bitrate") {
        return player.getAutoSwitchQualityFor(mediaType) ? 0 : player.getQualityFor(mediaType);
    } else if (menuType === "caption") {
        var idx = player.getCurrentTextTrackIndex() + 1;

        return idx;
    }
}
