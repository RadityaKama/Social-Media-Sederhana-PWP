document.addEventListener('DOMContentLoaded', () => {
    ['loginForm', 'regForm'].forEach(id => {
        const f = document.getElementById(id);
        if(f) f.addEventListener('submit', async(e) => {
            e.preventDefault();
            const res = await fetch('/api/auth', {
                method: 'POST', headers: {'Content-Type':'application/json'},
                body: JSON.stringify(Object.fromEntries(new FormData(f)))
            });
            const d = await res.json();
            if(d.status === 'success') {
                if(id === 'regForm') { Swal.fire('Berhasil', 'Akun dibuat', 'success'); location.reload(); }
                else window.location.href = '/feed';
            } else Swal.fire('Gagal', d.message, 'error');
        });
    });

    const pf = document.getElementById('postForm');
    if(pf) pf.addEventListener('submit', async(e) => {
        e.preventDefault();
        await fetch('/api/post', {method: 'POST', body: new FormData(pf)});
        window.location.reload();
    });

    const nf = document.getElementById('newsForm');
    if(nf) nf.addEventListener('submit', async(e) => {
        e.preventDefault();
        await fetch('/api/post', {method: 'POST', body: new FormData(nf)});
        Swal.fire('Terbit', 'Berita disiarkan', 'success');
        nf.reset();
    });

    const ef = document.getElementById('editForm');
    if(ef) ef.addEventListener('submit', async(e) => {
        e.preventDefault();
        await fetch('/api/act', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({...Object.fromEntries(new FormData(ef)), type: 'update_profile'})
        });
        window.location.reload();
    });
});

async function doAct(type, id) {
    const body = {type: type};
    if(type === 'like') body.pid = id;
    if(type === 'follow') body.tid = id;
    if(type === 'trend') body.tag = document.getElementById('trendTag').value;
    const res = await fetch('/api/act', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)});
    if((await res.json()).status.includes('success') || (await res.json()).status.includes('liked')) window.location.reload();
}

const msgBox = document.getElementById('msgBox');
const socket = io();
const myUid = parseInt(document.body.getAttribute('data-uid')); 

if(msgBox) {
    socket.emit('join', {room: msgBox.dataset.room});
    msgBox.scrollTop = msgBox.scrollHeight;
    
    socket.on('receive_message', (data) => {
        const row = document.createElement('div');
        row.className = `msg-row ${data.sender_id == myUid ? 'row-me' : 'row-you'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `msg-bubble ${data.sender_id == myUid ? 'bubble-me' : 'bubble-you'}`;
        bubble.innerText = data.msg;
        
        row.appendChild(bubble);
        msgBox.appendChild(row);
        msgBox.scrollTop = msgBox.scrollHeight;
    });
}

function sendMsg(rcvId) {
    const inp = document.getElementById('msgIn');
    if(!inp.value.trim()) return;
    socket.emit('send_message', {message: inp.value, receiver_id: rcvId, room: msgBox.dataset.room});
    inp.value = '';
}

const msgIn = document.getElementById('msgIn');
if(msgIn) {
    msgIn.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            const btn = document.querySelector('.input-paper button');
            if(btn) btn.click();
        }
    });
}