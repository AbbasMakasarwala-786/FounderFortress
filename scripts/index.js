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
  console.log("🔥 USING NEW STREAMING CODE VERSION 2.0 🔥");

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
    console.log('Making request to /ask endpoint...');
    output.textContent = '🤔 Thinking...';
    
    const res = await fetch('http://127.0.0.1:8000/ask', {
      method: 'POST',
      body: formData
    });

    console.log('Response received:', {
      status: res.status,
      statusText: res.statusText,
      contentType: res.headers.get('content-type'),
      headers: Object.fromEntries(res.headers.entries())
    });

    const contentType = res.headers.get('content-type') || '';
    console.log('Content-Type:', contentType);

    if (!res.ok) {
      // Handle error responses (e.g., 404, 500)
      if (contentType.includes('application/json')) {
        try {
          const data = await res.json();
          output.textContent = `❌ Error: ${data.detail || 'Unknown error'}`;
        } catch (e) {
          console.error('Failed to parse JSON error response:', e);
          const errorText = await res.text();
          output.textContent = `❌ Error: ${errorText || 'Invalid error response'}`;
        }
      } else {
        const errorText = await res.text();
        output.textContent = `❌ Error: ${errorText || 'Unknown error'}`;
      }
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    // Handle successful response
    if (contentType.includes('application/json')) {
      console.warn('Backend returned JSON instead of streaming!');
      try {
        const data = await res.json();
        output.textContent = data.result || data.message || 'No result';
      } catch (e) {
        console.error('Failed to parse JSON:', e);
        const text = await res.text(); // Note: Body already consumed, adjust below if needed
        output.textContent = '⚠️ Invalid JSON response';
        console.log('Response body:', text);
      }
      return;
    }

    // Handle streaming response (text/plain)
    console.log('Processing streaming response...');
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    output.textContent = '';
    let fullResponse = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        console.log('Stream ended');
        break;
      }
      const chunk = decoder.decode(value, { stream: true });
      console.log('Received chunk:', chunk);
      fullResponse += chunk;
      const displayText = fullResponse.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
      output.textContent = displayText || '...';
      output.scrollTop = output.scrollHeight;
    }

    const finalText = fullResponse.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
    output.textContent = finalText || '⚠️ No answer returned.';
    console.log('Final response:', finalText);

  } catch (err) {
    console.error('Ask failed:', err);
    console.error('Error stack:', err.stack);
    output.textContent = `❌ Failed to get answer: ${err.message}`;
  }
}
// In index.js
function toggleMode() {
  document.body.classList.toggle('dark-mode'); // Example implementation
}

// Assuming the button has an id, e.g., "modeButton"
const modeButton = document.getElementById('modeButton');
if (modeButton) {
  modeButton.addEventListener('click', toggleMode);
} else {
  console.error('Button with id "modeButton" not found.');
}