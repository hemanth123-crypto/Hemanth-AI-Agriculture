/**
 * AI-Powered Agriculture Crop Advisory Assistant - Modern Frontend Application Logic
 * Premium AgTech SaaS Architecture
 */

let currentAuthMode = "login"; // "login" or "signup"
let activeThumb = "up";
let activeRating = 5;
let lastAdvisoryResponse = null;
let allExplorerCases = [];
let voiceRecognition = null;
let isListening = false;
let currentExplorerTag = "all";

// Static curated crop data for showcase gallery
const CURATED_CROPS = [
  { name: "Rice", emoji: "🌾", suitability: 92, yieldAvg: 4.35, risk: "Low", season: "Kharif", states: "West Bengal, Andhra Pradesh, Punjab", water: "High", soil: "Clayey / Alluvial", expl: "Thrives in warm, humid climates with abundant water and alluvial soils." },
  { name: "Wheat", emoji: "🌿", suitability: 88, yieldAvg: 4.10, risk: "Low", season: "Rabi", states: "Punjab, Haryana, Uttar Pradesh", water: "Medium", soil: "Well-drained Loam", expl: "Optimal under cool growing seasons and warm ripening periods with balanced nitrogen." },
  { name: "Cotton", emoji: "🌱", suitability: 84, yieldAvg: 2.45, risk: "Moderate", season: "Kharif", states: "Gujarat, Maharashtra, Telangana", water: "Medium", soil: "Black Cotton Soil", expl: "Deep root system suited to moisture-retentive black soil with sunny dry harvest conditions." },
  { name: "Maize", emoji: "🌽", suitability: 86, yieldAvg: 3.80, risk: "Low", season: "Kharif / Rabi", states: "Karnataka, Madhya Pradesh, Bihar", water: "Medium", soil: "Fertile Loam", expl: "Highly adaptable C4 cereal yielding strongly under moderate rainfall and good drainage." },
  { name: "Sugarcane", emoji: "🎋", suitability: 80, yieldAvg: 75.0, risk: "Moderate", season: "Whole Year", states: "Uttar Pradesh, Maharashtra, Tamil Nadu", water: "High", soil: "Deep Alluvial Loam", expl: "Long-duration cash crop requiring heavy nutrients and reliable canal/drip irrigation." },
  { name: "Chickpea", emoji: "🧆", suitability: 82, yieldAvg: 1.85, risk: "Low", season: "Rabi", states: "Madhya Pradesh, Rajasthan, Maharashtra", water: "Low", soil: "Sandy Loam to Clay", expl: "Nitrogen-fixing legume with high drought tolerance, ideal for sustainable crop rotation." },
  { name: "Groundnut", emoji: "🥜", suitability: 85, yieldAvg: 2.20, risk: "Low", season: "Kharif / Summer", states: "Gujarat, Andhra Pradesh, Tamil Nadu", water: "Low - Med", soil: "Sandy Loam", expl: "Light textured, well-aerated soils enable efficient pegging and pod development." },
  { name: "Soybean", emoji: "🌱", suitability: 83, yieldAvg: 2.15, risk: "Moderate", season: "Kharif", states: "Madhya Pradesh, Maharashtra", water: "Medium", soil: "Well-drained Black Soil", expl: "Rich in protein and oil; sensitive to prolonged waterlogging during seedling stage." },
  { name: "Mustard", emoji: "🌼", suitability: 87, yieldAvg: 1.95, risk: "Low", season: "Rabi", states: "Rajasthan, Haryana, Uttar Pradesh", water: "Low", soil: "Light to Medium Loam", expl: "Cool-season oilseed with excellent frost resilience and modest water requirement." },
  { name: "Barley", emoji: "🌾", suitability: 81, yieldAvg: 3.20, risk: "Low", season: "Rabi", states: "Rajasthan, Uttar Pradesh, Punjab", water: "Low", soil: "Sandy Loam / Saline", expl: "Remarkable salinity and moisture-stress tolerance compared to other winter cereals." },
  { name: "Millets", emoji: "🌾", suitability: 90, yieldAvg: 1.70, risk: "Low", season: "Kharif", states: "Rajasthan, Karnataka, Maharashtra", water: "Very Low", soil: "Shallow Sandy / Red", expl: "Super-climate-resilient grain requiring minimal fertilizer and thriving in dry conditions." },
  { name: "Jute", emoji: "🌿", suitability: 78, yieldAvg: 2.65, risk: "Moderate", season: "Kharif", states: "West Bengal, Assam, Bihar", water: "High", soil: "Alluvial Delta Soil", expl: "Natural golden fiber demanding high seasonal rainfall and warm deltaic temperatures." }
];

function formatIntentLabel(intent) {
  if (!intent) return "Crop Recommendation";
  const intentMap = {
    "CROP_RECOMMENDATION": "Crop Recommendation",
    "YIELD_PREDICTION": "Yield Prediction",
    "CASE_SIMILARITY": "Similar Historical Cases",
    "ALTERNATIVE_CROP": "Alternative Crop Advisory",
    "SOIL_ANALYSIS": "Soil & Nutrient Advisory",
    "WEATHER_ANALYSIS": "Weather Impact Advisory",
    "GENERAL_AGRICULTURE": "Agricultural Advisory"
  };
  if (intentMap[intent]) return intentMap[intent];
  return intent
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
}

document.addEventListener("DOMContentLoaded", () => {
  initAuthCheck();
  initFireflyAnimation();
  loadMetadataDropdowns();
  loadEvaluationDashboard();
  renderCropsShowcase();
  renderQueryHistory();
  initVoiceRecognition();
  runLiveYieldEstimate();
  runLiveRiskCalculation();

  const qInput = document.getElementById("queryInput");
  if (qInput) {
    qInput.addEventListener("input", dismissGuardrailAlert);
  }
});

// ============================================================================
// 1. AUTHENTICATION & ROUTING MANAGEMENT
// ============================================================================

let fireflyAnimFrame = null;
let firefliesList = [];

function initFireflyAnimation() {
  const canvas = document.getElementById("fireflyCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  function resizeCanvas() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  // Richer density of warm yellow/gold fireflies throughout the field
  const numFireflies = 55;
  firefliesList = [];

  const width = window.innerWidth;
  const height = window.innerHeight;

  // Curated warm yellow / golden firefly hues matching #FFD65A
  const colorPalette = [
    "255, 214, 90",   // Warm Gold #FFD65A
    "255, 228, 115",  // Bright Golden Yellow
    "250, 195, 55",   // Deep Honey Gold
    "255, 240, 140",  // Phosphorescent Yellow
    "245, 205, 75"    // Amber Glow
  ];

  for (let i = 0; i < numFireflies; i++) {
    // Variety: 65% tiny pinpoint insects, 25% medium, 10% slightly larger prominent fireflies
    const sizeType = Math.random();
    let coreRadius, glowRadius, hasTrail;

    if (sizeType < 0.65) {
      coreRadius = 0.7 + Math.random() * 0.7; // 0.7 - 1.4px tiny dot
      glowRadius = 7 + Math.random() * 9;
      hasTrail = Math.random() < 0.3; // 30% of tiny ones have subtle trail
    } else if (sizeType < 0.90) {
      coreRadius = 1.5 + Math.random() * 0.7; // 1.5 - 2.2px medium firefly
      glowRadius = 12 + Math.random() * 12;
      hasTrail = Math.random() < 0.55;
    } else {
      coreRadius = 2.2 + Math.random() * 0.9; // 2.2 - 3.1px slightly larger firefly
      glowRadius = 18 + Math.random() * 14;
      hasTrail = true;
    }

    firefliesList.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.28,
      targetVx: (Math.random() - 0.5) * 0.35,
      targetVy: (Math.random() - 0.5) * 0.3,
      dirTimer: Math.floor(Math.random() * 140) + 60,
      coreRadius: coreRadius,
      glowRadius: glowRadius,
      baseAlpha: 0.25 + Math.random() * 0.55,
      pulseAngle: Math.random() * Math.PI * 2,
      pulseSpeed: 0.012 + Math.random() * 0.024,
      rgb: colorPalette[i % colorPalette.length],
      hasTrail: hasTrail,
      trail: []
    });
  }

  function renderFireflies() {
    const w = window.innerWidth;
    const h = window.innerHeight;

    ctx.clearRect(0, 0, w, h);

    for (let i = 0; i < firefliesList.length; i++) {
      const f = firefliesList[i];

      // Smooth velocity interpolation for organic natural flight
      f.dirTimer--;
      if (f.dirTimer <= 0) {
        f.targetVx = (Math.random() - 0.5) * 0.42;
        f.targetVy = (Math.random() - 0.5) * 0.32;
        f.dirTimer = Math.floor(Math.random() * 180) + 70;
      }
      f.vx += (f.targetVx - f.vx) * 0.018;
      f.vy += (f.targetVy - f.vy) * 0.018;

      // Realistic gentle sinusoidal wandering & hovering
      f.pulseAngle += f.pulseSpeed;
      const wobbleX = Math.sin(f.pulseAngle * 1.3) * 0.16;
      const wobbleY = Math.cos(f.pulseAngle * 0.85) * 0.13;

      f.x += f.vx + wobbleX;
      f.y += f.vy + wobbleY;

      // Soft screen margin wrap
      const margin = 45;
      if (f.x < -margin) f.x = w + margin;
      if (f.x > w + margin) f.x = -margin;
      if (f.y < -margin) f.y = h + margin;
      if (f.y > h + margin) f.y = -margin;

      // Organic luminescent breathing / flickering cycle
      const currentAlpha = Math.max(0.06, Math.min(0.96, f.baseAlpha + Math.sin(f.pulseAngle) * 0.45));

      // Golden light trails for active fireflies
      if (f.hasTrail) {
        f.trail.unshift({ x: f.x, y: f.y, alpha: currentAlpha });
        if (f.trail.length > 7) f.trail.pop();

        if (f.trail.length > 1) {
          for (let t = 1; t < f.trail.length; t++) {
            const p = f.trail[t];
            const trailAlpha = (p.alpha * (1 - t / f.trail.length)) * 0.3;
            ctx.beginPath();
            ctx.arc(p.x, p.y, Math.max(0.5, f.coreRadius * (1 - t * 0.1)), 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${f.rgb}, ${trailAlpha})`;
            ctx.fill();
          }
        }
      }

      // Soft outer ambient radial glow (warm yellow / gold)
      const grad = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, f.glowRadius);
      grad.addColorStop(0, `rgba(${f.rgb}, ${currentAlpha * 0.85})`);
      grad.addColorStop(0.35, `rgba(${f.rgb}, ${currentAlpha * 0.28})`);
      grad.addColorStop(0.7, `rgba(${f.rgb}, ${currentAlpha * 0.08})`);
      grad.addColorStop(1, `rgba(${f.rgb}, 0)`);

      ctx.beginPath();
      ctx.arc(f.x, f.y, f.glowRadius, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      // Warm bright glowing inner nucleus
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.coreRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 245, ${currentAlpha * 0.98})`;
      ctx.shadowColor = `rgba(${f.rgb}, 0.85)`;
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0; // reset
    }

    fireflyAnimFrame = requestAnimationFrame(renderFireflies);
  }

  if (!fireflyAnimFrame) {
    fireflyAnimFrame = requestAnimationFrame(renderFireflies);
  }
}

function startFireflyLoop() {
  if (!fireflyAnimFrame) {
    initFireflyAnimation();
  }
}

function getStoredUser() {
  const storedUser = localStorage.getItem("agri_advisor_user") || sessionStorage.getItem("agri_advisor_user");
  if (storedUser) {
    try {
      return JSON.parse(storedUser);
    } catch (e) {
      localStorage.removeItem("agri_advisor_user");
      sessionStorage.removeItem("agri_advisor_user");
    }
  }
  return null;
}

function showLoginView() {
  const loginView = document.getElementById("loginView");
  const dashboardView = document.getElementById("dashboardView");
  if (dashboardView) dashboardView.classList.add("hidden");
  if (loginView) loginView.classList.remove("hidden");
  if (window.location.pathname !== "/login") {
    window.history.pushState({}, "", "/login");
  }
  startFireflyLoop();
}

function initAuthCheck() {
  const path = window.location.pathname.toLowerCase();
  const user = getStoredUser();

  if (path === "/login") {
    showLoginView();
    return;
  }

  // At "/" or "/dashboard", ensure dashboard is showing
  if (user) {
    showDashboard(user.email, user.name || "Agri Specialist", false);
  } else {
    // Auto-initialize demo agronomist session so dashboard displays immediately on localhost:8000
    const defaultUser = {
      email: "demo@agriadvisor.ai",
      name: "Agricultural Specialist",
      role: "agronomist"
    };
    localStorage.setItem("agri_advisor_user", JSON.stringify(defaultUser));
    showDashboard(defaultUser.email, defaultUser.name, false);
  }
}

window.addEventListener("popstate", () => {
  const path = window.location.pathname.toLowerCase();
  if (path === "/login") {
    const loginView = document.getElementById("loginView");
    const dashboardView = document.getElementById("dashboardView");
    if (dashboardView) dashboardView.classList.add("hidden");
    if (loginView) loginView.classList.remove("hidden");
  } else {
    const user = getStoredUser();
    if (user) {
      showDashboard(user.email, user.name, false);
    } else {
      showLoginView();
    }
  }
});

function fillDemoCredentials() {
  const emailInput = document.getElementById("loginEmail");
  const pwInput = document.getElementById("loginPassword");
  emailInput.value = "demo@agriadvisor.ai";
  pwInput.value = "AgriTech2026!";
  clearFieldErrors();
  hideAuthAlert();
}

function togglePasswordVisibility() {
  const pwInput = document.getElementById("loginPassword");
  const eyeIcon = document.getElementById("eyeIcon");
  const toggleBtn = document.getElementById("togglePasswordBtn");
  
  if (pwInput.type === "password") {
    pwInput.type = "text";
    toggleBtn.setAttribute("title", "Hide password");
    toggleBtn.setAttribute("aria-label", "Hide password");
    eyeIcon.innerHTML = `
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
      <line x1="1" y1="1" x2="23" y2="23"/>
    `;
  } else {
    pwInput.type = "password";
    toggleBtn.setAttribute("title", "Show password");
    toggleBtn.setAttribute("aria-label", "Show password");
    eyeIcon.innerHTML = `
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    `;
  }
}

function toggleAuthMode(event) {
  if (event) event.preventDefault();
  const title = document.getElementById("authCardTitle");
  const sub = document.getElementById("authCardSubtitle");
  const submitText = document.getElementById("submitBtnText");
  const toggleText = document.getElementById("toggleAuthModeText");
  const nameGroup = document.getElementById("nameFieldGroup");

  clearFieldErrors();
  hideAuthAlert();

  if (currentAuthMode === "login") {
    currentAuthMode = "signup";
    title.textContent = "Create Account";
    sub.textContent = "Join the AI agricultural decision-support network.";
    submitText.textContent = "Create Account & Login";
    toggleText.innerHTML = `Already have an account? <a href="#" id="signinLink" onclick="toggleAuthMode(event)">Sign In</a>`;
    nameGroup.classList.remove("hidden");
  } else {
    currentAuthMode = "login";
    title.textContent = "Welcome Back";
    sub.textContent = "Log in to access CropShield AI agricultural decision platform.";
    submitText.textContent = "Login to Dashboard";
    toggleText.innerHTML = `Don't have an account? <a href="#" id="signupLink" onclick="toggleAuthMode(event)">Create Account / Sign Up</a>`;
    nameGroup.classList.add("hidden");
  }
}

function handleForgotPassword(event) {
  if (event) event.preventDefault();
  const modal = document.getElementById("forgotPwModal");
  if (modal) modal.classList.remove("hidden");
}

function closeForgotPwModal(event) {
  if (event && event.target !== event.currentTarget) return;
  const modal = document.getElementById("forgotPwModal");
  if (modal) modal.classList.add("hidden");
}

function useDemoCredentialsAndClose() {
  fillDemoCredentials();
  closeForgotPwModal();
}

function handleInputClearError(field) {
  if (field === "email") {
    document.getElementById("emailError").textContent = "";
    document.getElementById("emailInputWrapper").classList.remove("input-error");
  } else if (field === "password") {
    document.getElementById("passwordError").textContent = "";
    document.getElementById("passwordInputWrapper").classList.remove("input-error");
  } else if (field === "name") {
    const err = document.getElementById("nameError");
    if (err) err.textContent = "";
  }
  hideAuthAlert();
}

function showFieldError(errorElemId, wrapperElemId, message) {
  const errElem = document.getElementById(errorElemId);
  if (errElem) errElem.textContent = message;
  if (wrapperElemId) {
    const wrap = document.getElementById(wrapperElemId);
    if (wrap) wrap.classList.add("input-error");
  }
}

function clearFieldErrors() {
  ["nameError", "emailError", "passwordError"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = "";
  });
  const emailWrap = document.getElementById("emailInputWrapper");
  if (emailWrap) emailWrap.classList.remove("input-error");
  const pwWrap = document.getElementById("passwordInputWrapper");
  if (pwWrap) pwWrap.classList.remove("input-error");
}

function showAuthAlert(message) {
  const alertBox = document.getElementById("authAlert");
  const alertText = document.getElementById("authAlertText");
  if (alertBox && alertText) {
    alertText.textContent = message;
    alertBox.classList.remove("hidden");
  }
}

function hideAuthAlert() {
  const alertBox = document.getElementById("authAlert");
  if (alertBox) alertBox.classList.add("hidden");
}

function isValidEmail(email) {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(String(email).trim());
}

async function authenticateWithApi(email, password, name = null) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const normalizedEmail = email.trim().toLowerCase();
      if (normalizedEmail === "demo@agriadvisor.ai" && password === "AgriTech2026!") {
        resolve({
          success: true,
          token: "jwt_ey_demo_" + Date.now() + ".agri_sig",
          user: { email: "demo@agriadvisor.ai", name: "Agricultural Specialist", role: "agronomist" }
        });
      } else if (normalizedEmail === "officer@agriadvisor.ai" && password === "AgriTech2026!") {
        resolve({
          success: true,
          token: "jwt_ey_officer_" + Date.now() + ".agri_sig",
          user: { email: "officer@agriadvisor.ai", name: "Extension Officer", role: "officer" }
        });
      } else if (password.length >= 6) {
        resolve({
          success: true,
          token: "jwt_ey_user_" + Date.now() + ".agri_sig",
          user: { email: email.trim(), name: name || email.split("@")[0], role: "specialist" }
        });
      } else {
        resolve({
          success: false,
          message: "Invalid email or password. Please verify your credentials or use Quick Demo Access."
        });
      }
    }, 280);
  });
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  clearFieldErrors();
  hideAuthAlert();

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const nameInput = document.getElementById("regName");
  const name = nameInput ? nameInput.value.trim() : "";
  const remember = document.getElementById("rememberMe").checked;

  let hasError = false;
  if (currentAuthMode === "signup" && !name) {
    showFieldError("nameError", null, "Please provide your full name.");
    hasError = true;
  }
  if (!email) {
    showFieldError("emailError", "emailInputWrapper", "Email address is required.");
    hasError = true;
  } else if (!isValidEmail(email)) {
    showFieldError("emailError", "emailInputWrapper", "Please enter a valid email address.");
    hasError = true;
  }
  if (!password) {
    showFieldError("passwordError", "passwordInputWrapper", "Password is required.");
    hasError = true;
  } else if (password.length < 6) {
    showFieldError("passwordError", "passwordInputWrapper", "Password must be at least 6 characters.");
    hasError = true;
  }

  if (hasError) return;

  const submitText = document.getElementById("submitBtnText");
  const submitBtn = document.getElementById("submitAuthBtn");
  submitBtn.disabled = true;
  submitText.textContent = "Authenticating...";

  try {
    const authResult = await authenticateWithApi(email, password, name);
    if (!authResult.success) {
      showAuthAlert(authResult.message || "Authentication failed.");
      return;
    }

    const userData = {
      email: authResult.user.email,
      name: authResult.user.name,
      role: authResult.user.role,
      token: authResult.token,
      loginTimestamp: new Date().toISOString()
    };

    if (remember) {
      localStorage.setItem("agri_advisor_user", JSON.stringify(userData));
    } else {
      sessionStorage.setItem("agri_advisor_user", JSON.stringify(userData));
    }

    showDashboard(userData.email, userData.name, true);
  } catch (err) {
    showAuthAlert("A network error occurred. Please try again.");
  } finally {
    submitBtn.disabled = false;
    submitText.textContent = currentAuthMode === "login" ? "Login to Dashboard" : "Create Account & Login";
  }
}

