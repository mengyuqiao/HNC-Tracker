/**
 * camera.js — handles camera capture and file upload for both food and med screens.
 * Call initCamera() after including this script.
 */
function initCamera(mode) {
  const video       = document.getElementById('cameraVideo');
  const canvas      = document.getElementById('cameraCanvas');
  const cameraWrap  = document.getElementById('cameraWrap');
  const previewWrap = document.getElementById('previewWrap');
  const previewImg  = document.getElementById('previewImg');
  const captureBtn  = document.getElementById('captureBtn');
  const uploadBtn   = document.getElementById('uploadBtn');
  const retakeBtn   = document.getElementById('retakeBtn');
  const photoInput  = document.getElementById('photoInput');
  const captureCtrl = document.getElementById('captureControls');
  const confirmCtrl = document.getElementById('confirmControls');
  const form        = document.getElementById('uploadForm');

  let stream = null;
  let capturedBlob = null;

  // ── Start camera ──────────────────────────────────────────────────────────
  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 960 } },
        audio: false
      });
      video.srcObject = stream;
    } catch (err) {
      // Fallback: use file input if camera access fails
      console.warn('Camera not available, falling back to file input.', err);
      cameraWrap.style.display = 'none';
      captureBtn.style.display = 'none';
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
  }

  // ── Capture from live video ───────────────────────────────────────────────
  function captureFrame() {
    canvas.width  = video.videoWidth  || 1280;
    canvas.height = video.videoHeight || 960;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
      capturedBlob = blob;
      const url = URL.createObjectURL(blob);
      previewImg.src = url;
      cameraWrap.style.display = 'none';
      previewWrap.style.display = 'block';
      captureCtrl.style.display = 'none';
      confirmCtrl.style.display = 'block';
      stopCamera();
    }, 'image/jpeg', 0.90);
  }

  // ── Show file from library ────────────────────────────────────────────────
  function showFilePreview(file) {
    capturedBlob = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    cameraWrap.style.display = 'none';
    previewWrap.style.display = 'block';
    captureCtrl.style.display = 'none';
    confirmCtrl.style.display = 'block';
    stopCamera();
  }

  // ── Retake ────────────────────────────────────────────────────────────────
  function retake() {
    capturedBlob = null;
    previewImg.src = '';
    cameraWrap.style.display = 'block';
    previewWrap.style.display = 'none';
    captureCtrl.style.display = 'block';
    confirmCtrl.style.display = 'none';
    startCamera();
  }

  // ── Form submit — attach blob as file ─────────────────────────────────────
  form.addEventListener('submit', function(e) {
    if (!capturedBlob) return; // let normal file input proceed if no capture
    e.preventDefault();

    const dt   = new DataTransfer();
    const name = `${mode}_${Date.now()}.jpg`;
    const file = capturedBlob instanceof File
      ? capturedBlob
      : new File([capturedBlob], name, { type: 'image/jpeg' });
    dt.items.add(file);
    photoInput.files = dt.files;

    // Show loading state
    const submitBtn = confirmCtrl.querySelector('button[type=submit]');
    submitBtn.textContent = 'Analyzing…';
    submitBtn.disabled = true;

    form.submit();
  });

  // ── Event bindings ────────────────────────────────────────────────────────
  if (captureBtn) captureBtn.addEventListener('click', captureFrame);
  if (retakeBtn)  retakeBtn.addEventListener('click', retake);
  if (uploadBtn)  uploadBtn.addEventListener('click', () => photoInput.click());

  photoInput.addEventListener('change', () => {
    if (photoInput.files[0]) showFilePreview(photoInput.files[0]);
  });

  // Start camera on load
  startCamera();
}
