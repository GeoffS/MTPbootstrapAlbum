// Copyright 2015, All Rights Reserved
// geoff@geoff-s.net

var opts = {
    lines: 11, // The number of lines to draw
    length: 35, // The length of each line
    width: 11, // The line thickness
    radius: 15, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#ffffff', // #rgb or #rrggbb or array of colors
    speed: 1, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: '50%', // Top position relative to parent
    left: '50%' // Left position relative to parent
};

var bodyElem = document.getElementById('body');
var imgDivElem = document.getElementById('imageDiv');
var footer = document.getElementById('footer');
var oldImage;
var newImage;
var spinner;
var parent;

var hammertime = new Hammer(bodyElem);
hammertime.get('swipe').set({ direction: Hammer.DIRECTION_ALL });
hammertime.on('swipe', swipeHandler);

function swipeHandler(ev){
    console.log('Gesture: '+ev.type);
    footer.innerHTML = "hammertime.on()"+ev.type+', '+ev.direction;
    if((ev.direction & Hammer.DIRECTION_UP) != 0) {
        if(screenfull.enabled) {
            if(screenfull.isFullscreen) {
                console.log('about to do screenfull.exit()...');
                screenfull.exit(bodyElem);
            } else {
                console.log("Going to parent: "+parent);
                window.location.href = parent;
            }
        }
    } else if ((ev.direction & Hammer.DIRECTION_DOWN) != 0) {
        if (screenfull.enabled) {
            console.log('about to do screenfull.request()...');
            screenfull.request(bodyElem);
        }
    } else if ((ev.direction & Hammer.DIRECTION_RIGHT) != 0) {
        nextImage();
    } else if((ev.direction & Hammer.DIRECTION_LEFT) != 0) {
        prevImage();
    }
}
function checkKey(e) {
    e = e || window.event;
    if (e.keyCode == '38') {
        // up arrow
        console.log("Up-arrow - Going to parent: "+parent);
        window.location.href = parent;
    }
    else if (e.keyCode == '40') {
        // down arrow
    }
    else if (e.keyCode == '37') {
       // left arrow
       console.log("Left-arrow");
       prevImage();
    }
    else if (e.keyCode == '39') {
       // right arrow
       console.log("Right-arrow");
       nextImage();
    }
}
function popstateHandler(evt) {
	console.log("Popstate:"+evt.state);
	//imageIndex = evt.state;
    setImageIndexFromQueryString();
	console.log("imageIndex="+imageIndex);
	updateImage();
}
function resize(){
    var imageElem = document.getElementById('image');
    footer.innerHTML = "resize()";
    var docW = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var docH = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    console.log('Screnn now: '+docW+" X "+docH);
    // var imageElem = document.getElementById('image');
    console.log("Image dims(1): "+imageElem.naturalWidth+" x "+imageElem.naturalHeight);
    var imAspect = imageElem.naturalWidth/imageElem.naturalHeight;
    var docAspect = docW/docH;
    var factor = 1.0;
    var scale;
    if (docAspect > imAspect) {
        scale = docH/imageElem.naturalHeight*factor;
    } else {
        scale = docW/imageElem.naturalWidth*factor;
    };
    if(scale > 1.0) {scale = 1.0;}
    console.log("Image dims(2): "+imageElem.naturalWidth+" x "+imageElem.naturalHeight);
    var imW = imageElem.naturalWidth*scale;
    var imH = imageElem.naturalHeight*scale;
    console.log("scale, imW, imH="+scale+", "+imW+", "+imH);;
    imageElem.style.width  = imW+"px";
    imageElem.style.height = imH+"px";
}
function toggleFS() {
    if (screenfull.enabled) {
        console.log('about to do screenfull.toggle(bodyElem)...');
        screenfull.toggle(bodyElem);
        // console.log('about to do screenfull.request(e1)...');
        // screenfull.request(bodyElem);
    }
}
var imageIndex = -1;
var updating = false;
function nextImage(){
    if(updating) return;
    updating = true;
    imageIndex = (imageIndex+1) % images.length;
    replaceImgElem(true);
}
function prevImage() {
    if(updating) return;
    updating = true;
    imageIndex--;
    if (imageIndex < 0) {
        imageIndex = images.length-1;
    }
    replaceImgElem(true);
}
function updateImage() {
	if(updating) return;
    updating = true;
    replaceImgElem(false);
}
function replaceImgElem(doPush) {
    footer.innerHTML = 'nextImage()';
    console.log("nextImage="+imageIndex+', '+images[imageIndex]);
    oldImage = document.getElementById('image');
    newImage = document.createElement("img");
    newImage.src=images[imageIndex];
    
    if(doPush) {
    	//history.pushState(imageIndex, '', parent+'viewer.html?'+images[imageIndex]);
    	console.log('pushState=?'+images[imageIndex]+', '+imageIndex);
    	history.pushState(imageIndex, images[imageIndex], '?'+images[imageIndex]);
    }
    checkComplete(); 
}
function nextImageStep2() {
    console.log("newImg.complete="+newImage.complete);
    if(spinner != null) { spinner.stop(); }
    spinner = null;
    checkCounter = 0;
    newImage.style.display = 'block';
    newImage.style.margin = '0 auto 0 auto';
    //newImage.onclick = nextImage;
    newImage.id='image';
    imgDivElem.replaceChild(newImage, oldImage);
    resize(newImage);
    updating = false;
}
var checkCounter = 0;
var checkWait = 50;
function checkComplete() {
    console.log('oldImage='+oldImage.src);
    console.log('newImage='+newImage.src);
    console.log('newImage.complete='+newImage.complete);
    if(newImage.complete || checkCounter > 10) {
    //if(checkCounter > 3) { // for spinner testing
        nextImageStep2();
    } else {
        checkCounter++;
        if(checkCounter == 1) {
            opts.top = oldImage.height/2+'px';
            oldImage.style.opacity = 0.3;
            spinner = new Spinner(opts).spin(imgDivElem);
        }
        checkWait *= 2;
        checkWait = Math.min(checkWait, 500);
        console.log('About to wait...'+checkWait);
        setTimeout(checkComplete, checkWait);
    }
}
function setImageIndexFromQueryString() {
	var qs = location.search;
    console.log('Query String:'+qs);
    if(qs != null && qs != '' && qs[0] =='?') {
        var imgName = qs.substring(1, 500);
        console.log('imgName='+imgName);
        var noMatch = true;
        for (var i = 0; i < images.length; i++) {
            if(imgName == images[i]){
                imageIndex = i;
                noMatch = false;
                break;
            }
        }
        if(noMatch) {
        	console.log('No matching image name in list...');
        	imageIndex = -1;
        }
    } else {
        console.log('No image in URL...');
        imageIndex = -1;
    }
    console.log('setImageIndexFromQueryString: imageIndex='+imageIndex);
}
function init() {
    console.log('init()');
    footer.innerHTML = 'init()';
    var href = window.location.href;
    parent = href.substring(0, href.lastIndexOf('/')+1);
    console.log('Parent URL: '+parent);
    setImageIndexFromQueryString();
    updateImage();
    bodyElem.onresize = resize;
    document.onkeydown = checkKey;
    window.onpopstate = popstateHandler;
}