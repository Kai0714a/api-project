// static/index.js

const form = document.getElementById('download-form');
const progressBar = document.getElementById('download-progress');
const progressStatus = document.getElementById('progress-status');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const url = formData.get('url');
    const quality = formData.get('quality');

    try {
        const response = await fetch('/download', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to download video');
        }

        // Reset progress bar
        progressBar.value = 0;
        progressStatus.textContent = 'Downloading...';
        progressBar.style.backgroundColor = '#4CAF50'; // Green color

        const reader = response.body.getReader();
        const contentLength = +response.headers.get('Content-Length');
        let receivedLength = 0;
        const chunks = [];

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            chunks.push(value);
            receivedLength += value.length;
            progressBar.value = (receivedLength / contentLength) * 100;
        }

        // Combine chunks into a single Uint8Array
        const chunksAll = new Uint8Array(receivedLength);
        let position = 0;
        for (const chunk of chunks) {
            chunksAll.set(chunk, position);
            position += chunk.length;
        }

        // Create blob from chunks and download
        const blob = new Blob([chunksAll]);
        const urlObject = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = urlObject;
        link.download = `${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        progressStatus.textContent = 'Download complete!';
    } catch (error) {
        console.error('Download error:', error);
        progressStatus.textContent = 'Download failed. Please try again.';
        progressBar.style.backgroundColor = '#FF5722'; // Orange color indicating failure
    }
});
