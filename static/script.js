//var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
var socket = io.connect(window.location.protocol + '//' + window.location.host);
var currentCameraIndex = 4;
var cameras;
var stream;
var width;
var height;
var width_ideal = 1080;
var height_ideal = 1080;
let intervalId;
const video = document.querySelector("#video_element");
const button_next = document.getElementById('next_button');
const button_camera_switch = document.getElementById('camera_button');
const image_solution = document.getElementById('image_solution');
const loader_container = document.getElementById('loader_container');
const loader_text = document.getElementById('loader_text');
const fail_text = document.getElementById("fail");

socket.on('connect', function () {
    console.log("Connected...!", socket.connected)
});


// Listen to the server
socket.on('response', function(response){
    console.log('Received response');
    var [stage, image_stage] = response;
    ViewControl(stage, image_stage);
});

function ViewControl(stage='start', image=null){
    if (stage == "start"){
        get_available_camera();
        setTimeout(function(){
            StartCamera(cameras[currentCameraIndex].deviceId);
            SetWidthHeightCanvas();
            StartStream();
        }, 500);

        //CameraInit();

    }
   else if (stage == "recognition"){
        StopCamera(stream);
        StopSendingFrames();
        ShowImage(image);
        DeactivateButtonNextSearch();
        DeactivateButtonSwitchCamera();
        StartLoader();
        LoaderTextRecognition();
    }
    else if (stage == "solving"){
        LoaderTextSolving();
    }
    else if (stage == "error"){
        StartCamera(cameras[currentCameraIndex].deviceId);
        ShowCameraImage();
        StartStream();
        HideImage();
        StopLoader();
        ShowFailMessage();
    }
   else if (stage == "solution"){
    ShowImage(image);
    StopLoader();
    ActivateButtonNextSearch();
    }
}


function ActivateButtonNextSearch(){
    button_next.removeAttribute('disabled');
}

function DeactivateButtonNextSearch(){
    button_next.disabled = true;
}

function ActivateButtonSwitchCamera(){
    if (cameras.length > 1){
        button_camera_switch.removeAttribute('disabled');
    }
    else{
        button_camera_switch.disabled = true;
    }
}

function DeactivateButtonSwitchCamera(){
    button_camera_switch.disabled = true;
}

function ShowImage(image){
    image_solution.setAttribute('src', image);
    image_solution.style.display = 'flex';
}

function HideImage(){
    image_solution.style.display = 'none';
}

function StopSendingFrames() {
  clearInterval(intervalId);
}

function StopCamera(stream) {
    stream.getTracks().forEach((track) => {
        if (track.readyState == 'live') {
            track.enabled = false;
        }
    });
    video_element.style.display = 'none';
}

function StartLoader(){
    loader_container.style.display = 'flex';
}

function StopLoader(){
    loader_container.style.display = 'none';
}

function LoaderTextRecognition(){
    loader_text.textContent = "Please Wait  \n Recognition in progress";
}

function LoaderTextSolving(){
    loader_text.textContent = 'Please Wait  \n Solving in progress';
}

function ShowFailMessage(){
        fail_text.textContent = "Please try again";
        function clearText() {
            fail_text.textContent = "";
        }
        setTimeout(clearText, 2000);
}

function get_available_camera(){
        navigator.mediaDevices.enumerateDevices()
            .then(function (devices) {
                cameras = devices.filter(function (device) {
                    return device.kind === 'videoinput';
                });
            })
            .catch(function (error) {
                console.log("Error downloading video devices: " + error);
            });
}


function StartCamera(deviceId){

    var constraints = { video: {
                                  deviceId: { exact: deviceId },
                                  width: { ideal: width_ideal },
                                  height: { ideal: height_ideal }
                                } };
    if (navigator.mediaDevices.getUserMedia){
        navigator.mediaDevices.getUserMedia(constraints)
        .then(function (media_stream) {
                video.srcObject = media_stream;
                video.play();
                stream = media_stream;
        })
        .catch(function (error) {
            console.log("Error starting the camera: " + error);
        });
    }
}


function SetWidthHeightCanvas(){
    video.addEventListener('loadedmetadata', function() {
                      width = video.videoWidth;
                      height = video.videoHeight;
                    });
}

function StartStream(){
        const FPS = 2;
        intervalId  = setInterval(() => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;
        get_available_camera();
        ActivateButtonSwitchCamera();
        context.drawImage(video, 0, 0, width, height);
        var data = canvas.toDataURL('image/jpeg', 0.5);
        context.clearRect(0, 0, width, height);
        socket.emit('image', data);
    }, 1000 / FPS);
}


function SwitchCamera() {
    currentCameraIndex++;
    if (currentCameraIndex >= cameras.length) {
        currentCameraIndex = 0;
    }
    StartCamera(cameras[currentCameraIndex].deviceId);
}


function ShowCameraImage(){
    video_element.style.display = 'flex';
}

function NextSearch(){
    HideImage();
    get_available_camera();
    StartCamera(cameras[currentCameraIndex].deviceId);
    SetWidthHeightCanvas();
    StartStream();
    ActivateButtonSwitchCamera();
    DeactivateButtonNextSearch();
    ShowCameraImage();
}


ViewControl();
