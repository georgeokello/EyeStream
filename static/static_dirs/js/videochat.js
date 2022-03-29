const form = document.getElementById("room-name-form");
const roomNameInput = document.getElementById("room-name-input");
const container = document.getElementById("video-container");
const tokenInput = document.getElementById("token");
const roomNameSpace = document.getElementById("roomName");
const muteAudio = document.getElementById("mute_Audio");
const muteVideo = document.getElementById("mute_Video");
const leave = document.getElementById("leave_call");

muteAudio.style.visibility = "hidden";
muteVideo.style.visibility = "hidden";
leave.style.visibility = "hidden";

let room;
let localParticipant;

const startRoom = async (event) => {
    // prevent a page reload when a user submits the form
    event.preventDefault();
    // hide the join form
    form.style.display = "none";
    muteAudio.style.visibility = "visible";
    muteVideo.style.visibility = "visible";
    leave.style.visibility = "visible";
    roomNameSpace.style.visibility = "visible";


    // retrieve the room name
    const roomName = roomNameInput.value;
    // setting the room name on the page
    roomNameSpace.innerHTML = roomName;

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

    // fetch an Access Token from the join-room route
    const response = await fetch('join_room', {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ room_name: roomName }),
    });

    console.log(csrftoken);

    const { token } = await response.json();

    // join the video room with the token
    room = await joinVideoRoom(roomName, token);

    localParticipant = room.localParticipant;
    // render the local and remote participants' video and audio tracks
    handleConnectedParticipant(room.localParticipant);
    room.participants.forEach(handleConnectedParticipant);
    room.on("participantConnected", handleConnectedParticipant);


    // handle cleanup when a participant disconnects
    room.on("participantDisconnected", handleDisconnectedParticipant);
    window.addEventListener("pagehide", () => room.disconnect());
    window.addEventListener("beforeunload", () => room.disconnect());
};

const handleConnectedParticipant = (participant) => {
    // create a div for this participant's tracks
    const participantDiv = document.createElement("div");

    // mute audio
    muteAudio.onclick = () => {
        room.localParticipant.audioTracks.forEach(track => {
            if(track.track.isEnabled){
                track.track.disable();
                muteAudio.innerHTML = "Umute Audio"
            }else{
                track.track.enable();
                muteAudio.innerHTML = "Mute Audio";
            }
            
        });
    };

    // mute video
    muteVideo.onclick = () => {
        room.localParticipant.videoTracks.forEach(track => {
            if(track.track.isEnabled){
                track.track.disable();
                muteVideo.innerHTML = "Umute Video"
            }else{
                track.track.enable();
                muteVideo.innerHTML = "Mute Video";
            }
            
        });
    };

    // leave call
    leave.onclick = () => {
        handleDisconnectedParticipant(localParticipant);
        room.disconnect();
        // hide elements
        participantDiv.remove();
        muteAudio.style.visibility = "hidden";
        muteVideo.style.visibility = "hidden";
        leave.style.visibility = "hidden";
        form.style.display = "block";
        roomNameSpace.style.visibility = "hidden";
    };

    participantDiv.setAttribute("id", participant.identity);
    container.appendChild(participantDiv);

    // iterate through the participant's published tracks and
    // call `handleTrackPublication` on them
    participant.tracks.forEach((trackPublication) => {
        handleTrackPublication(trackPublication, participant);
    });

    // listen for any new track publications
    participant.on("trackPublished", handleTrackPublication);
};

const handleTrackPublication = (trackPublication, participant) => {
    function displayTrack(track) {
        // append this track to the participant's div and render it on the page
        const participantDiv = document.getElementById(participant.identity);
        // track.attach creates an HTMLVideoElement or HTMLAudioElement
        // (depending on the type of track) and adds the video or audio stream
        participantDiv.append(track.attach());
    }

    // check if the trackPublication contains a `track` attribute. If it does,
    // we are subscribed to this track. If not, we are not subscribed.
    if (trackPublication.track) {
        displayTrack(trackPublication.track);
    }

    // listen for any new subscriptions to this track publication
    trackPublication.on("subscribed", displayTrack);
};


const handleDisconnectedParticipant = (participant) => {
    // stop listening for this participant
    participant.removeAllListeners();
    // remove this participant's div from the page
    const participantDiv = document.getElementById(participant.identity);
    participantDiv.remove();
};

const joinVideoRoom = async (roomName, token) => {
    // join the video room with the Access Token and the given room name
    const room = await Twilio.Video.connect(token, {
        room: roomName,
        audio: true,
        video: true,
    });
    return room;
};



form.addEventListener("submit", startRoom);



