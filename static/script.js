// local host:
//var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
var socket = io.connect(window.location.protocol + '//' + window.location.host);

socket.on('connect', function () {
    console.log("Connected...!", socket.connected)
});

var currentCameraIndex = 0;
var cameras;
const video = document.querySelector("#videoElement");
var stream;
let intervalId;
var width;
var height;
var width_ideal = 1080;
var height_ideal = 1080;

// odbieranie klatek z servera, i ustawienie elementu <photo> jego źródła jako image które przyszło
socket.on('processed_image', function (image) {
    photo.setAttribute('src', image);
});


socket.on('response', function(response){
    console.log('odbieram response');
    var [stage, image_stage] = response;
    //console.log(stage);
    //console.log(image_stage);
    view_control(stage, image_stage);
});

function view_control(stage='start', image=null){
    if (stage == "start"){
        CameraInit();
        StartStream();
        //ActivateButtonSwitchCamera();

    }
    else if (stage == "solution"){
        ShowImage(image);
        StopLoader();
        ActivateButtonNextSearch();
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
            RestartCamera(cameras[currentCameraIndex].deviceId);
            ShowCameraImage();
            StartStream();
            HideImage();
            StopLoader();
            ShowFailMessage();
            //ActivateButtonSwitchCamera(); to juz jest w startstream
    }
}




function ActivateButtonNextSearch(){
    const button = document.getElementById('next-button');
    button.removeAttribute('disabled');
}

function DeactivateButtonNextSearch(){
    const button = document.getElementById('next-button');
    button.disabled = true;
}

function ActivateButtonSwitchCamera(){
    //console.log("camera length", cameras.length > 1);
    const button = document.getElementById('camera-button');
    console.log("camera length", cameras.length);
    if (cameras.length > 1){

        button.removeAttribute('disabled');
    }
    else{
        button.disabled = true;
    }
}

function DeactivateButtonSwitchCamera(){
    const button = document.getElementById('camera-button');
    button.disabled = true;
}

function ShowImage(image){
// ale jeszcze trzeba tutaj ustawic ten obrazek
    const image_solution = document.getElementById('image_solution');
    //photo.setAttribute('src', image); gdzie imgae jest prosto tym obrazem przesłąnym z serwera
    image_solution.setAttribute('src', image);
    //image_solution.setAttribute('src', 'static/8_4.jpg');

    image_solution.style.display = 'flex';
}

function HideImage(){
    const loader = document.getElementById('image_solution');
    loader.style.display = 'none';
}

function StopSendingFrames() {
  clearInterval(intervalId);
}


function StopCamera(stream) {
    // Stop recording camera and hide recording area
    stream.getTracks().forEach((track) => {
        if (track.readyState == 'live') {
            track.enabled = false;
        }
    });

    const videoElement = document.getElementById('videoElement');
    videoElement.style.display = 'none';
}


function StartLoader(){
    const Loader_container = document.getElementById('Loader_container');
    Loader_container.style.display = 'flex';//'inline-block';
}

function StopLoader(){
    const Loader_container = document.getElementById('Loader_container');
    Loader_container.style.display = 'none';//'inline-block';
}

function LoaderTextRecognition(){
    var element = document.getElementById('loader_text');
    element.textContent = "Please Wait  \n Recognition in progress";
}

function LoaderTextSolving(){
    var element = document.getElementById('loader_text');
    element.textContent = 'Please Wait  \n Solving in progress';
}


function ShowFailMessage(){
    var myTextElement = document.getElementById("fail");

        // Ustaw tekst w elemencie
        myTextElement.textContent = "Fail";

        // Funkcja do usunięcia tekstu po 2 sekundach
        function clearText() {
            myTextElement.textContent = "";
        }

        // Wywołaj funkcję clearText() po 2 sekundach
        setTimeout(clearText, 2000);

}


function get_available_camera(){
// zmienia tylko zmienna cameras czyli liste kamer
    var videoElement = document.getElementById("videoElement");

    //var mediaDevices = navigator.mediaDevices;
    //console.log("media ", mediaDevices)
        // Pobierz dostępne urządzenia wideo
        navigator.mediaDevices.enumerateDevices()
            .then(function (devices) {
                cameras = devices.filter(function (device) {
                    return device.kind === 'videoinput';
                });

            })
            .catch(function (error) {
                console.log("Błąd podczas pobierania urządzeń wideo: " + error);
            });
        console.log("media cameras", cameras)
        //return cameras
}

// to jest do pierwszego odpalenai kamery
function CameraInit(){

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            video:{
                width: {ideal: width_ideal},
                height: {ideal: height_ideal}
            }
        })
            .then(function (media_stream) {
                video.srcObject = media_stream;
                video.play();
                stream = media_stream;

                video.addEventListener('loadedmetadata', function() {
                      width = video.videoWidth;
                      height = video.videoHeight;
                      console.log('Użyte wymiary video1:', width, height);
                    });
            })
            .catch(function (err0r) {
            });
    }
}


// to jest do odpalania nowej kamert po jej przełaczneiu
function StartCameraChange(deviceId) {
    var constraints = { video: {
                                  deviceId: { exact: deviceId },
                                  width: { ideal: width_ideal },
                                  height: { ideal: height_ideal }
                                } };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(function (media_stream) {
                video.srcObject = media_stream;
                video.play();
                stream = media_stream;
        })
        .catch(function (error) {
            console.log("Błąd podczas uruchamiania kamery: " + error);
        });
}

// to jest do odpalenia kamert dla nowego wyszukiwania
function RestartCamera(deviceId){
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

                video.addEventListener('loadedmetadata', function() {
                      width = video.videoWidth;
                      height = video.videoHeight;
                      console.log('Użyte wymiary video1:', width, height);
                    });
        })
        .catch(function (error) {
            console.log("Błąd podczas uruchamiania kamery: " + error);
        });
    }
}


function StartStream(){
        const FPS = 1;
        intervalId  = setInterval(() => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;
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

    StartCameraChange(cameras[currentCameraIndex].deviceId);
}


function ShowCameraImage(){
    const videoElement = document.getElementById('videoElement');
    videoElement.style.display = 'flex';
}

function NextSearch(){

    HideImage();
    get_available_camera();
    RestartCamera(cameras[currentCameraIndex].deviceId);
    StartStream();
    ActivateButtonSwitchCamera();
    DeactivateButtonNextSearch();
    ShowCameraImage();
    //const videoElement = document.getElementById('videoElement');
    //videoElement.style.display = 'flex';
}


view_control();
get_available_camera();