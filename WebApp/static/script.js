const canvas = document.getElementById("emotionCanvas");
const ctx = canvas.getContext("2d");
const cx = canvas.width / 2;
const cy = canvas.height / 2;
const r = 250;

let startTime = null;
let locked = false;
let lockedAngle = 0;
let currentAngle = 0;

// Emotion labels from Russell's circumplex model
const emotions = [
  "Pleased", "Glad", "Happy", "Delighted", "Excited", "Astonished", "Aroused",
  "Tense", "Alarmed", "Afraid", "Angry", "Annoyed", "Distressed", "Frustrated",
  "Miserable", "Sad", "Gloomy", "Depressed", "Bored", "Droopy", "Tired", "Sleepy",
  "Calm", "Relaxed", "Satisfied", "At Ease", "Content", "Serene"
];

const angleStep = 360 / emotions.length;
const emotionMap = emotions.map((e, i) => [e, i * angleStep]);

function drawMeter(angle) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw gradient background circle
  const gradient = ctx.createRadialGradient(cx, cy, 5, cx, cy, r);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
  gradient.addColorStop(1, 'rgba(230, 240, 255, 0.5)');
  
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.fillStyle = gradient;
  ctx.fill();
  
  // Draw outer ring
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.strokeStyle = "rgba(106, 17, 203, 0.3)";
  ctx.lineWidth = 2;
  ctx.stroke();
  
  // Draw quadrant lines
  ctx.strokeStyle = "rgba(106, 17, 203, 0.15)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i++) {
    const rad = (i * 90 * Math.PI) / 180;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + r * Math.cos(rad), cy + r * Math.sin(rad));
    ctx.stroke();
  }

  // Draw axis labels
  ctx.font = "bold 18px 'Quicksand', sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  
  // Pleasure-Arousal labels
  ctx.fillStyle = "#4caf50";
  ctx.fillText("High Pleasure", cx + r * 0.8, cy);
  ctx.fillText("Low Pleasure", cx - r * 0.8, cy);
  ctx.fillText("High Arousal", cx, cy - r * 0.8);
  ctx.fillText("Low Arousal", cx, cy + r * 0.8);

  // Emotion labels
  ctx.font = "14px 'Poppins', sans-serif";
  ctx.fillStyle = "#333";
  
  emotionMap.forEach(([emotion, ang]) => {
    const rad = (ang * Math.PI) / 180;
    const textRadius = r - 40;
    const x = cx + textRadius * Math.cos(rad);
    const y = cy + textRadius * Math.sin(rad);
    
    // Highlight the label near the current angle
    const angleDiff = Math.abs(ang - currentAngle);
    const minAngleDiff = Math.min(angleDiff, 360 - angleDiff);
    
    if (minAngleDiff < 15) {
      ctx.fillStyle = "#6a11cb";
      ctx.font = "bold 15px 'Poppins', sans-serif";
    } else {
      ctx.fillStyle = "#555";
    }
    
    // Adjust text alignment based on position
    ctx.textAlign = Math.abs(Math.cos(rad)) > 0.5 ? "center" : (Math.cos(rad) > 0 ? "left" : "right");
    ctx.textBaseline = Math.abs(Math.sin(rad)) > 0.5 ? "middle" : (Math.sin(rad) > 0 ? "top" : "bottom");
    
    ctx.fillText(emotion, x, y);
  });

  // Draw needle
  const rad = (angle * Math.PI) / 180;
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + (r - 20) * Math.cos(rad), cy + (r - 20) * Math.sin(rad));
  ctx.strokeStyle = "#ff6b6b";
  ctx.lineWidth = 4;
  ctx.lineCap = "round";
  ctx.shadowBlur = 10;
  ctx.shadowColor = "rgba(255, 107, 107, 0.5)";
  ctx.stroke();
  ctx.shadowBlur = 0;
  
  // Draw needle head
  ctx.beginPath();
  ctx.arc(cx + (r - 20) * Math.cos(rad), cy + (r - 20) * Math.sin(rad), 8, 0, 2 * Math.PI);
  ctx.fillStyle = "#ff6b6b";
  ctx.fill();
}

// Initialize the meter
drawMeter(0);

canvas.addEventListener("mousemove", (e) => {
  if (locked) return;

  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left - cx;
  const y = e.clientY - rect.top - cy;
  const angle = (Math.atan2(y, x) * 180) / Math.PI;
  const fixed = (angle + 360) % 360;
  currentAngle = fixed;
  drawMeter(currentAngle);
});

canvas.addEventListener("mousedown", () => {
  startTime = Date.now();
  locked = true;
  lockedAngle = currentAngle;
  drawMeter(lockedAngle);
  
  // Add pulse animation to center circle
  const centerCircle = document.querySelector('.center-circle');
  centerCircle.style.animation = 'pulse 0.5s';
  setTimeout(() => {
    centerCircle.style.animation = '';
  }, 500);
});

canvas.addEventListener("mouseup", () => {
  const holdTime = (Date.now() - startTime) / 1000;
  
  fetch("/process", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ angle: lockedAngle, hold_time: holdTime })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("emotion-display").textContent = data.emotion;
    
    const certaintyDisplay = document.getElementById("certainty-display");
    certaintyDisplay.textContent = data.certainty_label;
    certaintyDisplay.className = "certainty-result";
    certaintyDisplay.classList.add(`certainty-${data.certainty_label.replace(/\s+/g, '-').toLowerCase()}`);
  });
  
  locked = false;
});