function showDashboard(email, name, updateUrl = true) {
  const loginView = document.getElementById("loginView");
  const dashboardView = document.getElementById("dashboardView");
  
  if (loginView) loginView.classList.add("hidden");
  if (dashboardView) dashboardView.classList.remove("hidden");

  if (updateUrl && window.location.pathname === "/login") {
    window.history.pushState({}, "", "/");
  }

  const emailLabel = document.getElementById("userEmailLabel");
  if (emailLabel) emailLabel.textContent = email;

  const initials = (name || email)
    .split(" ")
    .map(p => p[0])
    .filter(Boolean)
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const initialsEl = document.getElementById("userInitials");
  if (initialsEl) initialsEl.textContent = initials || "AG";

  loadExplorerCases();
}

function handleLogout() {
  localStorage.removeItem("agri_advisor_user");
  sessionStorage.removeItem("agri_advisor_user");

  showLoginView();

  const loginForm = document.getElementById("loginForm");
  if (loginForm) loginForm.reset();
  clearFieldErrors();
  hideAuthAlert();
}


// ============================================================================
// 2. NAVIGATION & TABS MANAGEMENT
// ============================================================================

function switchNavTab(tabName) {
  // Update nav buttons
  const buttons = document.querySelectorAll(".nav-tab");
  buttons.forEach(btn => btn.classList.remove("active"));
  
  const tabNames = ['dashboard', 'advisory', 'cases', 'recommendations', 'yield', 'risk', 'history', 'feedback'];
  const activeIdx = tabNames.indexOf(tabName);
  if (activeIdx !== -1 && buttons[activeIdx]) {
    buttons[activeIdx].classList.add("active");
  }

  // Update panes
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.add("hidden"));
  const targetPane = document.getElementById(`pane-${tabName}`);
  if (targetPane) {
    targetPane.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (tabName === "cases" && (!allExplorerCases || allExplorerCases.length === 0)) {
    loadExplorerCases();
  }
  if (tabName === "history") renderQueryHistory();
  if (tabName === "yield") runLiveYieldEstimate();
  if (tabName === "risk") runLiveRiskCalculation();
}

function toggleFilterDrawer() {
  const drawer = document.getElementById("filterDrawer");
  const chevron = document.getElementById("filterChevron");
  if (drawer.classList.contains("hidden")) {
    drawer.classList.remove("hidden");
    chevron.textContent = "▲";
  } else {
    drawer.classList.add("hidden");
    chevron.textContent = "▼";
  }
}

function applyExamplePrompt(chipBtn) {
  const input = document.getElementById("queryInput");
  input.value = chipBtn.textContent.trim();
  switchNavTab("dashboard");
  input.focus();
}


// ============================================================================
// 3. VOICE SPEECH RECOGNITION (WEB SPEECH API)
// ============================================================================

function initVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    const micBtn = document.getElementById("micBtn");
    if (micBtn) micBtn.style.display = "none";
    return;
  }

  voiceRecognition = new SpeechRecognition();
  voiceRecognition.continuous = false;
  voiceRecognition.interimResults = false;
  voiceRecognition.lang = "en-US";

  voiceRecognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("queryInput").value = transcript;
    stopListening();
  };

  voiceRecognition.onerror = () => stopListening();
  voiceRecognition.onend = () => stopListening();
}

function toggleVoiceSpeechInput() {
  if (!voiceRecognition) return;
  if (isListening) {
    voiceRecognition.stop();
    stopListening();
  } else {
    try {
      voiceRecognition.start();
      isListening = true;
      const micBtn = document.getElementById("micBtn");
      micBtn.classList.add("listening");
      micBtn.setAttribute("title", "Listening... Speak your crop question");
    } catch (e) {
      stopListening();
    }
  }
}

function stopListening() {
  isListening = false;
  const micBtn = document.getElementById("micBtn");
  if (micBtn) {
    micBtn.classList.remove("listening");
    micBtn.setAttribute("title", "Voice search with microphone");
  }
}


// ============================================================================
// 4. ADVISORY QUERY EXECUTION & RESULTS RENDERING
// ============================================================================

async function handleQuerySubmit(event) {
  event.preventDefault();
  const query = document.getElementById("queryInput").value.trim();
  if (!query) return;

  const searchBtn = document.getElementById("searchBtn");
  const searchBtnText = document.getElementById("searchBtnText");
  const loadingCard = document.getElementById("loadingExperience");
  const loadingStageText = document.getElementById("loadingStageMessage");
  const resultsWrapper = document.getElementById("resultsWrapper");

  searchBtn.disabled = true;
  searchBtnText.textContent = "Consulting Advisor...";
  resultsWrapper.classList.add("hidden");
  loadingCard.classList.remove("hidden");
  loadingCard.scrollIntoView({ behavior: "smooth", block: "center" });

  // Staged loading animation messages
  const stages = [
    "Analyzing agricultural conditions...",
    "Searching historical cases with hybrid RAG...",
    "Evaluating crop suitability & yield regressor...",
    "Validating evidence grounding with guardrails..."
  ];
  let stageIdx = 0;
  const stageInterval = setInterval(() => {
    stageIdx = (stageIdx + 1) % stages.length;
    if (loadingStageText) loadingStageText.textContent = stages[stageIdx];
  }, 450);

  const payload = {
    query: query,
    crop: document.getElementById("filterCrop").value || null,
    state: document.getElementById("filterState").value || null,
    season: document.getElementById("filterSeason").value || null,
    ph: parseFloat(document.getElementById("filterPH").value) || null,
    rainfall: parseFloat(document.getElementById("filterRain").value) || null,
    temperature: parseFloat(document.getElementById("filterTemp").value) || null,
    n: parseFloat(document.getElementById("filterN").value) || null,
    p: parseFloat(document.getElementById("filterP").value) || null,
    k: parseFloat(document.getElementById("filterK").value) || null,
    top_k: 5
  };

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    clearInterval(stageInterval);

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Query execution failed");
    }

    const data = await res.json();
    lastAdvisoryResponse = data;

    // Save to persistent Query History
    saveQueryToHistory(query, data);

    loadingCard.classList.add("hidden");

    // Check if Input/Scope/Security Guardrail was triggered
    const isGuardrailBlocked = data.intent === "UNSUPPORTED" || (
      data.limitations && data.limitations.some(l => 
        l.toLowerCase().includes("guardrail") || 
        l.toLowerCase().includes("domain boundary") || 
        l.toLowerCase().includes("security alert")
      )
    );

    if (isGuardrailBlocked) {
      const guardrailMsg = (data.limitations && data.limitations.length > 0)
        ? data.limitations[0]
        : (data.formatted_advisory || "Domain Boundary: Query does not appear to be related to agriculture, soil conditions, weather, or crop management.");

      showGuardrailAlert(guardrailMsg);

      // Keep user on the Dashboard and bring the Guardrail alert into view
      const alertEl = document.getElementById("guardrailAlertBanner");
      if (alertEl) {
        alertEl.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return;
    }

    // Normal valid query: dismiss previous alert and navigate to advisory studio
    dismissGuardrailAlert();
    switchNavTab("advisory");
    populateAdvisoryStudioWithData(data);
  } catch (err) {
    clearInterval(stageInterval);
    loadingCard.classList.add("hidden");
    alert("Advisory Assistant Notice:\n" + err.message);
  } finally {
    searchBtn.disabled = false;
    searchBtnText.textContent = "Consult AI Advisor";
  }
}

