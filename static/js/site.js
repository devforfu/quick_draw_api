/* Canvas Drawing.
*
* Taken and adapted from:
*   https://stackoverflow.com/questions/2368784/draw-on-html5-canvas-using-a-mouse
*
* */

let canvas, ctx, flag = false;
let prevX = 0,
    currX = 0,
    prevY = 0,
    currY = 0,
    width = 0,
    height = 0,
    dotFlag = false,
    stroke = 'black',
    lw = 2;


function init() {
    canvas = document.getElementById('doodle');
    ctx = canvas.getContext('2d');
    width = canvas.width;
    height = canvas.height;
    erase();

    canvas.addEventListener('mousemove', function(e) {
       findXY('move', e)
    }, false);

    canvas.addEventListener('mousedown', function(e) {
       findXY('down', e)
    }, false);

    canvas.addEventListener('mouseup', function(e) {
       findXY('up', e)
    }, false);

    canvas.addEventListener('mouseout', function(e) {
       findXY('out', e)
    }, false);
}


function findXY(action, e) {
    if (action === 'down') {
        prevX = currX;
        prevY = currY;
        currX = e.clientX - canvas.offsetLeft;
        currY = e.clientY - canvas.offsetTop;

        flag = true;
        dotFlag = true;

        if (dotFlag) {
            ctx.beginPath();
            ctx.fillStyle = stroke;
            ctx.fillRect(currX, currY, 2, 2);
            ctx.closePath();
            dotFlag = false;
        }
    }
    if (action === 'up' || action === 'out') {
        if (flag) {
            sendToServer(canvas.toDataURL());
        }
        flag = false;
    }
    if (action === 'move') {
        if (flag) {
            prevX = currX;
            prevY = currY;
            currX = e.clientX - canvas.offsetLeft;
            currY = e.clientY - canvas.offsetTop;
            draw();
        }
    }
}


function draw() {
    ctx.beginPath();
    ctx.moveTo(prevX, prevY);
    ctx.lineTo(currX, currY);
    ctx.strokeStyle = stroke;
    ctx.lineWidth = lw;
    ctx.stroke();
    ctx.closePath();
}


function erase() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);
}


function sendToServer(data) {
    console.log(document.getElementById('slow').checked);

    const url = document.location.href + 'send';
    const promise = fetch(url, {
        method: 'post',
        headers: {
            'Content-Type': 'applicatoin/json; charset=utf-8'
        },
        body:JSON.stringify({
            imgBase64: data,
            slow: document.getElementById('slow').checked
        })
    });

    promise.then(r => { return r.json() }).then(data => {
        const node = document.getElementById('response');
        while (node.firstChild) {
            node.removeChild(node.firstChild);
        }
        const preds = data['predictions'];
        for (let i = 0; i < 10; i++) {
            const item = preds[i];
            const childNode = document.createElement('li');
            const textNode = document.createTextNode(`${item[0]} (loss: ${item[1]})`);
            childNode.append(textNode);
            node.appendChild(childNode);
        }
    });
}