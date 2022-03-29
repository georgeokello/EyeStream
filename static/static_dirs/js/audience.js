const streamPlayer = document.getElementById('player');
const startEndButton = document.getElementById('streamStartEnd');

let player;
let watchingStream = false;

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


const watchStream = async () => {
    try {
        const response = await fetch('/audienceToken', {
            method: 'POST',
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                'X-CSRFToken': csrftoken,
            },
        });

        const data = await response.json();
        console.log(data)

        if (data.message) {
            alert(data.message);
            return;
        }

        player = await Twilio.Live.Player.connect(data.token, { playerWasmAssetsPath: '../playerArtifacts' });
        player.play();
        streamPlayer.appendChild(player.videoElement);

        watchingStream = true;
        startEndButton.innerHTML = 'leave stream';
        startEndButton.classList.replace('bg-green-500', 'bg-red-500');
        startEndButton.classList.replace('hover:bg-green-500', 'hover:bg-red-700');

    } catch (error) {
        console.log(error);
        alert('Unable to connect to livestream');
    }
}


const leaveStream = () => {
    player.disconnect();
    watchingStream = false;
    startEndButton.innerHTML = 'watch stream';
    startEndButton.classList.replace('bg-red-500', 'bg-green-500');
    startEndButton.classList.replace('hover:bg-red-500', 'hover:bg-green-700');
}

const watchOrLeaveStream = async (event) => {
    event.preventDefault();
    if (!watchingStream) {
        await watchStream();
    }
    else {
        leaveStream();
    }
};

startEndButton.addEventListener('click', watchOrLeaveStream);