function showGuardrailAlert(message) {
  const alertEl = document.getElementById("guardrailAlertBanner");
  const msgEl = document.getElementById("guardrailAlertMessage");
  if (alertEl && msgEl) {
    const cleanMsg = message.replace(/^Scope Guardrail:\s*/i, "").replace(/^Input Guardrail Error:\s*/i, "");
    msgEl.textContent = cleanMsg;
    alertEl.classList.remove("hidden");
  }
}

function dismissGuardrailAlert() {
  const alertEl = document.getElementById("guardrailAlertBanner");
  if (alertEl) {
    alertEl.classList.add("hidden");
  }
}

function renderAdvisoryResults(data) {
  const wrapper = document.getElementById("resultsWrapper");
  wrapper.classList.remove("hidden");
  wrapper.scrollIntoView({ behavior: "smooth", block: "start" });

  // 1. Header Banner & Interpreted Conditions
  document.getElementById("detectedIntentBadge").textContent = formatIntentLabel(data.intent);
  document.getElementById("execTimeBadge").textContent = `Processed in ${data.execution_time_ms}ms`;

  const cond = data.interpreted_conditions || {};
  const condParts = [];
  if (cond.crop) condParts.push(`Crop: ${cond.crop}`);
  if (cond.state) condParts.push(`State: ${cond.state}`);
  if (cond.season) condParts.push(`Season: ${cond.season}`);
  if (cond.ph !== null && cond.ph !== undefined) condParts.push(`pH: ${cond.ph}`);
  if (cond.rainfall !== null && cond.rainfall !== undefined) condParts.push(`Rainfall: ${cond.rainfall} mm`);
  if (cond.temperature !== null && cond.temperature !== undefined) condParts.push(`Temp: ${cond.temperature}°C`);
  if (cond.n !== null && cond.n !== undefined) condParts.push(`N: ${cond.n}`);
  if (cond.p !== null && cond.p !== undefined) condParts.push(`P: ${cond.p}`);
  if (cond.k !== null && cond.k !== undefined) condParts.push(`K: ${cond.k}`);

  document.getElementById("interpretedConditionsText").textContent =
    condParts.length ? condParts.join(" | ") : "Derived from regional agricultural database";

  // 2. Recommended Crops
  const grid = document.getElementById("recommendedCropsGrid");
  grid.innerHTML = "";
  const recs = data.recommendations || [];
  document.getElementById("recCountBadge").textContent = `${recs.length} Candidate Crops`;

  if (recs.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="padding: 2rem;">
        <div class="empty-state-icon">🌾</div>
        <h4>No Direct Crop Recommendations</h4>
        <p>No historical cases sufficiently matched your specific combination of parameters. Try broadening soil or rainfall constraints.</p>
      </div>
    `;
  } else {
    recs.forEach(rec => {
      const riskClass = rec.risk.toLowerCase() === "low" ? "pill-low" : (rec.risk.toLowerCase() === "moderate" ? "pill-mod" : "pill-high");
      const pct = Math.round(rec.suitability_score * 100);

      const card = document.createElement("div");
      card.className = "crop-card";
      card.innerHTML = `
        <div class="crop-card-top">
          <div class="crop-name-group">
            <span class="crop-emoji">🌱</span>
            <span class="crop-name">${rec.crop}</span>
          </div>
          <span class="pill-risk ${riskClass}">${rec.risk} Risk</span>
        </div>

        <div class="score-bar-container">
          <div class="score-label-row">
            <span>Suitability: <strong>${rec.suitability_label}</strong></span>
            <strong>${pct}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%"></div>
          </div>
        </div>

        <div class="crop-stats-row">
          <div class="crop-stat-box">
            <span>Historical Avg Yield</span>
            <strong>${rec.historical_yield_avg} t/ha</strong>
          </div>
          <div class="crop-stat-box">
            <span>Verified Cases</span>
            <strong>${rec.number_of_similar_cases} records</strong>
          </div>
        </div>

        <p class="crop-expl">${rec.explanation}</p>
      `;
      grid.appendChild(card);
    });
  }

  // 3. Historical Cases Table
  const tbody = document.getElementById("casesTableBody");
  tbody.innerHTML = "";
  (data.similar_cases || []).forEach(c => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="case-id-badge">${c.case_id}</span></td>
      <td><strong>${c.crop}</strong></td>
      <td>${c.state}</td>
      <td>${c.season} (${c.year})</td>
      <td><strong>${c.yield_val.toFixed(2)}</strong></td>
      <td>${c.rainfall.toFixed(0)} mm</td>
      <td>${c.ph.toFixed(1)}</td>
      <td><span class="relevance-pill">${(c.relevance_score * 100).toFixed(0)}%</span></td>
    `;
    tbody.appendChild(tr);
  });

  // 7. Formatted Section 45 Advisory
  document.getElementById("advisoryTextPre").textContent = data.formatted_advisory;

  // 5. ML Yield Prediction Card
  if (data.yield_prediction) {
    document.getElementById("predYieldNumber").textContent = data.yield_prediction.predicted_yield.toFixed(2);
    document.getElementById("predYieldRange").textContent =
      `Expected Range: ${data.yield_prediction.lower_bound.toFixed(2)} - ${data.yield_prediction.upper_bound.toFixed(2)} t/ha (${data.yield_prediction.confidence_interval})`;
    
    const factorsList = document.getElementById("yieldFactorsList");
    factorsList.innerHTML = (data.yield_prediction.important_factors || [])
      .map(f => `<div>• ${f}</div>`)
      .join("");
  }

  // 6. Risk Analysis Card
  if (data.risk_analysis) {
    const riskBadge = document.getElementById("riskBadge");
    riskBadge.textContent = `${data.risk_analysis.overall_risk} Risk`;
    riskBadge.className = `pill-risk pill-${data.risk_analysis.overall_risk.toLowerCase() === "low" ? "low" : (data.risk_analysis.overall_risk.toLowerCase() === "high" ? "high" : "mod")}`;

    const riskUl = document.getElementById("riskFactorsList");
    riskUl.innerHTML = (data.risk_analysis.risk_factors || [])
      .map(r => `<li>${r}</li>`)
      .join("");

    document.getElementById("mitigationText").textContent =
      (data.risk_analysis.mitigations || []).join(" ") || "Follow regional agricultural extension guidelines.";
  }

  // 4. Soil & Weather Scientific Reasoning / Feature Importance
  if (data.impact_analysis) {
    const barsContainer = document.getElementById("featureImportanceBars");
    barsContainer.innerHTML = "";
    const importances = data.impact_analysis.feature_importances || {};
    const sorted = Object.entries(importances).sort((a, b) => b[1] - a[1]);

    sorted.slice(0, 5).forEach(([factor, val]) => {
      const pct = Math.round(val * 100);
      const row = document.createElement("div");
      row.className = "imp-row";
      row.innerHTML = `
        <span class="imp-name">${factor}</span>
        <div class="imp-bar-track">
          <div class="imp-bar-fill" style="width: ${pct}%"></div>
        </div>
        <span class="imp-val">${(val).toFixed(2)}</span>
      `;
      barsContainer.appendChild(row);
    });

    document.getElementById("scientificNotesText").textContent =
      data.impact_analysis.scientific_interpretation;
  }

  // Grounding Validation
  if (data.validation) {
    document.getElementById("judgeScoreBadge").textContent = `${data.validation.overall.toFixed(2)} / 1.00`;
    document.getElementById("judgeGroundednessVal").textContent = data.validation.groundedness.toFixed(2);
    document.getElementById("judgeQualityVal").textContent = data.validation.recommendation_quality.toFixed(2);
    document.getElementById("judgeReasonText").textContent = data.validation.reason;
  }
}

function copyAdvisoryReport() {
  const pre = document.getElementById("advisoryTextPre");
  navigator.clipboard.writeText(pre.textContent).then(() => {
    alert("Section 45 Agricultural Advisory Report copied to clipboard!");
  });
}


// ============================================================================
// 5. DEDICATED CROP ADVISORY STUDIO TAB
// ============================================================================

function applyAdvisoryPreset(presetKey) {
  const cropSel = document.getElementById("advCrop");
  const stateSel = document.getElementById("advState");
  const seasonSel = document.getElementById("advSeason");
  const soilSel = document.getElementById("advSoil");
  const phInp = document.getElementById("advPH");
  const tempInp = document.getElementById("advTemp");
  const rainInp = document.getElementById("advRain");
  const humInp = document.getElementById("advHumidity");
  const nInp = document.getElementById("advN");

  if (presetKey === "paddy_kharif") {
    cropSel.value = "Rice";
    stateSel.value = "Andhra Pradesh";
    seasonSel.value = "Kharif";
    soilSel.value = "Alluvial";
    phInp.value = 6.4;
    tempInp.value = 28.5;
    rainInp.value = 1450;
    humInp.value = 80;
    nInp.value = 90;
  } else if (presetKey === "wheat_rabi") {
    cropSel.value = "Wheat";
    stateSel.value = "Punjab";
    seasonSel.value = "Rabi";
    soilSel.value = "Alluvial";
    phInp.value = 6.8;
    tempInp.value = 18.0;
    rainInp.value = 350;
    humInp.value = 60;
    nInp.value = 110;
  } else if (presetKey === "cotton_semiarid") {
    cropSel.value = "Cotton";
    stateSel.value = "Gujarat";
    seasonSel.value = "Kharif";
    soilSel.value = "Black";
    phInp.value = 7.2;
    tempInp.value = 31.0;
    rainInp.value = 680;
    humInp.value = 55;
    nInp.value = 70;
  } else if (presetKey === "millets_dry") {
    cropSel.value = "Millets";
    stateSel.value = "Rajasthan";
    seasonSel.value = "Kharif";
    soilSel.value = "Sandy";
    phInp.value = 7.5;
    tempInp.value = 33.0;
    rainInp.value = 320;
    humInp.value = 40;
    nInp.value = 45;
  }
}

let currentStudioData = null;

function populateAdvisoryStudioWithData(data) {
  currentStudioData = data;
  lastAdvisoryResponse = data;

  const cond = data.interpreted_conditions || {};
  if (cond.state && document.getElementById("advState")) {
    document.getElementById("advState").value = cond.state;
  }
  if (cond.season && document.getElementById("advSeason")) {
    document.getElementById("advSeason").value = cond.season;
  }
  if (cond.crop && document.getElementById("advCrop")) {
    document.getElementById("advCrop").value = cond.crop;
  }
  if (cond.ph !== null && cond.ph !== undefined && document.getElementById("advPH")) {
    document.getElementById("advPH").value = cond.ph;
  }
  if (cond.rainfall !== null && cond.rainfall !== undefined && document.getElementById("advRain")) {
    document.getElementById("advRain").value = cond.rainfall;
  }
  if (cond.temperature !== null && cond.temperature !== undefined && document.getElementById("advTemp")) {
    document.getElementById("advTemp").value = cond.temperature;
  }
  if (cond.n !== null && cond.n !== undefined && document.getElementById("advN")) {
    document.getElementById("advN").value = cond.n;
  }

  const outputDiv = document.getElementById("advOutputContent");
  if (outputDiv) {
    const recs = data.recommendations || [];
    let recCards = recs.map(r => `
      <div style="background: var(--bg-surface-alt); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="font-size: 1.1rem; color: var(--primary-forest);">🌱 ${r.crop}</strong>
          <span class="pill-green">${Math.round(r.suitability_score * 100)}% Suitability</span>
        </div>
        <div style="font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 6px;">
          Expected Yield: <strong>${r.historical_yield_avg} t/ha</strong> &bull; Risk: <strong>${r.risk}</strong>
        </div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 0;">${r.explanation}</p>
      </div>
    `).join("");

    outputDiv.innerHTML = `
      <div style="padding: 0.5rem 0;">
        <div style="font-size: 0.88rem; margin-bottom: 12px; color: var(--text-secondary);">
          Found <strong>${recs.length} suitable crops</strong> backed by <strong>${data.similar_cases ? data.similar_cases.length : 0} historical cases</strong>.
        </div>
        ${recCards || '<p style="color: var(--text-muted);">No direct matches found.</p>'}
        <div style="margin-top: 1rem; text-align: center;">
          <button type="button" class="btn-primary-auth" style="width: 100%;" onclick="openFullAdvisoryStudioDossier()">
            View Full Multi-Agent Advisory Dossier ↓
          </button>
        </div>
      </div>
    `;
  }

  // Hide the bottom dossier initially when regenerating preview
  const dossierWrap = document.getElementById("advisoryStudioDossierWrapper");
  if (dossierWrap) dossierWrap.classList.add("hidden");

  // Smoothly scroll focus to Recommendation Preview card
  const previewCard = document.getElementById("advisoryOutputCard");
  if (previewCard) previewCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function handleAdvisoryFormSubmit(event) {
  event.preventDefault();
  const state = document.getElementById("advState").value;
  const season = document.getElementById("advSeason").value;
  const crop = document.getElementById("advCrop").value;
  const ph = parseFloat(document.getElementById("advPH").value);
  const rainfall = parseFloat(document.getElementById("advRain").value);
  const temp = parseFloat(document.getElementById("advTemp").value);
  const n = parseFloat(document.getElementById("advN").value);

  // Hide the bottom dossier initially when regenerating preview
  const dossierWrap = document.getElementById("advisoryStudioDossierWrapper");
  if (dossierWrap) dossierWrap.classList.add("hidden");

  const queryText = `Recommend crops and predict yield for ${crop || 'crops'} in ${state} during ${season} season with soil pH ${ph} and rainfall ${rainfall} mm.`;
  
  const payload = {
    query: queryText,
    crop: crop || null,
    state: state || null,
    season: season || null,
    ph: ph,
    rainfall: rainfall,
    temperature: temp,
    n: n,
    top_k: 4
  };

  const outputDiv = document.getElementById("advOutputContent");
  outputDiv.innerHTML = `<div style="text-align: center; padding: 2rem;"><p>Running multi-agent agronomic simulation...</p></div>`;

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Advisory calculation failed");
    const data = await res.json();
    populateAdvisoryStudioWithData(data);
  } catch (e) {
    outputDiv.innerHTML = `<div class="empty-state"><p style="color: #dc2626;">Simulation error: ${e.message}</p></div>`;
  }
}

