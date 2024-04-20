const socket = io('/'); // Connect to the root path of your server
const videoGrid = document.getElementById('video-grid'); // The HTML element where video streams will be added
const myVideo = document.createElement('video');
myVideo.muted = true;

// Creating a Peer object with an undefined id, which means it will be assigned by the server
const myPeer = new Peer(undefined, {
    host: '/', // Should be updated with your PeerJS server
    port: '3001' // Ensure the PeerJS server is listening on this port
});

// Request access to the user's video and audio
navigator.mediaDevices.getUserMedia({
    video: true,
    audio: true
}).then(stream => {
    addVideoStream(myVideo, stream); // Add our video stream to the video grid

    // Handle incoming calls
    myPeer.on('call', call => {
        call.answer(stream); // Answer the call with an A/V stream.
        const video = document.createElement('video');
        call.on('stream', userVideoStream => {
            addVideoStream(video, userVideoStream); // Add the caller's video stream to the video grid
        });
    });

    // When a new user connects, connect to them
    socket.on('user-connected', userId => {
        connectToNewUser(userId, stream);
    });
}).catch(error => {
    console.error('Error accessing media devices:', error);
});

// When we first open our Peer connection
myPeer.on('open', id => {
    socket.emit('join-room', ROOM_ID, id); // Notify server we're joining this room
});

// Convenience function to add a video stream to the DOM and play it
function addVideoStream(video, stream) {
    video.srcObject = stream;
    video.addEventListener('loadedmetadata', () => {
        video.play();
    });
    videoGrid.append(video);
}

// Function to connect to a new user
function connectToNewUser(userId, stream) {
    const call = myPeer.call(userId, stream); // Call the new user with our current stream
    const video = document.createElement('video');
    call.on('stream', userVideoStream => {
        addVideoStream(video, userVideoStream); // Add the new user's video to the grid once their stream is received
    });
    call.on('close', () => {
        video.remove(); // Remove the video from the grid once the call is closed
    });
}

