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

    const msgBox = document.getElementById('msgBox');
    const myUid = parseInt(document.body.getAttribute('data-uid')); 
    
    if(msgBox) {
        const socket = io();
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

        window.sendMsg = function(rcvId) {
            const inp = document.getElementById('msgIn');
            if(!inp.value.trim()) return;
            socket.emit('send_message', {message: inp.value, receiver_id: rcvId, room: msgBox.dataset.room});
            inp.value = '';
        };

        const msgIn = document.getElementById('msgIn');
        if(msgIn) {
            msgIn.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    window.sendMsg(parseInt(msgBox.dataset.room.split('_').find(id => id != myUid)));
                }
            });
        }
    }
});

async function doLike(pid, el) {
    const icon = el.querySelector('i');
    const cnt = el.querySelector('span');
    if(icon.classList.contains('fa-regular')) {
        icon.classList.remove('fa-regular');
        icon.classList.add('fa-solid', 'liked');
        cnt.innerText = parseInt(cnt.innerText) + 1;
    } else {
        icon.classList.remove('fa-solid', 'liked');
        icon.classList.add('fa-regular');
        cnt.innerText = parseInt(cnt.innerText) - 1;
    }
    await fetch('/api/act', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({type: 'like', pid: pid})});
}

async function doAct(type, id) {
    const body = {type: type};
    if(type === 'follow') body.tid = id;
    if(type === 'trend') body.tag = document.getElementById('trendTag').value;
    const res = await fetch('/api/act', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)});
    if((await res.json()).status.includes('success')) window.location.reload();
}

function openLightbox(url) {
    const lb = document.getElementById('lightbox');
    const ct = lb.querySelector('.lightbox-content');
    ct.style.backgroundImage = url;
    lb.classList.add('active');
}

let activePostId = null;
async function openComments(pid) {
    activePostId = pid;
    const modal = document.getElementById('commentModal');
    const list = document.getElementById('commentList');
    list.innerHTML = '<div style="text-align:center; padding:20px;">Memuat...</div>';
    modal.classList.add('active');
    
    try {
        const res = await fetch(`/api/get_comments/${pid}`);
        const comments = await res.json();
        list.innerHTML = '';
        if(comments.length === 0) list.innerHTML = '<div style="text-align:center; color:#999; margin-top:20px;">Belum ada diskusi.</div>';
        comments.forEach(c => {
            // PENTING: Render isi_komentar
            list.innerHTML += `<div class="comment-item"><b>${c.nama} <small style="font-weight:normal;color:#999;">@${c.username}</small></b><p>${c.isi_komentar}</p></div>`;
        });
    } catch(err) { list.innerHTML = '<div style="text-align:center; color:red;">Gagal.</div>'; }
}

document.getElementById('sendCommentBtn').addEventListener('click', async () => {
    const inp = document.getElementById('commentInput');
    if(!inp.value.trim()) return;
    await fetch('/api/comment', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({pid: activePostId, text: inp.value})
    });
    inp.value = '';
    openComments(activePostId);
});