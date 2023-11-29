
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const promptInput = document.getElementById('promptInput');
  const submitButton = document.getElementById('submitButton');
  let isDrawing = false;
  let brushColor = '#000000';
  let lastX = 0;
  let lastY = 0;

  canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    [lastX, lastY] = [e.offsetX, e.offsetY];
  });

  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', () => isDrawing = false);
  canvas.addEventListener('mouseout', () => isDrawing = false);

  function draw(e) {
    if (!isDrawing) return;
    ctx.strokeStyle = brushColor;
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
    [lastX, lastY] = [e.offsetX, e.offsetY];
  }

  // Change the brush color
  function changeColor(color) {
    brushColor = color;
  }

  // Eraser tool
  function eraser() {
    brushColor = '#FFFFFF'; // Assuming the canvas background is white
  }

  // Submit button event listener
  submitButton.addEventListener('click', function() {
    const dataURL = canvas.toDataURL('image/png');
    const promptText = promptInput.value;
    // Here you would call the Stable Diffusion API with dataURL and promptText
    // For now, we'll just log them to the console
    console.log('Image Data URL:', dataURL);
    console.log('Prompt:', promptText);

    // Placeholder for the API call
    callStableDiffusionApi(dataURL, promptText);
  });

  // Function to call the Stable Diffusion API - this is where you'd implement the real call
  function callStableDiffusionApi(imageData, prompt) {
    // Implement API interaction here and update the UI with the response
    console.log('Calling Stable Diffusion API...');
  }