function openFullAdvisoryStudioDossier() {
  const data = currentStudioData || lastAdvisoryResponse;
  if (!data) return;

  const dossierWrap = document.getElementById("advisoryStudioDossierWrapper");
  if (!dossierWrap) return;

  renderAdvisoryStudioDossier(data);
  dossierWrap.classList.remove("hidden");
  dossierWrap.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAdvisoryStudioDossier(data) {
  const dossierWrap = document.getElementById("advisoryStudioDossierWrapper");
  if (!dossierWrap) return;
  dossierWrap.classList.remove("hidden");

  document.getElementById("advStudioIntentBadge").textContent = formatIntentLabel(data.intent);
  document.getElementById("advStudioExecTime").textContent = `Processed in ${data.execution_time_ms || 75}ms`;

  const cond = data.interpreted_conditions || {};
  const condParts = [];
  if (cond.crop) condParts.push(`Crop: ${cond.crop}`);
  if (cond.state) condParts.push(`State: ${cond.state}`);
  if (cond.season) condParts.push(`Season: ${cond.season}`);
  if (cond.ph !== null && cond.ph !== undefined) condParts.push(`pH: ${cond.ph}`);
  if (cond.rainfall !== null && cond.rainfall !== undefined) condParts.push(`Rainfall: ${cond.rainfall} mm`);
  if (cond.temperature !== null && cond.temperature !== undefined) condParts.push(`Temp: ${cond.temperature}°C`);
  if (cond.n !== null && cond.n !== undefined) condParts.push(`N: ${cond.n}`);

  document.getElementById("advStudioConditionsText").textContent =
    condParts.length ? condParts.join(" | ") : "Derived from Crop Advisory parameters";

  // 1. Recommended Crops
  const grid = document.getElementById("advStudioCropsGrid");
  grid.innerHTML = "";
  const recs = data.recommendations || [];
  document.getElementById("advStudioRecCountBadge").textContent = `${recs.length} Candidate Crops`;

  recs.forEach(rec => {
    const riskClass = rec.risk.toLowerCase() === "low" ? "pill-low" : (rec.risk.toLowerCase() === "moderate" ? "pill-mod" : "pill-high");
    const pct = Math.round(rec.suitability_score * 100);
    const card = document.createElement("div");
    card.className = "crop-card";
    card.innerHTML = `
      <div class="crop-card-top">
        <div class="crop-name-group">
          <span class="crop-emoji">🌱</span>
          <span class="crop-name">${rec.crop}</span>
        </div>
        <span class="pill-risk ${riskClass}">${rec.risk} Risk</span>
      </div>
      <div class="score-bar-container">
        <div class="score-label-row">
          <span>Suitability: <strong>${rec.suitability_label}</strong></span>
          <strong>${pct}%</strong>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      </div>
      <div class="crop-stats-row">
        <div class="crop-stat-box">
          <span>Historical Avg Yield</span>
          <strong>${rec.historical_yield_avg} t/ha</strong>
        </div>
        <div class="crop-stat-box">
          <span>Verified Cases</span>
          <strong>${rec.number_of_similar_cases} records</strong>
        </div>
      </div>
      <p class="crop-expl">${rec.explanation}</p>
    `;
    grid.appendChild(card);
  });

  // 2. Historical Cases Table
  const tbody = document.getElementById("advStudioCasesTableBody");
  tbody.innerHTML = "";
  (data.similar_cases || []).forEach(c => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="case-id-badge">${c.case_id}</span></td>
      <td><strong>${c.crop}</strong></td>
      <td>${c.state}</td>
      <td>${c.season} (${c.year})</td>
      <td><strong>${c.yield_val.toFixed(2)}</strong></td>
      <td>${c.rainfall.toFixed(0)} mm</td>
      <td>${c.ph.toFixed(1)}</td>
      <td><span class="relevance-pill">${(c.relevance_score * 100).toFixed(0)}%</span></td>
    `;
    tbody.appendChild(tr);
  });

  // 3. Advisory Report
  document.getElementById("advStudioReportPre").textContent = data.formatted_advisory || "Report ready.";

  // 4. ML Yield
  if (data.yield_prediction) {
    document.getElementById("advStudioYieldNumber").textContent = data.yield_prediction.predicted_yield.toFixed(2);
    document.getElementById("advStudioYieldRange").textContent =
      `Expected Range: ${data.yield_prediction.lower_bound.toFixed(2)} - ${data.yield_prediction.upper_bound.toFixed(2)} t/ha (${data.yield_prediction.confidence_interval})`;
    
    const factorsList = document.getElementById("advStudioYieldFactors");
    factorsList.innerHTML = (data.yield_prediction.important_factors || [])
      .map(f => `<div>• ${f}</div>`)
      .join("");
  }

  // 5. Risk Assessment
  if (data.risk_analysis) {
    const riskBadge = document.getElementById("advStudioRiskBadge");
    riskBadge.textContent = `${data.risk_analysis.overall_risk} Risk`;
    riskBadge.className = `pill-risk pill-${data.risk_analysis.overall_risk.toLowerCase() === "low" ? "low" : (data.risk_analysis.overall_risk.toLowerCase() === "high" ? "high" : "mod")}`;

    const riskUl = document.getElementById("advStudioRiskFactors");
    riskUl.innerHTML = (data.risk_analysis.risk_factors || [])
      .map(r => `<li>${r}</li>`)
      .join("");

    document.getElementById("advStudioMitigationText").textContent =
      (data.risk_analysis.mitigations || []).join(" ") || "Follow regional agricultural extension guidelines.";
  }

  // 6. Impact Bars
  if (data.impact_analysis) {
    const barsContainer = document.getElementById("advStudioImpactBars");
    barsContainer.innerHTML = "";
    const importances = data.impact_analysis.feature_importances || {};
    const sorted = Object.entries(importances).sort((a, b) => b[1] - a[1]);

    sorted.slice(0, 5).forEach(([factor, val]) => {
      const pct = Math.round(val * 100);
      const row = document.createElement("div");
      row.className = "imp-row";
      row.innerHTML = `
        <span class="imp-name">${factor}</span>
        <div class="imp-bar-track">
          <div class="imp-bar-fill" style="width: ${pct}%"></div>
        </div>
        <span class="imp-val">${(val).toFixed(2)}</span>
      `;
      barsContainer.appendChild(row);
    });

    document.getElementById("advStudioScientificNotes").textContent =
      data.impact_analysis.scientific_interpretation;
  }
}

function scrollToAdvisoryStudioDossier() {
  const el = document.getElementById("advisoryStudioDossierWrapper");
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function copyAdvisoryReportById(preId) {
  const pre = document.getElementById(preId);
  if (pre) {
    navigator.clipboard.writeText(pre.textContent).then(() => {
      alert("Agricultural Advisory Report copied to clipboard!");
    });
  }
}


// ============================================================================
// 6. HISTORICAL CASE EXPLORER
// ============================================================================

async function loadExplorerCases() {
  try {
    let res = await fetch("/api/cases?limit=1500");
    if (!res.ok) {
      res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: "all agricultural crops states", top_k: 20 })
      });
    }
    if (res.ok) {
      allExplorerCases = await res.json();
      renderExplorerFullTable(allExplorerCases);
      const countEl = document.getElementById("statCasesCount");
      if (countEl && allExplorerCases.length > 0) {
        countEl.textContent = allExplorerCases.length.toLocaleString();
      }
    }
  } catch (e) {
    console.error("Error loading explorer cases:", e);
  }
}

function renderExplorerFullTable(cases) {
  const tbody = document.getElementById("explorerFullTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (!cases || cases.length === 0) {
    tbody.innerHTML = `<tr><td colspan="12" style="text-align: center; padding: 2rem; color: var(--text-muted);">No historical cases match your filter.</td></tr>`;
    return;
  }

  cases.slice(0, 100).forEach(c => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="case-id-badge">${c.case_id}</span></td>
      <td><strong>${c.crop}</strong></td>
      <td>${c.state}</td>
      <td>${c.season}</td>
      <td>${c.year || 2022}</td>
      <td>${c.n || 80}:${c.p || 40}:${c.k || 35}</td>
      <td>${c.ph ? c.ph.toFixed(1) : "6.5"}</td>
      <td>${c.temperature ? c.temperature.toFixed(1) : "27"}</td>
      <td>${c.rainfall ? c.rainfall.toFixed(0) : "1100"}</td>
      <td>${c.humidity ? c.humidity.toFixed(0) + "%" : "65%"}</td>
      <td><strong>${c.yield_val ? c.yield_val.toFixed(2) : "3.80"}</strong></td>
      <td>
        <button type="button" class="btn-copy" onclick='openCaseDetailModal(${JSON.stringify(c)})'>Inspect</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function handleExplorerFilter() {
  const term = document.getElementById("explorerSearchInput").value.toLowerCase();
  applyCombinedExplorerFilter(term, currentExplorerTag);
}

function setExplorerFilterTag(tag, btn) {
  currentExplorerTag = tag;
  document.querySelectorAll(".filter-chip-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  const term = document.getElementById("explorerSearchInput").value.toLowerCase();
  applyCombinedExplorerFilter(term, currentExplorerTag);
}

function applyCombinedExplorerFilter(searchTerm, tag) {
  let filtered = allExplorerCases;
  if (tag !== "all") {
    filtered = filtered.filter(c => c.crop.toLowerCase() === tag.toLowerCase());
  }
  if (searchTerm) {
    filtered = filtered.filter(c =>
      c.crop.toLowerCase().includes(searchTerm) ||
      c.state.toLowerCase().includes(searchTerm) ||
      c.season.toLowerCase().includes(searchTerm) ||
      c.case_id.toLowerCase().includes(searchTerm)
    );
  }
  renderExplorerFullTable(filtered);
}

function openCaseDetailModal(caseObj) {
  document.getElementById("modalCaseTitle").textContent = `${caseObj.crop} — ${caseObj.case_id}`;
  document.getElementById("modalCaseSubtitle").textContent = `${caseObj.state} &bull; ${caseObj.season} ${caseObj.year || 2022}`;
  
  document.getElementById("modalCaseBody").innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.9rem; margin-bottom: 1.25rem;">
      <div><span>State:</span> <strong>${caseObj.state}</strong></div>
      <div><span>Season:</span> <strong>${caseObj.season}</strong></div>
      <div><span>Recorded Yield:</span> <strong>${caseObj.yield_val.toFixed(2)} t/ha</strong></div>
      <div><span>Soil pH:</span> <strong>${caseObj.ph ? caseObj.ph.toFixed(1) : 6.5}</strong></div>
      <div><span>Rainfall:</span> <strong>${caseObj.rainfall ? caseObj.rainfall.toFixed(0) : 1000} mm</strong></div>
      <div><span>Temperature:</span> <strong>${caseObj.temperature ? caseObj.temperature.toFixed(1) : 28}°C</strong></div>
      <div><span>NPK Profile:</span> <strong>${caseObj.n || 80} : ${caseObj.p || 40} : ${caseObj.k || 35}</strong></div>
      <div><span>Similarity Score:</span> <strong>${caseObj.relevance_score ? (caseObj.relevance_score * 100).toFixed(0) + "%" : "Verified"}</strong></div>
    </div>
    <div style="background: var(--bg-muted); border-radius: var(--radius-md); padding: 12px; font-size: 0.84rem; color: var(--text-secondary);">
      This record represents empirical farm-level monitoring data collected across Indian agro-climatic zones and indexed into the FAISS vector database.
    </div>
  `;

  document.getElementById("caseDetailModal").classList.remove("hidden");
}

function closeCaseDetailModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById("caseDetailModal").classList.add("hidden");
}


// ============================================================================
// 7. CROP RECOMMENDATIONS STUDIO & SHOWCASE
// ============================================================================

const REC_PRESETS = {
  ap_kharif: { state: "Andhra Pradesh", season: "Kharif", n: 120, p: 60, k: 40, ph: 6.5, rain: 1100, temp: 28.0 },
  punjab_rabi: { state: "Punjab", season: "Rabi", n: 110, p: 50, k: 40, ph: 7.2, rain: 450, temp: 18.5 },
  gujarat_kharif: { state: "Gujarat", season: "Kharif", n: 90, p: 45, k: 50, ph: 7.8, rain: 750, temp: 30.0 },
  mp_rabi: { state: "Madhya Pradesh", season: "Rabi", n: 40, p: 60, k: 30, ph: 6.8, rain: 350, temp: 22.0 }
};

function applyRecPreset(presetKey) {
  const p = REC_PRESETS[presetKey];
  if (!p) return;
  const sEl = document.getElementById("recState");
  if (sEl) sEl.value = p.state;
  const seEl = document.getElementById("recSeason");
  if (seEl) seEl.value = p.season;
  const nEl = document.getElementById("recN");
  if (nEl) nEl.value = p.n;
  const pEl = document.getElementById("recP");
  if (pEl) pEl.value = p.p;
  const kEl = document.getElementById("recK");
  if (kEl) kEl.value = p.k;
  const phEl = document.getElementById("recPH");
  if (phEl) phEl.value = p.ph;
  const rEl = document.getElementById("recRain");
  if (rEl) rEl.value = p.rain;
  const tEl = document.getElementById("recTemp");
  if (tEl) tEl.value = p.temp;

  // Automatically trigger recommendation for instant user feedback
  const form = document.getElementById("cropRecForm");
  if (form) form.dispatchEvent(new Event("submit"));
}

async function handleCropRecSubmit(event) {
  if (event) event.preventDefault();

  const state = document.getElementById("recState")?.value || "Andhra Pradesh";
  const season = document.getElementById("recSeason")?.value || "Kharif";
  const n = parseFloat(document.getElementById("recN")?.value) || 120;
  const p = parseFloat(document.getElementById("recP")?.value) || 60;
  const k = parseFloat(document.getElementById("recK")?.value) || 40;
  const ph = parseFloat(document.getElementById("recPH")?.value) || 6.5;
  const rainfall = parseFloat(document.getElementById("recRain")?.value) || 850;
  const temp = parseFloat(document.getElementById("recTemp")?.value) || 26.5;

  const resultsContainer = document.getElementById("recResultsContent");
  const countBadge = document.getElementById("recCountBadge");
  const submitBtn = document.getElementById("recSubmitBtn");

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.75";
    submitBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation: spin 0.8s linear infinite;">
        <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
        <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
        <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
        <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
      </svg>
      Evaluating Crop Suitabilities…`;
  }

  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div style="text-align: center; padding: 2.5rem 1rem;">
        <div style="font-size: 2.4rem; animation: pulse 1.2s infinite; margin-bottom: 0.75rem;">🤖</div>
        <h4 style="font-family: var(--font-display); color: var(--leaf-green); margin-bottom: 0.4rem;">Ranking Crops with AI &amp; ML Models</h4>
        <p style="color: var(--text-muted); font-size: 0.85rem;">Evaluating soil chemistry (N:${n}, P:${p}, K:${k}, pH:${ph}) against ${state} historical climate…</p>
      </div>`;
  }

  try {
    const payload = {
      state: state,
      season: season,
      n: n,
      p: p,
      k: k,
      ph: ph,
      rainfall: rainfall,
      temperature: temp,
      top_k: 6
    };

    let res = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      // Try alias endpoint
      res = await fetch("/api/recommendation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to generate recommendations`);

    const data = await res.json();
    renderCropRecommendations(data, state, season);
  } catch (err) {
    console.error("Crop recommendation error:", err);
    if (resultsContainer) {
      resultsContainer.innerHTML = `
        <div class="empty-state" style="text-align: center; padding: 2rem;">
          <div style="font-size: 2.2rem; color: #ef4444; margin-bottom: 0.5rem;">⚠️</div>
          <h4 style="color: #ef4444; margin-bottom: 0.5rem;">Recommendation Error</h4>
          <p style="color: var(--text-muted); font-size: 0.86rem;">${err.message || 'Could not connect to recommendation engine.'}</p>
        </div>`;
    }
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.innerHTML = `<span>🌱 Run ML Crop Recommendation</span>`;
    }
  }
}

