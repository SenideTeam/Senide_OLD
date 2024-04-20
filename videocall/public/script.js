const socket = io('/');
const videoGrid = document.getElementById('video-grid');
const myPeer = new Peer(undefined, {
    host: '/',
    port: '3001'
});
const myVideo = document.createElement('video');
myVideo.muted = true;

navigator.mediaDevices.getUserMedia({
    video: true,
    audio: true
}).then(stream => {
    addVideoStream(myVideo, stream)

    myPeer.on('call', call =>{
        call.answer(stream)
        const video = document.createElement('video')
        call.on('stream', userVideoStream =>{
            addVideoStream(video, userVideoStream)
        })
    })

    socket.on('user-connected', userId =>{
        connectToNewUser(userId, stream)
    })
}).catch(error => {
    console.error('Error accessing media devices:', error);
    // Handle error (e.g., show an error message to the user)
});



myPeer.on('open', id => {
    socket.emit('join-room', ROOM_ID, id);
});

function addVideoStream(video, stream) {
    video.srcObject = stream;
    video.addEventListener('loadedmetadata', () => {
        video.play();
    });
    videoGrid.append(video);
}

function connectToNewUser(userId, stream){
    const call = myPeer.call(userId, stream)
    const video = documents.createElement('video') 
    call.on('stream', userVideoStream =>{        
        addVideoStream(video, userVideoStream)
    })
    call.on('close', () => {
        VideoColorSpace.remove()
    })
}
