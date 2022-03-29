const stream = document.getElementById('stream');
const identityInput = document.getElementById('identity');
const streamNameInput = document.getElementById('streamName');
const startEndButton = document.getElementById('streamStartEnd');
const video = document.getElementsByTagName('video')[0];
const liveNotification = document.getElementById('notification') 
const loadingStatus = document.getElementById('statusLoading') 
let streaming = false;
let live_room;
let streamDetails;


liveNotification.style.visibility = "hidden";
loadingStatus.style.visibility = 'hidden';

const addLocalVideo = async () => {
    const videoTrack = await Twilio.Video.createLocalVideoTrack();
    const trackElement = videoTrack.attach();
    stream.appendChild(trackElement);
};

addLocalVideo();

// Cookies method 

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');


const startStream = async (streamName, identity) => {
    // loading
    loadingStatus.style.visibility = "visible"
    // Create the livestream
    const startStreamResponse = await fetch('startStream', {
        method: 'POST',
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'streamName': streamName
        })
    });

    console.log(csrftoken);

    streamDetails = await startStreamResponse.json();
    const roomId = streamDetails.roomId;

    // Get an Access Token
    const tokenResponse = await fetch('/streamerToken', {
        method: 'POST',
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'identity': identity,
            'room': roomId,
        })
    });

    const tokenData = await tokenResponse.json();

    // Connect to the Video Room
    live_room = await Twilio.Video.connect(tokenData.token);
    streaming = true;

    //hiding status text
    loadingStatus.style.visibility = "hidden"
    // stream.insertBefore(liveNotification, video);
    liveNotification.style.visibility = "visible";

    startEndButton.disabled = false;
    startEndButton.classList.replace('btn-outline-primary', 'btn-danger');
    startEndButton.classList.replace('hover:btn-outline-primary', 'btn-danger');
}


const endStream = async () => {
    // If streaming, end the stream
    if (streaming) {
        try {
            const response = await fetch('/endLiveStream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    streamDetails: streamDetails
                })
            });

            const data = await response.json();
            live_room.disconnect();
            streaming = false;
            liveNotification.remove();

            startEndButton.innerHTML = 'start stream';
            startEndButton.classList.replace('bg-red-500', 'bg-green-500');
            startEndButton.classList.replace('hover:bg-red-500', 'hover:bg-green-700');
            identityInput.disabled = false;
            streamNameInput.disabled = false;

        } catch (error) {
            console.log(error)
        }
    }
}


const startOrEndStream = async (event) => {
    event.preventDefault();
    if (!streaming) {
        const streamName = streamNameInput.value;
        console.log(streamName)
        const identity = identityInput.value;
        console.log(identity)

        startEndButton.innerHTML = 'end stream';
        startEndButton.disabled = true;
        identityInput.disabled = true;
        streamNameInput.disabled = true;

        try {
            await startStream(streamName, identity);

        } catch (error) {
            console.log(error);
            alert('Unable to start livestream.', error);
            startEndButton.innerHTML = 'start stream';
            startEndButton.disabled = false;
            identityInput.disabled = false;
            streamNameInput.disabled = false;
        }

    }
    else {
        endStream();
    }
};

startEndButton.addEventListener('click', startOrEndStream);

window.addEventListener('beforeunload', async (event) => {
    event.preventDefault();
    await endStream();
    e.returnValue = '';
});

