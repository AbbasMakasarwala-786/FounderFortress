let currentDocId = null;

const fileInput = document.getElementById('fileInput');
const docStatus = document.getElementById('docStatus');
const output = document.getElementById('output');
const questionInput = document.getElementById('questionInput');

fileInput.addEventListener('change', async (event) => {
  const file = event.target.files[0];

  if (!file) {
    docStatus.textContent = '⚠️ No file selected.';
    docStatus.classList.add('error');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('http://127.0.0.1:8000/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (data.doc_id) {
      currentDocId = data.doc_id;
      docStatus.textContent = `📄 Uploaded: ${data.doc_id}`;
      docStatus.classList.remove('error');
    } else {
      currentDocId = null;
      docStatus.textContent = '❌ No doc_id returned from server';
      docStatus.classList.add('error');
    }
  } catch (err) {
    console.error('Upload failed:', err);
    currentDocId = null;
    docStatus.textContent = '❌ Upload failed';
    docStatus.classList.add('error');
  }
});

async function askQuestion() {
  const question = questionInput.value.trim();

  if (!currentDocId) {
    output.textContent = '⚠️ Upload a document first.';
    return;
  }

  if (!question) {
    output.textContent = '⚠️ Enter a question first.';
    return;
  }

  const formData = new FormData();
  formData.append('doc_id', currentDocId);
  formData.append('question', question);

  try {
    const res = await fetch('http://127.0.0.1:8000/ask', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    output.textContent = data.result || '⚠️ No answer returned.';
  } catch (err) {
    console.error('Ask failed:', err);
    output.textContent = '❌ Failed to get answer';
  }
}

function toggleMode() {
  document.body.classList.toggle('dark-mode');
}
