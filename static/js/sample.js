/* Audio API */
const audioElem = document.querySelector('#audio-1');
const playElem = document.querySelector('#play');
const volUpElem = document.querySelector('#up');
const volDownElem = document.querySelector('#down');

const audioContext = new AudioContext();
const audioDestination = audioContext.destination;

const audioSourceNode = audioContext.createMediaElementSource(audioElem);
const analyser = audioContext.createAnalyser();
const biquadFilterHigh = audioContext.createBiquadFilter();
const biquadFilterBand = audioContext.createBiquadFilter();
const biquadFilterLow = audioContext.createBiquadFilter();
const gainNode = audioContext.createGain();

/* Biquad filter */
/* 0 ~ 24000 */
/* -3.4e+38 ~ 1541.27 */
biquadFilterHigh.type = 'highshelf';
biquadFilterBand.type = 'peaking';
biquadFilterLow.type = 'lowshelf';
biquadFilterHigh.frequency.value = 3200.0;
biquadFilterBand.frequency.value = 1000.0;
biquadFilterLow.frequency.value = 320.0;
biquadFilterHigh.gain.value = 5;
biquadFilterBand.gain.value = 0;
biquadFilterLow.gain.value = 0;

audioSourceNode
.connect(analyser)
.connect(biquadFilterHigh)
.connect(biquadFilterBand)
.connect(biquadFilterLow)
.connect(gainNode)
.connect(audioDestination);

let playState = false;

/* Canvas */
const canvas = document.querySelector('#canvas');
const canvasContext = canvas.getContext("2d");
canvasContext.clearRect(0, 0, canvas.width, canvas.height);

/* Draw Canvas */
analyser.fftSize = 2048;
const bufferLength = analyser.frequencyBinCount;
const dataArray = new Uint8Array(bufferLength);

const draw = () => {
    var drawVisual = requestAnimationFrame(draw);
    analyser.getByteTimeDomainData(dataArray);

    canvasContext.fillStyle = 'rgb(200, 200, 200)';
    canvasContext.fillRect(0, 0, canvas.width, canvas.height);

    canvasContext.lineWidth = 2;
    canvasContext.strokeStyle = 'rgb(0, 0, 0)';
    canvasContext.beginPath();

    var sliceWidth = canvas.width * 1.0 / bufferLength;
    var x = 0;

    for(var i = 0; i < bufferLength; i++) {
   
        var v = dataArray[i] / 128.0;
        var y = v * canvas.height/2;

        if(i === 0) {
            canvasContext.moveTo(x, y);
        } else {
            canvasContext.lineTo(x, y);
        }

        x += sliceWidth;
    }

    canvasContext.lineTo(canvas.width, canvas.height/2);
    canvasContext.stroke();
};

const play = (ev) => {
    audioContext.resume().then(() => {
        playState = !playState;
        console.log(playState);

        if (playState) {
            audioElem.play();
        } else {
            audioElem.pause();
        }

        draw();
    });
};

const volumeUp = (ev) => {
    if (gainNode.gain.value > 2) {
        gainNode.gain.value = 2;
    } else {
        gainNode.gain.value += 0.2;
    }
};

const volumeDown = (ev) => {
    if (gainNode.gain.value < 0) {
        gainNode.gain.value = 0;
    } else {
        gainNode.gain.value -= 0.2;
    }
}

playElem.addEventListener('click', play);
volUpElem.addEventListener('click', volumeUp);
volDownElem.addEventListener('click', volumeDown);