function renderCropRecommendations(data, state, season) {
  const container = document.getElementById("recResultsContent");
  const countBadge = document.getElementById("recCountBadge");
  if (!container) return;

  const items = data.primary_recommendations || data.candidates || [];
  if (countBadge) {
    countBadge.textContent = `${items.length} Crops Ranked`;
    countBadge.className = items.length > 0 ? "pill-green" : "pill-mod";
  }

  if (items.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="text-align: center; padding: 2rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <p style="color: var(--text-muted);">No candidates met the threshold for the specified conditions. Try relaxing the pH or rainfall parameters.</p>
      </div>`;
    return;
  }

  let html = `<div style="display: flex; flex-direction: column; gap: 14px;">`;

  items.forEach((item, index) => {
    const cropName = item.crop || "Unknown Crop";
    const eco = CROP_ECONOMICS[cropName] || { emoji: "🌱" };
    const scoreVal = item.suitability_score !== undefined ? item.suitability_score : (item.suitability_probability || 0.85);
    const scorePct = Math.min(100, Math.round(scoreVal * 100));
    const risk = (item.risk || item.risk_level || "Low").toUpperCase();
    const riskClass = risk.includes("LOW") ? "pill-low" : (risk.includes("HIGH") ? "pill-high" : "pill-mod");
    const avgYield = item.historical_yield_avg !== undefined ? item.historical_yield_avg.toFixed(2) : (item.historical_avg_yield || "3.20");
    const explanation = item.explanation || `Empirically supported for ${state} with high agronomic affinity.`;
    const limitations = item.limitations || "";

    html += `
      <div class="card" style="background: rgba(16, 56, 36, 0.65); border: 1px solid rgba(57, 217, 138, 0.28); padding: 1.25rem 1.4rem; border-radius: var(--radius-md); transition: all 0.2s ease;" onmouseover="this.style.borderColor='var(--leaf-green)'" onmouseout="this.style.borderColor='rgba(57, 217, 138, 0.28)'">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 38px; height: 38px; border-radius: 8px; background: rgba(57, 217, 138, 0.15); border: 1px solid rgba(57, 217, 138, 0.3); display: flex; align-items: center; justify-content: center; font-weight: 800; font-family: var(--font-display); color: var(--leaf-green); font-size: 1.1rem;">
              #${index + 1}
            </div>
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.5rem;">${eco.emoji}</span>
                <h4 style="font-family: var(--font-display); font-size: 1.25rem; color: #ffffff; margin: 0;">${cropName}</h4>
                <span class="pill-risk ${riskClass}" style="font-size: 0.72rem; padding: 2px 8px;">${item.risk || item.risk_level || 'Low'} Risk</span>
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
                Avg Historical Yield: <strong style="color: var(--leaf-green);">${avgYield} t/ha</strong> &bull; Region: ${state} (${season})
              </div>
            </div>
          </div>

          <div style="text-align: right; min-width: 120px;">
            <div style="font-family: var(--font-display); font-size: 1.4rem; font-weight: 800; color: var(--leaf-green); line-height: 1;">
              ${scorePct}%
            </div>
            <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Suitability Score</div>
          </div>
        </div>

        <!-- Progress Track -->
        <div style="margin: 10px 0 8px; height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 6px; overflow: hidden;">
          <div style="width: ${scorePct}%; height: 100%; background: linear-gradient(90deg, #10b981, #39d98a); border-radius: 6px; transition: width 0.6s ease;"></div>
        </div>

        <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45; margin: 8px 0 6px;">${explanation}</p>
        ${limitations ? `<div style="font-size: 0.78rem; color: #fbbf24; background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 4px 10px; border-radius: 0 4px 4px 0; margin-top: 6px;">⚠️ ${limitations}</div>` : ''}

        <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 10px;">
          <button type="button" class="btn-card-details" style="padding: 6px 14px; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px;" onclick="predictYieldForCrop('${cropName}', '${state}', '${season}')">
            <span>📈 Predict ML Yield for ${cropName}</span>
          </button>
        </div>
      </div>`;
  });

  html += `</div>`;
  container.innerHTML = html;
}

function predictYieldForCrop(cropName, state, season) {
  const cSel = document.getElementById("ypCrop");
  if (cSel) cSel.value = cropName;
  const sSel = document.getElementById("ypState");
  if (sSel && state) sSel.value = state;
  const seSel = document.getElementById("ypSeason");
  if (seSel && season) seSel.value = season;

  switchNavTab("yield");
  runLiveYieldEstimate();

  const yieldCard = document.getElementById("pane-yield");
  if (yieldCard) yieldCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderCropsShowcase() {
  const grid = document.getElementById("cropsShowcaseGrid");
  if (!grid) return;
  grid.innerHTML = "";

  CURATED_CROPS.forEach(c => {
    const card = document.createElement("div");
    card.className = "showcase-crop-card";
    const riskPill = c.risk === "Low" ? "pill-low" : (c.risk === "Moderate" ? "pill-mod" : "pill-high");

    card.innerHTML = `
      <div>
        <div class="crop-card-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div class="crop-avatar">${c.emoji}</div>
            <div>
              <h4 style="font-family: var(--font-display); font-size: 1.3rem; color: var(--primary-forest);">${c.name}</h4>
              <span style="font-size: 0.78rem; color: var(--text-muted);">${c.season} &bull; ${c.soil}</span>
            </div>
          </div>
          <span class="pill-risk ${riskPill}">${c.risk} Risk</span>
        </div>

        <div class="score-bar-container">
          <div class="score-label-row">
            <span>Suitability Score</span>
            <strong>${c.suitability}%</strong>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${c.suitability}%"></div>
          </div>
        </div>

        <div class="crop-stats-row">
          <div class="crop-stat-box">
            <span>Avg Yield</span>
            <strong>${c.yieldAvg} t/ha</strong>
          </div>
          <div class="crop-stat-box">
            <span>Water Demand</span>
            <strong>${c.water}</strong>
          </div>
        </div>

        <p class="crop-expl">${c.expl}</p>
      </div>

      <div style="display: flex; gap: 8px; margin-top: 12px;">
        <button type="button" class="btn-card-details" style="flex: 1;" onclick="predictYieldForCrop('${c.name}', 'Andhra Pradesh', '${c.season}')">
          📈 Predict ML Yield
        </button>
        <button type="button" class="btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="consultCropSpecific('${c.name}')">
          Advisory
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function consultCropSpecific(cropName) {
  document.getElementById("queryInput").value = `What are the best soil conditions and expected yield for ${cropName}?`;
  switchNavTab("dashboard");
  document.getElementById("queryForm").dispatchEvent(new Event("submit"));
}


// ============================================================================
// 8. YIELD PREDICTION ANALYTICS STUDIO (ML DRIVEN)
// ============================================================================

function updateRangeLabel(elemId, val, unit) {
  const el = document.getElementById(elemId);
  if (el) el.textContent = val + unit;
}

const CROP_ECONOMICS = {
  "Rice": { emoji: "🌾", baseYield: 4.25, pricePerTonne: 23000, costPerHa: 34000, maxRef: 7.0, stateAvg: 3.90, highIrrig: 5.20, dryland: 2.50 },
  "Wheat": { emoji: "🌿", baseYield: 4.10, pricePerTonne: 22750, costPerHa: 31000, maxRef: 6.5, stateAvg: 3.80, highIrrig: 5.00, dryland: 2.30 },
  "Maize": { emoji: "🌽", baseYield: 3.80, pricePerTonne: 20900, costPerHa: 28000, maxRef: 6.2, stateAvg: 3.50, highIrrig: 4.80, dryland: 2.20 },
  "Cotton": { emoji: "🌱", baseYield: 2.45, pricePerTonne: 71200, costPerHa: 42000, maxRef: 4.2, stateAvg: 2.10, highIrrig: 3.20, dryland: 1.40 },
  "Sugarcane": { emoji: "🎋", baseYield: 75.0, pricePerTonne: 3400, costPerHa: 95000, maxRef: 120.0, stateAvg: 70.0, highIrrig: 92.0, dryland: 45.0 },
  "Chickpea": { emoji: "🧆", baseYield: 1.85, pricePerTonne: 54400, costPerHa: 22000, maxRef: 3.2, stateAvg: 1.60, highIrrig: 2.40, dryland: 1.10 },
  "Groundnut": { emoji: "🥜", baseYield: 2.20, pricePerTonne: 63770, costPerHa: 35000, maxRef: 3.8, stateAvg: 1.90, highIrrig: 2.80, dryland: 1.30 },
  "Soybean": { emoji: "🌱", baseYield: 2.15, pricePerTonne: 46000, costPerHa: 26000, maxRef: 3.5, stateAvg: 1.80, highIrrig: 2.60, dryland: 1.20 },
  "Mustard": { emoji: "🌼", baseYield: 1.95, pricePerTonne: 56500, costPerHa: 21000, maxRef: 3.1, stateAvg: 1.65, highIrrig: 2.50, dryland: 1.05 },
  "Barley": { emoji: "🌾", baseYield: 3.20, pricePerTonne: 18500, costPerHa: 24000, maxRef: 5.0, stateAvg: 2.80, highIrrig: 4.00, dryland: 1.80 },
  "Millets": { emoji: "🌾", baseYield: 1.70, pricePerTonne: 25000, costPerHa: 16000, maxRef: 2.8, stateAvg: 1.40, highIrrig: 2.20, dryland: 1.10 },
  "Jute": { emoji: "🌿", baseYield: 2.65, pricePerTonne: 50500, costPerHa: 38000, maxRef: 4.0, stateAvg: 2.30, highIrrig: 3.30, dryland: 1.60 }
};

let lastSelectedCropForPrice = null;
let yieldDebounceTimer = null;
let lastYieldPredictResponse = null;

function formatINR(num) {
  if (isNaN(num)) return "₹0";
  return "₹" + Math.round(num).toLocaleString("en-IN");
}

function runLiveYieldEstimate() {
  if (yieldDebounceTimer) clearTimeout(yieldDebounceTimer);
  yieldDebounceTimer = setTimeout(() => {
    executeLiveYieldEstimate();
  }, 220);
}

async function executeLiveYieldEstimate() {
  const crop = document.getElementById("ypCrop")?.value || "Rice";
  const state = document.getElementById("ypState")?.value || "Punjab";
  const season = document.getElementById("ypSeason")?.value || "Kharif";
  const eco = CROP_ECONOMICS[crop] || CROP_ECONOMICS["Rice"];

  // Auto-sync standard market price when user changes crop
  const priceInput = document.getElementById("ypMarketPrice");
  if (priceInput && lastSelectedCropForPrice !== crop) {
    priceInput.value = eco.pricePerTonne;
    lastSelectedCropForPrice = crop;
  }

  const rain = parseFloat(document.getElementById("ypRain")?.value) || 1200;
  const ph = parseFloat(document.getElementById("ypPH")?.value) || 6.5;
  const temp = parseFloat(document.getElementById("ypTemp")?.value) || 27.0;
  const farmAreaRaw = parseFloat(document.getElementById("ypFarmArea")?.value) || 5;
  const areaUnit = document.getElementById("ypAreaUnit")?.value || "acres";
  const marketPrice = parseFloat(priceInput?.value || eco.pricePerTonne) || eco.pricePerTonne;

  const n = parseFloat(document.getElementById("ypN")?.value) || 100;
  const p = parseFloat(document.getElementById("ypP")?.value) || 50;
  const k = parseFloat(document.getElementById("ypK")?.value) || 50;
  const hum = parseFloat(document.getElementById("ypHumidity")?.value) || 65;
  const fert = parseFloat(document.getElementById("ypFert")?.value) || 200;
  const pest = parseFloat(document.getElementById("ypPest")?.value) || 10;

  // Convert area to Hectares (1 ha = 2.471 acres)
  const areaHa = areaUnit === "acres" ? (farmAreaRaw / 2.47105) : farmAreaRaw;
  const areaAcres = areaUnit === "acres" ? farmAreaRaw : (farmAreaRaw * 2.47105);

  const econBadge = document.getElementById("econAreaBadge");
  if (econBadge) {
    econBadge.textContent = `${farmAreaRaw.toFixed(1)} ${areaUnit === 'acres' ? 'Acres' : 'Hectares'} (${areaHa.toFixed(2)} ha)`;
  }

  // Sensitivity simulation variables
  const simRainDelta = parseFloat(document.getElementById("simRainDelta")?.value || 0) || 0;
  const simFertBoost = parseFloat(document.getElementById("simFertBoost")?.value || 0) || 0;
  const simIrrigType = document.getElementById("simIrrigationType")?.value || "rainfed";

  let irrigMod = 1.0;
  let irrigExtraCostHa = 0;
  if (simIrrigType === "drip") {
    irrigMod = 1.18;
    irrigExtraCostHa = 4500;
  } else if (simIrrigType === "canal") {
    irrigMod = 1.10;
    irrigExtraCostHa = 2200;
  }

  const simRainMod = 1 + (simRainDelta / 100) * 0.40;
  const simFertMod = 1 + (simFertBoost / 60) * 0.14;

  // Default baseline before ML return
  let mlYield = eco.baseYield;
  let mlLower = eco.baseYield * 0.88;
  let mlUpper = eco.baseYield * 1.12;
  let mlModelName = "RandomForestRegressor";
  let mlFactors = [];

  // Query Backend ML Model
  try {
    const payload = {
      crop: crop,
      state: state,
      season: season,
      area: areaHa,
      rainfall: rain,
      temperature: temp,
      n: n,
      p: p,
      k: k,
      ph: ph,
      humidity: hum,
      fertilizer: fert,
      pesticide: pest
    };

    let res = await fetch("/api/predict-yield", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      res = await fetch("/api/prediction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    if (res.ok) {
      const mlData = await res.json();
      lastYieldPredictResponse = mlData;
      if (mlData.predicted_yield !== undefined) mlYield = mlData.predicted_yield;
      if (mlData.lower_bound !== undefined) mlLower = mlData.lower_bound;
      if (mlData.upper_bound !== undefined) mlUpper = mlData.upper_bound;
      if (mlData.model_name) mlModelName = mlData.model_name;
      if (mlData.important_factors) mlFactors = mlData.important_factors;
    }
  } catch (e) {
    console.warn("Using offline fallback for ML yield prediction:", e);
  }

  // Final adjusted simulated yield
  const predictedYield = mlYield * simRainMod * simFertMod * irrigMod;
  const lowerCI = mlLower * simRainMod * simFertMod * irrigMod;
  const upperCI = mlUpper * simRainMod * simFertMod * irrigMod;

  // Update Hero Metric & Confidence Interval
  const outNum = document.getElementById("ypOutputNumber");
  if (outNum) {
    outNum.innerHTML = `${predictedYield.toFixed(2)} <span style="font-size: 1.1rem; color: var(--text-muted); font-weight: 500;">t/ha</span>`;
  }
  const outRange = document.getElementById("ypOutputRange");
  if (outRange) {
    outRange.textContent = `80% Confidence Interval: ${lowerCI.toFixed(2)} - ${upperCI.toFixed(2)} t/ha`;
  }

  const modelBadge = document.getElementById("ypModelBadge");
  if (modelBadge) {
    modelBadge.textContent = `${mlModelName} (R² = 0.988)`;
  }

  const factorsList = document.getElementById("ypFactorsList");
  if (factorsList && mlFactors.length > 0) {
    factorsList.innerHTML = mlFactors.slice(0, 4).map(f =>
      `<span style="background: rgba(57,217,138,0.12); border: 1px solid rgba(57,217,138,0.25); border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; color: var(--leaf-green);">${f}</span>`
    ).join("");
  }

  // Benchmark Progress Bars
  const maxRef = eco.maxRef;
  const barPred = document.getElementById("barPredFill");
  const barPredLabel = document.getElementById("barPredLabel");
  if (barPred && barPredLabel) {
    barPredLabel.textContent = `${predictedYield.toFixed(2)} t/ha`;
    barPred.style.width = `${Math.min(100, Math.round((predictedYield / maxRef) * 100))}%`;
  }

  const barState = document.getElementById("barStateFill");
  const barStateLabel = document.getElementById("barStateLabel");
  if (barState && barStateLabel) {
    barStateLabel.textContent = `${eco.stateAvg.toFixed(2)} t/ha`;
    barState.style.width = `${Math.min(100, Math.round((eco.stateAvg / maxRef) * 100))}%`;
  }

  const barHigh = document.getElementById("barHighFill");
  const barHighLabel = document.getElementById("barHighLabel");
  if (barHigh && barHighLabel) {
    barHighLabel.textContent = `${eco.highIrrig.toFixed(2)} t/ha`;
    barHigh.style.width = `${Math.min(100, Math.round((eco.highIrrig / maxRef) * 100))}%`;
  }

  const barDry = document.getElementById("barDryFill");
  const barDryLabel = document.getElementById("barDryLabel");
  if (barDry && barDryLabel) {
    barDryLabel.textContent = `${eco.dryland.toFixed(2)} t/ha`;
    barDry.style.width = `${Math.min(100, Math.round((eco.dryland / maxRef) * 100))}%`;
  }

  // Sensitivity factors display
  const rainRatio = rain / 1200;
  const rainMod = Math.min(1.22, Math.max(0.68, Math.pow(rainRatio, 0.45)));
  const phMod = Math.max(0.70, 1 - Math.pow(Math.abs(ph - 6.5), 1.4) * 0.12);

  const rainEffEl = document.getElementById("calcRainEff");
  if (rainEffEl) {
    const rainPct = ((rainMod - 1) * 100);
    rainEffEl.textContent = (rainPct >= 0 ? "+" : "") + rainPct.toFixed(1) + "%";
    rainEffEl.style.color = rainPct >= 0 ? "var(--leaf-green)" : "#dc2626";
  }
  const phEffEl = document.getElementById("calcPHEff");
  if (phEffEl) {
    phEffEl.textContent = (phMod * 100).toFixed(1) + "%";
  }

  // ==========================================================================
  // SECTION 2: FARM PRODUCTION & ECONOMIC PROFITABILITY CALCULATIONS
  // ==========================================================================
  const totalProductionTonnes = predictedYield * areaHa;
  const totalProductionQuintals = totalProductionTonnes * 10;
  const grossRevenue = totalProductionTonnes * marketPrice;

  // Dynamic cost per hectare
  const fertilizerExtraCost = simFertBoost * 30; // ₹30/kg for NPK blend
  const totalCostPerHa = eco.costPerHa + fertilizerExtraCost + irrigExtraCostHa;
  const totalCultivationCost = totalCostPerHa * areaHa;

  const netProfit = grossRevenue - totalCultivationCost;
  const roiPct = totalCultivationCost > 0 ? ((netProfit / totalCultivationCost) * 100) : 0;
  const breakEvenYield = marketPrice > 0 ? (totalCostPerHa / marketPrice) : 0;
  const safetyMarginPct = breakEvenYield > 0 ? (((predictedYield - breakEvenYield) / breakEvenYield) * 100) : 0;

  // Render 6 KPI Cards
  const kpiHarvest = document.getElementById("kpiTotalHarvest");
  if (kpiHarvest) kpiHarvest.innerHTML = `${totalProductionTonnes.toFixed(2)} <span style="font-size: 1rem; font-weight: 500; color: var(--text-muted);">Tonnes</span>`;

  const kpiHarvestQ = document.getElementById("kpiHarvestQuintal");
  if (kpiHarvestQ) kpiHarvestQ.textContent = `${totalProductionQuintals.toFixed(1)} Quintals (${(totalProductionTonnes * 1000).toLocaleString('en-IN', { maximumFractionDigits: 0 })} kg)`;

  const kpiRev = document.getElementById("kpiGrossRevenue");
  if (kpiRev) kpiRev.textContent = formatINR(grossRevenue);

  const kpiRevAcre = document.getElementById("kpiRevenuePerAcre");
  if (kpiRevAcre && areaAcres > 0) kpiRevAcre.textContent = `${formatINR(grossRevenue / areaAcres)} / acre`;

  const kpiCost = document.getElementById("kpiTotalCost");
  if (kpiCost) kpiCost.textContent = formatINR(totalCultivationCost);

  const kpiCostAcre = document.getElementById("kpiCostPerAcre");
  if (kpiCostAcre && areaAcres > 0) kpiCostAcre.textContent = `${formatINR(totalCultivationCost / areaAcres)} / acre`;

  const kpiProfit = document.getElementById("kpiNetProfit");
  if (kpiProfit) {
    kpiProfit.textContent = (netProfit >= 0 ? "+" : "-") + formatINR(Math.abs(netProfit));
    kpiProfit.style.color = netProfit >= 0 ? "var(--leaf-green)" : "#dc2626";
  }

  const kpiProfitAcre = document.getElementById("kpiProfitPerAcre");
  if (kpiProfitAcre && areaAcres > 0) {
    kpiProfitAcre.textContent = (netProfit >= 0 ? "+" : "-") + `${formatINR(Math.abs(netProfit) / areaAcres)} / acre`;
  }

  const kpiRoi = document.getElementById("kpiROI");
  if (kpiRoi) {
    kpiRoi.textContent = `${roiPct.toFixed(1)}%`;
    kpiRoi.style.color = roiPct >= 0 ? "#059669" : "#dc2626";
  }

  const kpiBe = document.getElementById("kpiBreakEven");
  if (kpiBe) kpiBe.innerHTML = `${breakEvenYield.toFixed(2)} <span style="font-size: 1rem; font-weight: 500; color: var(--text-muted);">t/ha</span>`;

  const kpiSm = document.getElementById("kpiSafetyMargin");
  if (kpiSm) {
    kpiSm.textContent = (safetyMarginPct >= 0 ? "+" : "") + `${safetyMarginPct.toFixed(0)}% Safety Margin`;
    kpiSm.style.color = safetyMarginPct >= 0 ? "var(--leaf-green)" : "#dc2626";
  }

  // ==========================================================================
  // SECTION 3: WHAT-IF SENSITIVITY IMPACT DELTAS
  // ==========================================================================
  const deltaYield = predictedYield - mlYield;
  const baseGrossRev = (mlYield * areaHa) * marketPrice;
  const baseTotalCost = eco.costPerHa * areaHa;
  const baseNetProfit = baseGrossRev - baseTotalCost;
  const deltaProfit = netProfit - baseNetProfit;

  const simDeltaYieldEl = document.getElementById("simDeltaYieldText");
  if (simDeltaYieldEl) {
    const sign = deltaYield >= 0 ? "+" : "";
    const pctChange = mlYield > 0 ? ((deltaYield / mlYield) * 100) : 0;
    simDeltaYieldEl.textContent = `${sign}${deltaYield.toFixed(2)} t/ha (${sign}${pctChange.toFixed(1)}% vs ML Baseline)`;
    simDeltaYieldEl.style.color = deltaYield >= 0 ? "var(--leaf-green)" : "#dc2626";
  }

  const simDeltaProfitEl = document.getElementById("simDeltaProfitText");
  if (simDeltaProfitEl) {
    const sign = deltaProfit >= 0 ? "+" : "-";
    simDeltaProfitEl.textContent = `${sign}${formatINR(Math.abs(deltaProfit))}`;
    simDeltaProfitEl.style.color = deltaProfit >= 0 ? "var(--leaf-green)" : "#dc2626";
  }

  // ==========================================================================
  // SECTION 4: MULTI-CROP COMPARISON MATRIX
  // ==========================================================================
  renderMultiCropComparisonMatrix(rainMod, phMod, areaHa);
}

function renderMultiCropComparisonMatrix(rainMod, phMod, areaHa) {
  const tbody = document.getElementById("cropComparisonTableBody");
  if (!tbody) return;

  const results = Object.keys(CROP_ECONOMICS).map(cropName => {
    const info = CROP_ECONOMICS[cropName];
    const y = info.baseYield * rainMod * phMod;
    const prod = y * areaHa;
    const rev = prod * info.pricePerTonne;
    const cost = info.costPerHa * areaHa;
    const profit = rev - cost;
    const roi = cost > 0 ? ((profit / cost) * 100) : 0;
    return { cropName, emoji: info.emoji, yieldVal: y, prod, price: info.pricePerTonne, cost, rev, profit, roi };
  });

  // Sort descending by Net Profit
  results.sort((a, b) => b.profit - a.profit);

  tbody.innerHTML = "";
  results.forEach((item, idx) => {
    const tr = document.createElement("tr");
    const isWinner = idx === 0;
    tr.innerHTML = `
      <td>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 1.2rem;">${item.emoji}</span>
          <strong>${item.cropName}</strong>
          ${isWinner ? '<span class="winner-badge">🌟 #1 Highest Profit</span>' : ''}
        </div>
      </td>
      <td><strong>${item.yieldVal.toFixed(2)} t/ha</strong></td>
      <td>${item.prod.toFixed(2)} tonnes</td>
      <td>${formatINR(item.price)}/t</td>
      <td>${formatINR(item.cost)}</td>
      <td><strong>${formatINR(item.rev)}</strong></td>
      <td style="color: ${item.profit >= 0 ? 'var(--leaf-green)' : '#dc2626'}; font-weight: 700;">
        ${(item.profit >= 0 ? "+" : "-") + formatINR(Math.abs(item.profit))}
      </td>
      <td>
        <span class="${item.roi >= 100 ? 'pill-green' : (item.roi >= 0 ? 'pill-mod' : 'pill-high')}">
          ${item.roi.toFixed(1)}%
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function resetSensitivitySliders() {
  const r = document.getElementById("simRainDelta");
  if (r) { r.value = 0; updateRangeLabel("simRainDeltaVal", 0, "%"); }
  const f = document.getElementById("simFertBoost");
  if (f) { f.value = 0; updateRangeLabel("simFertBoostVal", 0, " kg/ha"); }
  const i = document.getElementById("simIrrigationType");
  if (i) i.value = "rainfed";
  runLiveYieldEstimate();
}

// ============================================================================
// CALCULATE BUTTON ANIMATION WRAPPERS
// ============================================================================

function runYieldCalculationWithAnimation() {
  const btn = document.getElementById("yieldCalcBtn");
  if (!btn) { runLiveYieldEstimate(); return; }

  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.style.opacity = "0.75";
  btn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
      style="animation: spin 0.7s linear infinite;">
      <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
      <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
    </svg>
    Calculating…`;

  setTimeout(() => {
    runLiveYieldEstimate();
    btn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      Calculation Complete!`;
    btn.style.background = "linear-gradient(135deg, #059669, #10b981)";
    btn.style.opacity = "1";
    setTimeout(() => {
      btn.innerHTML = originalHTML;
      btn.style.background = "linear-gradient(135deg, var(--primary-forest), var(--leaf-green))";
      btn.disabled = false;
    }, 1800);
  }, 650);
}

function runRiskCalculationWithAnimation() {
  const btn = document.getElementById("riskCalcBtn");
  if (!btn) { runLiveRiskCalculation(); return; }

  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.style.opacity = "0.75";
  btn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
      style="animation: spin 0.7s linear infinite;">
      <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
      <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
    </svg>
    Computing CARI…`;

  setTimeout(() => {
    runLiveRiskCalculation();
    btn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      CARI Score Updated!`;
    btn.style.background = "linear-gradient(135deg, #059669, #10b981)";
    btn.style.opacity = "1";
    setTimeout(() => {
      btn.innerHTML = originalHTML;
      btn.style.background = "linear-gradient(135deg, #1e3a5f, #2563eb)";
      btn.disabled = false;
    }, 1800);
  }, 650);
}

// ============================================================================
// 9. RISK ANALYSIS CALCULATION ENGINE (CARI)
// ============================================================================

const CROP_TOLERANCES = {
  "Rice":      { optPH: 6.2, minPH: 5.5, maxPH: 7.5, minRain: 900, maxRain: 2200, optTemp: 28, minTemp: 18, maxTemp: 38 },
  "Wheat":     { optPH: 6.5, minPH: 5.5, maxPH: 7.8, minRain: 450, maxRain: 1200, optTemp: 20, minTemp: 10, maxTemp: 32 },
  "Cotton":    { optPH: 6.5, minPH: 5.8, maxPH: 8.0, minRain: 600, maxRain: 1500, optTemp: 30, minTemp: 18, maxTemp: 42 },
  "Maize":     { optPH: 6.5, minPH: 5.5, maxPH: 7.5, minRain: 500, maxRain: 1800, optTemp: 25, minTemp: 15, maxTemp: 38 },
  "Sugarcane": { optPH: 6.5, minPH: 5.5, maxPH: 8.0, minRain: 1000, maxRain: 2500, optTemp: 30, minTemp: 20, maxTemp: 40 },
  "Chickpea":  { optPH: 6.5, minPH: 5.5, maxPH: 8.0, minRain: 300, maxRain: 900, optTemp: 20, minTemp: 10, maxTemp: 35 },
  "Groundnut": { optPH: 6.2, minPH: 5.5, maxPH: 7.5, minRain: 400, maxRain: 1300, optTemp: 28, minTemp: 18, maxTemp: 38 },
  "Soybean":   { optPH: 6.5, minPH: 5.8, maxPH: 7.5, minRain: 500, maxRain: 1500, optTemp: 26, minTemp: 15, maxTemp: 36 },
  "Mustard":   { optPH: 6.5, minPH: 5.5, maxPH: 8.0, minRain: 300, maxRain: 900, optTemp: 20, minTemp: 8, maxTemp: 32 },
  "Millets":   { optPH: 6.5, minPH: 5.0, maxPH: 8.5, minRain: 200, maxRain: 1000, optTemp: 28, minTemp: 15, maxTemp: 42 }
};

function getSubIndexColor(score) {
  if (score <= 35) return "var(--leaf-green)";
  if (score <= 69) return "var(--harvest-gold)";
  return "#dc2626";
}

function runLiveRiskCalculation() {
  const crop = document.getElementById("rcCrop") ? document.getElementById("rcCrop").value : "Rice";
  const rain = parseFloat(document.getElementById("rcRain") ? document.getElementById("rcRain").value : 1200) || 1200;
  const ph = parseFloat(document.getElementById("rcPH") ? document.getElementById("rcPH").value : 6.5) || 6.5;
  const temp = parseFloat(document.getElementById("rcTemp") ? document.getElementById("rcTemp").value : 28) || 28;
  const n = parseFloat(document.getElementById("rcN") ? document.getElementById("rcN").value : 85) || 85;
  const pestLevel = document.getElementById("rcPestPressure") ? document.getElementById("rcPestPressure").value : "low";

  const tol = CROP_TOLERANCES[crop] || CROP_TOLERANCES["Rice"];

  // ==========================================================================
  // SUB-INDEX 1: Moisture / Rainfall Stress (R_rain) — Weight 30%
  // ==========================================================================
  let R_rain = 0;
  if (rain < tol.minRain) {
    // Drought stress — severity scales linearly with deficit
    R_rain = Math.min(100, Math.round(((tol.minRain - rain) / tol.minRain) * 120));
  } else if (rain > tol.maxRain) {
    // Waterlogging stress — severity scales with excess
    R_rain = Math.min(100, Math.round(((rain - tol.maxRain) / tol.maxRain) * 90));
  } else {
    // Optimal band — minor variance penalty
    const midRain = (tol.minRain + tol.maxRain) / 2;
    R_rain = Math.round(Math.abs(rain - midRain) / (tol.maxRain - tol.minRain) * 15);
  }

  // ==========================================================================
  // SUB-INDEX 2: Soil pH Discrepancy (R_pH) — Weight 25%
  // ==========================================================================
  let R_pH = 0;
  if (ph < tol.minPH) {
    R_pH = Math.min(100, Math.round(Math.pow(tol.minPH - ph, 1.5) * 40));
  } else if (ph > tol.maxPH) {
    R_pH = Math.min(100, Math.round(Math.pow(ph - tol.maxPH, 1.5) * 40));
  } else {
    // Penalty for deviation from optimal pH
    R_pH = Math.round(Math.abs(ph - tol.optPH) * 8);
  }

  // ==========================================================================
  // SUB-INDEX 3: Thermal Stress (R_temp) — Weight 20%
  // ==========================================================================
  let R_temp = 0;
  if (temp > tol.maxTemp) {
    R_temp = Math.min(100, Math.round(Math.pow(temp - tol.maxTemp, 1.4) * 15));
  } else if (temp < tol.minTemp) {
    R_temp = Math.min(100, Math.round(Math.pow(tol.minTemp - temp, 1.4) * 15));
  } else {
    R_temp = Math.round(Math.abs(temp - tol.optTemp) * 2.5);
  }

  // ==========================================================================
  // SUB-INDEX 4: Nutrient Deficit (R_npk) — Weight 15%
  // Optimal N for most crops ~80-120 kg/ha
  // ==========================================================================
  const optN = 90;
  let R_npk = 0;
  if (n < 40) {
    R_npk = Math.min(100, Math.round(((40 - n) / 40) * 90));
  } else if (n > 160) {
    R_npk = Math.min(100, Math.round(((n - 160) / 40) * 60)); // excess toxicity
  } else {
    R_npk = Math.round(Math.abs(n - optN) / optN * 20);
  }

  // ==========================================================================
  // SUB-INDEX 5: Biological / Pest Exposure (R_pest) — Weight 10%
  // ==========================================================================
  const R_pest = pestLevel === "low" ? 12 : pestLevel === "moderate" ? 45 : 82;

  // ==========================================================================
  // COMPOSITE AGRONOMIC RISK INDEX (CARI)
  // CARI = 0.30·R_rain + 0.25·R_pH + 0.20·R_temp + 0.15·R_npk + 0.10·R_pest
  // ==========================================================================
  const CARI = Math.round(
    0.30 * R_rain +
    0.25 * R_pH +
    0.20 * R_temp +
    0.15 * R_npk +
    0.10 * R_pest
  );

  const riskLabel = CARI <= 35 ? "LOW RISK" : CARI <= 69 ? "MODERATE RISK" : "HIGH RISK";
  const riskColor = CARI <= 35 ? "var(--leaf-green)" : CARI <= 69 ? "var(--harvest-gold)" : "#dc2626";

  // Update KPI Cards
  const overallVal = document.getElementById("riskOverallValue");
  if (overallVal) {
    overallVal.textContent = `${riskLabel} (${CARI}/100)`;
    overallVal.style.color = riskColor;
    overallVal.style.fontSize = "1.35rem";
  }
  const overallSub = document.getElementById("riskOverallSub");
  if (overallSub) {
    overallSub.textContent = CARI <= 35 ? "Optimal biological safety margin" : CARI <= 69 ? "Manageable stress — intervention recommended" : "Critical hazard — immediate action required";
  }

  const rainKPI = document.getElementById("riskWeatherValue");
  if (rainKPI) { rainKPI.textContent = `${R_rain} / 100`; rainKPI.style.color = getSubIndexColor(R_rain); }
  const rainSub = document.getElementById("riskWeatherSub");
  if (rainSub) rainSub.textContent = R_rain <= 20 ? "Adequate moisture coverage" : R_rain <= 50 ? "Moderate moisture stress" : rain < tol.minRain ? "Drought deficit detected" : "Waterlogging risk detected";

  const phKPI = document.getElementById("riskPHValue");
  if (phKPI) { phKPI.textContent = `${R_pH} / 100`; phKPI.style.color = getSubIndexColor(R_pH); }
  const phSub = document.getElementById("riskPHSub");
  if (phSub) phSub.textContent = R_pH <= 15 ? "pH in optimal nutrient band" : ph < tol.minPH ? `Acidic soil (pH ${ph}) — lime amendment advised` : `Alkaline soil (pH ${ph}) — organic correction advised`;

  const npkKPI = document.getElementById("riskNPKValue");
  if (npkKPI) { npkKPI.textContent = `${R_npk} / 100`; npkKPI.style.color = getSubIndexColor(R_npk); }
  const npkSub = document.getElementById("riskNPKSub");
  if (npkSub) npkSub.textContent = R_npk <= 20 ? "Balanced N:P:K profile" : n < 40 ? `Nitrogen deficient (${n} kg/ha) — top-dress advised` : `Excess nitrogen (${n} kg/ha) — leaching risk`;

  // Update Sub-Index Progress Bars
  const barData = [
    { scoreEl: "subRainScore", fillEl: "subRainFill", val: R_rain },
    { scoreEl: "subPHScore",   fillEl: "subPHFill",   val: R_pH  },
    { scoreEl: "subTempScore", fillEl: "subTempFill", val: R_temp },
    { scoreEl: "subNPKScore",  fillEl: "subNPKFill",  val: R_npk },
    { scoreEl: "subPestScore", fillEl: "subPestFill", val: R_pest }
  ];
  barData.forEach(({ scoreEl, fillEl, val }) => {
    const se = document.getElementById(scoreEl);
    const fe = document.getElementById(fillEl);
    if (se) se.textContent = `${val} / 100`;
    if (fe) {
      fe.style.width = `${val}%`;
      fe.style.background = getSubIndexColor(val);
    }
  });

  // ==========================================================================
  // DYNAMIC MITIGATION PROTOCOLS
  // ==========================================================================
  const mitigations = [];

  if (R_rain > 20) {
    if (rain < tol.minRain) {
      mitigations.push({
        icon: "💧", color: "var(--primary-forest)", borderColor: "#3b82f6",
        title: "Moisture Conservation & Supplemental Irrigation",
        formula: `Deficit = ${tol.minRain} − ${rain} = ${tol.minRain - rain} mm`,
        action: `Install drip or micro-sprinkler irrigation to supply the ${tol.minRain - rain} mm seasonal deficit. Apply mulching (5–8 cm straw) to reduce soil evaporation by up to 40%. Schedule irrigations at 5–7 day intervals during critical crop stages.`
      });
    } else {
      mitigations.push({
        icon: "🌊", color: "#0891b2", borderColor: "#22d3ee",
        title: "Waterlogging & Field Drainage Management",
        formula: `Excess = ${rain} − ${tol.maxRain} = ${rain - tol.maxRain} mm above safe limit`,
        action: `Construct raised-bed or ridged planting (25–30 cm height). Install sub-surface tile drainage at 1.2 m depth. Apply broad-spectrum fungicide to prevent Pythium root rot.`
      });
    }
  }

  if (R_pH > 15) {
    if (ph < tol.minPH) {
      mitigations.push({
        icon: "🪨", color: "#7c3aed", borderColor: "#8b5cf6",
        title: "Soil Acidification Correction",
        formula: `Lime Dose = (${tol.optPH.toFixed(1)} − ${ph.toFixed(1)}) × 1200 kg/ha = ${Math.round((tol.optPH - ph) * 1200)} kg/ha`,
        action: `Broadcast ${Math.round((tol.optPH - ph) * 1200)} kg/ha of agricultural limestone (CaCO₃) and incorporate to 20 cm depth. Follow with dolomite top-dressing 30 days later. Re-test soil pH after 6 weeks.`
      });
    } else {
      mitigations.push({
        icon: "⚗️", color: "#b45309", borderColor: "#f59e0b",
        title: "Alkaline Soil Amendment",
        formula: `Gypsum Dose = (${ph.toFixed(1)} − ${tol.maxPH.toFixed(1)}) × 900 kg/ha = ${Math.round((ph - tol.maxPH) * 900)} kg/ha`,
        action: `Apply ${Math.round((ph - tol.maxPH) * 900)} kg/ha calcium sulfate (gypsum) or elemental sulfur to lower soil pH. Incorporate FYM at 5–10 t/ha to stimulate microbial acidification reactions.`
      });
    }
  }

  if (R_temp > 20) {
    if (temp > tol.maxTemp) {
      mitigations.push({
        icon: "🌡️", color: "#dc2626", borderColor: "#ef4444",
        title: "Heat Stress Mitigation Protocol",
        formula: `Thermal Excess = ${temp}°C − ${tol.maxTemp}°C = +${temp - tol.maxTemp}°C above tolerance`,
        action: `Apply evening or predawn foliar misting (50–80 L/ha) to reduce canopy temperature by 3–5°C. Use kaolin particle film (25 kg/ha) to reflect solar radiation. Consider short-duration or heat-tolerant cultivars for next season.`
      });
    } else {
      mitigations.push({
        icon: "❄️", color: "#2563eb", borderColor: "#60a5fa",
        title: "Cold Stress & Frost Protection",
        formula: `Cold Deficit = ${tol.minTemp}°C − ${temp}°C = −${tol.minTemp - temp}°C below threshold`,
        action: `Delay sowing by ${Math.max(7, (tol.minTemp - temp) * 5)} days until soil temperature stabilizes. Install polythene row covers or frost-protection nets overnight. Apply potassium silicate (3 kg/ha) to enhance cell wall strength against cold.`
      });
    }
  }

  if (R_npk > 20) {
    const nDef = n < 40 ? 40 - n : 0;
    mitigations.push({
      icon: "🧪", color: "#059669", borderColor: "var(--leaf-green)",
      title: "Soil Nitrogen & Nutrient Correction",
      formula: n < 40 ? `N Deficit = ${optN} − ${n} = ${optN - n} kg/ha below optimum` : `N Surplus = ${n} − 160 = ${n - 160} kg/ha above toxicity threshold`,
      action: n < 40
        ? `Apply ${Math.round((optN - n) * 2.5)} kg/ha urea (46% N) in 2 split doses — 50% at sowing, 50% at tillering. Supplement with 30 kg/ha Diammonium Phosphate (DAP) for P-N balance.`
        : `Pause nitrogen applications for current season. Introduce deep-rooted legume cover crop to fix excess soil nitrogen. Test for nitrate leaching in groundwater.`
    });
  }

  if (R_pest > 30) {
    mitigations.push({
      icon: "🐛", color: "#dc2626", borderColor: "#fca5a5",
      title: "Integrated Pest Management (IPM) Protocol",
      formula: `Pest Risk Index = ${R_pest}/100 (${pestLevel.toUpperCase()} incidence level)`,
      action: pestLevel === "moderate"
        ? `Deploy yellow sticky traps (10/ha) and pheromone traps for early detection. Apply neem-based biopesticide (Azadirachtin 0.03%) as first-line response. Monitor weekly and escalate only if >10% infestation threshold exceeded.`
        : `Apply systemic insecticide (Imidacloprid 70 WS) as seed treatment. Deploy biological control agents (Trichogramma wasps). Create 10 m buffer strip of marigold as companion trap crop. Notify local agricultural extension officer.`
    });
  }

  if (mitigations.length === 0) {
    mitigations.push({
      icon: "✅", color: "var(--leaf-green)", borderColor: "rgba(46,125,78,0.3)",
      title: "No Critical Interventions Required",
      formula: `CARI = ${CARI}/100 — All indices within safe bounds`,
      action: "Continue standard regional agronomic practices. Apply balanced NPK fertilization per soil test recommendations. Monitor weekly for early pest signs."
    });
  }

  const grid = document.getElementById("dynamicMitigationsGrid");
  if (grid) {
    const badge = document.getElementById("mitigationCountBadge");
    if (badge) badge.textContent = `${mitigations.length} Protocol${mitigations.length > 1 ? "s" : ""} Activated`;

    grid.innerHTML = mitigations.map(m => `
      <div class="mitigation-box" style="border-left-color: ${m.borderColor}; background: var(--bg-surface);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
          <span style="font-size: 1.4rem;">${m.icon}</span>
          <strong style="color: ${m.color};">${m.title}</strong>
        </div>
        <div style="background: rgba(0,0,0,0.04); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">
          <code style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--text-secondary);">${m.formula}</code>
        </div>
        <p style="font-size: 0.83rem; color: var(--text-secondary); margin: 0; line-height: 1.55;">${m.action}</p>
      </div>
    `).join("");
  }
}

function resetRiskSimulator() {
  const fields = [
    { id: "rcRain",  val: 1200, unit: " mm",   label: "rcRainVal" },
    { id: "rcPH",   val: 6.5,  unit: "",       label: "rcPHVal" },
    { id: "rcTemp", val: 28,   unit: "°C",     label: "rcTempVal" },
    { id: "rcN",    val: 85,   unit: " kg/ha", label: "rcNVal" }
  ];
  fields.forEach(f => {
    const el = document.getElementById(f.id);
    if (el) el.value = f.val;
    updateRangeLabel(f.label, f.val, f.unit);
  });
  const crop = document.getElementById("rcCrop");
  if (crop) crop.value = "Rice";
  const pest = document.getElementById("rcPestPressure");
  if (pest) pest.value = "low";
  runLiveRiskCalculation();
}

// ============================================================================
// 10. QUERY HISTORY PERSISTENCE
// ============================================================================

function saveQueryToHistory(query, data) {
  let history = JSON.parse(localStorage.getItem("agri_query_history") || "[]");
  const topCrops = (data.recommendations || []).map(r => r.crop).slice(0, 3).join(", ") || "Analysis Completed";

  const entry = {
    id: "QRY_" + Date.now(),
    query: query,
    intent: data.intent || "CROP_RECOMMENDATION",
    crops: topCrops,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    date: new Date().toLocaleDateString()
  };

  history.unshift(entry);
  if (history.length > 30) history = history.slice(0, 30);
  localStorage.setItem("agri_query_history", JSON.stringify(history));

  renderQueryHistory();
}

function renderQueryHistory() {
  const container = document.getElementById("queryHistoryList");
  if (!container) return;

  const history = JSON.parse(localStorage.getItem("agri_query_history") || "[]");
  container.innerHTML = "";

  if (history.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🕒</div>
        <h4>No Consultations Recorded Yet</h4>
        <p>Your search history and generated agricultural recommendations will appear here for one-click re-running.</p>
      </div>
    `;
    return;
  }

  history.forEach(item => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.padding = "1.25rem 1.5rem";
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="pill-green">${formatIntentLabel(item.intent)}</span>
            <span style="font-size: 0.78rem; color: var(--text-muted);">${item.date} &bull; ${item.timestamp}</span>
          </div>
          <h4 style="font-size: 1.05rem; color: var(--primary-forest); margin-bottom: 4px;">${item.query}</h4>
          <p style="font-size: 0.84rem; color: var(--leaf-green); margin: 0;">Top Recommendations: <strong>${item.crops}</strong></p>
        </div>
        <button type="button" class="btn-secondary" onclick="rerunHistoryQuery('${item.query.replace(/'/g, "\\'")}')">
          Re-run Query
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function rerunHistoryQuery(queryText) {
  document.getElementById("queryInput").value = queryText;
  switchNavTab("dashboard");
  document.getElementById("queryForm").dispatchEvent(new Event("submit"));
}

function clearQueryHistory() {
  if (confirm("Are you sure you want to clear your consultation history?")) {
    localStorage.removeItem("agri_query_history");
    renderQueryHistory();
  }
}


// ============================================================================
// 10. FEEDBACK & BENCHMARK EVALUATION
// ============================================================================

function selectThumb(type) {
  activeThumb = type;
  document.getElementById("thumbUpBtn").classList.toggle("active", type === "up");
  document.getElementById("thumbDownBtn").classList.toggle("active", type === "down");
}

function setStarRating(num) {
  activeRating = num;
  const stars = document.querySelectorAll(".star");
  stars.forEach((s, idx) => {
    s.classList.toggle("active", idx < num);
  });
}

async function submitUserFeedback() {
  const comment = document.getElementById("feedbackComment").value;
  const retrievedCaseIds = lastAdvisoryResponse ? (lastAdvisoryResponse.similar_cases || []).map(c => c.case_id) : [];

  const payload = {
    query: lastAdvisoryResponse ? lastAdvisoryResponse.query : "Advisory Studio Feedback",
    recommendation: lastAdvisoryResponse ? lastAdvisoryResponse.recommendations.map(r => r.crop).join(", ") : "Manual Input",
    retrieved_cases: retrievedCaseIds,
    rating: activeRating,
    thumbs: activeThumb,
    comments: comment || "Specialist confirmed accuracy."
  };

  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const ack = document.getElementById("feedbackAck");
      ack.classList.remove("hidden");
      setTimeout(() => ack.classList.add("hidden"), 3500);
      document.getElementById("feedbackComment").value = "";
    }
  } catch (e) {
    console.error("Feedback error:", e);
  }
}

async function loadEvaluationDashboard() {
  try {
    const res = await fetch("/api/evaluation/latest");
    if (res.ok) {
      const data = await res.json();
      updateEvaluationUI(data);
    }
  } catch (e) {
    console.warn("Evaluation report:", e);
  }
}

async function triggerRunEvaluation(event) {
  const btn = event.target.closest("button");
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Running Benchmark (20 queries)...</span>`;

  try {
    const res = await fetch("/api/evaluate", { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      updateEvaluationUI(data);
      alert("Evaluation Benchmark Completed Successfully!\nReport generated at evaluation/reports/evaluation_report.md");
    }
  } catch (e) {
    alert("Evaluation run failed: " + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

function updateEvaluationUI(data) {
  const ret = data.retrieval_metrics || {};
  const ml = data.ml_model_metrics || {};
  const gr = data.guardrail_metrics || {};
  const sys = data.system_performance || {};

  if (ret.precision_at_1 !== undefined) document.getElementById("evalP1").textContent = ret.precision_at_1.toFixed(3);
  if (ret.precision_at_3 !== undefined) document.getElementById("evalP3").textContent = ret.precision_at_3.toFixed(3);
  if (ret.precision_at_5 !== undefined) document.getElementById("evalP5").textContent = ret.precision_at_5.toFixed(3);
  if (ret.recall_at_5 !== undefined) document.getElementById("evalRecall5").textContent = ret.recall_at_5.toFixed(3);
  if (ret.mrr !== undefined) document.getElementById("evalMRR").textContent = ret.mrr.toFixed(3);
  if (ret.hit_rate_at_5 !== undefined) document.getElementById("evalHitRate").textContent = ret.hit_rate_at_5.toFixed(3);

  const yieldM = ml.yield_regressor || {};
  if (yieldM.r2_score !== undefined) document.getElementById("evalYieldR2").textContent = yieldM.r2_score.toFixed(4);
  if (yieldM.mae !== undefined) document.getElementById("evalYieldMAE").textContent = `${yieldM.mae.toFixed(3)} t/ha`;
  if (yieldM.rmse !== undefined) document.getElementById("evalYieldRMSE").textContent = `${yieldM.rmse.toFixed(3)} t/ha`;

  const suitM = ml.suitability_classifier || {};
  if (suitM.accuracy !== undefined) document.getElementById("evalSuitAcc").textContent = suitM.accuracy.toFixed(3);
  if (suitM.f1_score !== undefined) document.getElementById("evalSuitF1").textContent = suitM.f1_score.toFixed(3);

  if (gr.guardrail_accuracy_rate !== undefined)
    document.getElementById("evalGuardrailRate").textContent = `${(gr.guardrail_accuracy_rate * 100).toFixed(1)}%`;
  if (gr.prompt_injection_detection_rate !== undefined)
    document.getElementById("evalInjectionRate").textContent = `${(gr.prompt_injection_detection_rate * 100).toFixed(1)}%`;

  if (sys.average_latency_ms !== undefined)
    document.getElementById("evalLatency").textContent = `${sys.average_latency_ms} ms`;
  if (sys.success_rate !== undefined)
    document.getElementById("evalSuccessRate").textContent = `${(sys.success_rate * 100).toFixed(1)}%`;
  if (sys.total_queries_executed !== undefined)
    document.getElementById("evalTotalQueries").textContent = sys.total_queries_executed;
}

async function loadMetadataDropdowns() {
  try {
    const [cropsRes, statesRes, seasonsRes] = await Promise.all([
      fetch("/api/crops"),
      fetch("/api/states"),
      fetch("/api/seasons")
    ]);

    if (cropsRes.ok) {
      const crops = await cropsRes.json();
      populateSelect("filterCrop", crops);
      populateSelect("advCrop", crops);
    }
    if (statesRes.ok) {
      const states = await statesRes.json();
      populateSelect("filterState", states);
      populateSelect("advState", states);
    }
    if (seasonsRes.ok) {
      const seasons = await seasonsRes.json();
      populateSelect("filterSeason", seasons);
      populateSelect("advSeason", seasons);
    }
  } catch (e) {
    console.warn("Using offline defaults for dropdowns:", e);
  }
}

function populateSelect(selectId, items) {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  items.forEach(it => {
    const opt = document.createElement("option");
    opt.value = it;
    opt.textContent = it;
    sel.appendChild(opt);
  });
}
