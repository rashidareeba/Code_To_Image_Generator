document.getElementById('codeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const resultDiv = document.getElementById('result');
    const image = document.getElementById('outputImage');
    const downloadLink = document.getElementById('downloadLink');
    const generateBtn = document.querySelector('.generate-btn');
    
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Server error');
        
        const data = await response.json();
        
        image.src = data.image_url;
        image.onload = () => {
            resultDiv.classList.remove('hidden');
            downloadLink.href = data.download_url;
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Image';
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        };
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating image. Please try again.');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Image';
    }
});