/**
 * Mitra AI Mentor Chatbot Widget
 * Embedded floating conversational placement assistant with Gemini Live & Offline Knowledge Engine
 */

(function () {
    // Inject Styles for the Chatbot Widget
    const style = document.createElement('style');
    style.id = 'ai-mentor-styles';
    style.innerHTML = `
        #ai-mentor-fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 9999;
            box-shadow: 0 10px 25px -5px rgba(109, 40, 217, 0.4), 0 8px 10px -6px rgba(109, 40, 217, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        #ai-mentor-fab:hover {
            transform: scale(1.06);
            box-shadow: 0 20px 30px -10px rgba(109, 40, 217, 0.6);
        }
        #ai-mentor-window {
            position: fixed;
            bottom: 96px;
            right: 24px;
            width: 410px;
            max-width: calc(100vw - 32px);
            height: 640px;
            max-height: calc(100vh - 120px);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            border-radius: 24px;
            background: #ffffff;
            box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.3), 0 0 0 1px rgba(226, 232, 240, 0.9);
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            transform-origin: bottom right;
        }
        #ai-mentor-window.closed {
            opacity: 0;
            pointer-events: none;
            transform: scale(0.85) translateY(20px);
        }
        .mentor-msg-bubble {
            animation: fadeInMsg 0.22s ease-out;
            word-break: break-word;
        }
        @keyframes fadeInMsg {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .mentor-typing-dot {
            animation: mentorPulse 1.4s infinite ease-in-out both;
        }
        .mentor-typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .mentor-typing-dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes mentorPulse {
            0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }
        .carousel-hide-scroll::-webkit-scrollbar {
            display: none;
        }
        .carousel-hide-scroll {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    `;
    document.head.appendChild(style);

    // Get current student display info dynamically from AppState, DOM, or localStorage
    function getStudentInfo() {
        try {
            // 1. Check window.AppState.user if loaded
            if (window.AppState && window.AppState.user) {
                const u = window.AppState.user;
                const name = (u.full_name || u.name || '').trim();
                const cgpa = (u.profile && u.profile.cgpa) || u.cgpa;
                if (name) {
                    return cgpa ? `${name} • CGPA ${cgpa}` : `${name} • Placement Candidate`;
                }
            }
            // 2. Check localStorage 'user'
            const userJson = localStorage.getItem('user');
            if (userJson) {
                const u = JSON.parse(userJson);
                const name = (u.full_name || u.name || '').trim();
                const cgpa = (u.profile && u.profile.cgpa) || u.cgpa;
                if (name) {
                    return cgpa ? `${name} • CGPA ${cgpa}` : `${name} • Placement Candidate`;
                }
            }
            // 3. Check DOM header #userDisplayName
            const userDisplayEl = document.getElementById('userDisplayName');
            if (userDisplayEl && userDisplayEl.textContent && userDisplayEl.textContent.trim()) {
                const domName = userDisplayEl.textContent.trim();
                if (domName && !domName.toLowerCase().includes('candidate') && !domName.toLowerCase().includes('student')) {
                    return `${domName} • Placement Candidate`;
                }
            }
            // 4. Check userEmail from localStorage
            const email = localStorage.getItem('userEmail');
            if (email) {
                const cleanName = email.split('@')[0].replace(/[._]/g, ' ');
                const capName = cleanName.replace(/\b\w/g, c => c.toUpperCase());
                return `${capName} • Placement Candidate`;
            }
        } catch (e) {}
        return 'Placement Candidate • AI Mentor';
    }

    // Expose refresh function to window for immediate dynamic sync
    window.refreshMentorUserSubtitle = function() {
        const sub = document.getElementById('mentorSubtitle');
        if (sub) {
            sub.textContent = getStudentInfo();
        }
    };

    // Build Floating Action Button & Chat Window HTML
    const container = document.createElement('div');
    container.id = 'ai-mentor-container';
    container.innerHTML = `
        <!-- Floating Action Button -->
        <button id="ai-mentor-fab" class="bg-gradient-to-r from-purple-700 via-indigo-600 to-purple-800 text-white p-4 rounded-full flex items-center justify-center cursor-pointer group shadow-xl">
            <svg class="w-6 h-6 transition-transform group-hover:rotate-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="4" y="6" width="16" height="12" rx="3" stroke-width="2"></rect>
                <circle cx="9" cy="12" r="1.5" fill="currentColor"></circle>
                <circle cx="15" cy="12" r="1.5" fill="currentColor"></circle>
                <path d="M12 2v4M2 12h2M20 12h2" stroke-width="2" stroke-linecap="round"></path>
            </svg>
            <span class="absolute -top-1 -right-1 flex h-3.5 w-3.5">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white"></span>
            </span>
        </button>

        <!-- Slide-out Chat Window -->
        <div id="ai-mentor-window" class="closed flex flex-col font-sans">
            <!-- Header (Exact match to Mitra AI Mentor design) -->
            <div style="background: linear-gradient(135deg, #2A0845 0%, #4B1270 50%, #20073B 100%);" class="text-white px-4 py-3.5 flex items-center justify-between border-b border-purple-900/60 shadow-sm">
                <div class="flex items-center gap-3">
                    <!-- Robot Avatar -->
                    <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-fuchsia-600 to-indigo-600 flex items-center justify-center text-white shadow-md border border-white/20 shrink-0">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <rect x="4" y="7" width="16" height="11" rx="3" stroke-width="2"></rect>
                            <circle cx="9" cy="12.5" r="1.2" fill="currentColor"></circle>
                            <circle cx="15" cy="12.5" r="1.2" fill="currentColor"></circle>
                            <path d="M12 3v4M8 3h8M2 12.5h2M20 12.5h2" stroke-width="2" stroke-linecap="round"></path>
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h4 class="font-bold text-sm tracking-wide text-white">Mitra Al Mentor</h4>
                            <span class="px-2 py-0.5 rounded-full bg-purple-700/90 text-white text-[9px] font-extrabold tracking-wider border border-purple-400/40 shadow-sm">GEMINI LIVE</span>
                        </div>
                        <p id="mentorSubtitle" class="text-[11px] text-purple-200/90 font-medium">${getStudentInfo()}</p>
                    </div>
                </div>
                <div class="flex items-center gap-1.5">
                    <button id="ai-mentor-sparkle-btn" title="Explore AI Features" class="p-1.5 text-purple-200 hover:text-white hover:bg-white/10 rounded-lg transition cursor-pointer">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                        </svg>
                    </button>
                    <button id="ai-mentor-clear-btn" title="Clear Chat" class="p-1.5 text-purple-200 hover:text-white hover:bg-white/10 rounded-lg transition cursor-pointer">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                    <button id="ai-mentor-close-btn" title="Close" class="p-1.5 text-purple-200 hover:text-white hover:bg-white/10 rounded-lg transition cursor-pointer">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Horizontal Pill Carousel (Exact match to Image 1) -->
            <div class="bg-slate-100/90 border-b border-slate-200 px-2 py-2 flex items-center gap-1.5 shrink-0">
                <button id="carouselPrevBtn" class="w-6 h-6 rounded-full bg-white hover:bg-slate-200 text-slate-600 flex items-center justify-center shrink-0 shadow-xs transition text-xs font-bold cursor-pointer">
                    ◀
                </button>
                <div id="pillsCarousel" class="carousel-hide-scroll flex items-center gap-2 overflow-x-auto scroll-smooth py-0.5">
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="Can you explain the registration process and document verification requirements for placement drives?">
                        <span>📝</span> Registration Help
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="What are the eligibility criteria, CGPA cutoffs, and attendance requirements for Tier-1 companies?">
                        <span>🎯</span> Eligibility Criteria
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="Explain the 3-Round Sequential Pipeline and how gating works between Aptitude, Technical MCQ, and Mock Interview.">
                        <span>🔄</span> 3-Rounds Info
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="What are the 47 active placement drives, top companies, and package tiers available?">
                        <span>🏢</span> 47 Placement Drives
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="Give me essential tips for the AI Mock Interview: STAR method, eye gaze proctoring, and speech pacing.">
                        <span>📹</span> AI Mock Interview
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="How do I optimize my resume for ATS scoring and format technical skills with symbols?">
                        <span>📄</span> Resume Intelligence
                    </button>
                    <button class="mentor-chip px-3 py-1 bg-white hover:bg-purple-50 text-slate-700 hover:text-purple-700 border border-slate-200 hover:border-purple-300 rounded-full text-[11px] font-semibold transition shrink-0 shadow-2xs flex items-center gap-1.5 cursor-pointer" data-query="What are proven breathing techniques and 24-hour prep plans to manage placement stress and anxiety?">
                        <span>💖</span> Placement Stress & Anxiety
                    </button>
                </div>
                <button id="carouselNextBtn" class="w-6 h-6 rounded-full bg-white hover:bg-slate-200 text-slate-600 flex items-center justify-center shrink-0 shadow-xs transition text-xs font-bold cursor-pointer">
                    ▶
                </button>
            </div>

            <!-- Messages Area -->
            <div id="ai-mentor-messages" class="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/50 text-slate-800 text-xs">
                <!-- Welcome greeting with exact 4 bullets from Image 1 -->
                <div class="mentor-msg-bubble bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs space-y-3.5">
                    <ul class="space-y-2.5 text-slate-700 leading-relaxed text-[12px]">
                        <li class="flex items-start gap-2">
                            <span class="shrink-0 text-base">🎙️</span>
                            <div><strong class="text-slate-900 font-bold">AI Mock Interview Preparation:</strong> Tips on STAR answers, eye gaze proctoring, and speech pacing.</div>
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="shrink-0 text-base">📄</span>
                            <div><strong class="text-slate-900 font-bold">Resume Intelligence & ATS:</strong> Optimize keywords to pass Round 1 screening.</div>
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="shrink-0 text-base">🔄</span>
                            <div><strong class="text-slate-900 font-bold">3-Round Sequential Pipeline:</strong> Understand the progression from Aptitude to Mock Interview.</div>
                        </li>
                        <li class="flex items-start gap-2">
                            <span class="shrink-0 text-base">💖</span>
                            <div><strong class="text-slate-900 font-bold">Placement Stress & Anxiety:</strong> Proven breathing techniques and 24-hour prep plans.</div>
                        </li>
                    </ul>

                    <div class="pt-2 border-t border-slate-100">
                        <p class="font-bold text-slate-900 text-[12px]">What concern would you like to explore first?</p>
                        <p class="text-slate-500 text-[11px] mt-0.5">Choose a suggestion below or type your question!</p>
                    </div>

                    <!-- Action suggestion buttons matching Image 1 -->
                    <div class="flex flex-wrap gap-2 pt-1">
                        <button class="mentor-action-btn px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-[11px] font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-2xs" data-action="tab-interview">
                            <svg class="w-3.5 h-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                            </svg>
                            <span>AI Mock Interview</span>
                        </button>
                        <button class="mentor-action-btn px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-[11px] font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-2xs" data-action="tab-resume">
                            <svg class="w-3.5 h-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <span>Resume Intelligence</span>
                        </button>
                        <button class="mentor-action-btn px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-[11px] font-semibold transition flex items-center gap-1.5 cursor-pointer shadow-2xs" data-action="tab-placement">
                            <svg class="w-3.5 h-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                            </svg>
                            <span>Explore 47 Drives</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Footer / Input Box (Exact match to Image 1) -->
            <div class="p-3 bg-white border-t border-slate-200/80">
                <form id="ai-mentor-form" class="flex items-center gap-2">
                    <div class="flex-1 flex items-center border-2 border-indigo-500 rounded-full px-3.5 py-1.5 bg-white shadow-xs focus-within:ring-2 focus-within:ring-purple-200 transition">
                        <input type="text" id="ai-mentor-input" placeholder="Ask your doubt or concern..." autocomplete="off" class="flex-1 text-xs text-slate-800 placeholder-slate-400 outline-none bg-transparent" />
                        <button type="button" id="ai-mentor-mic-btn" title="Speak your question" class="p-1 text-slate-500 hover:text-indigo-600 transition cursor-pointer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                            </svg>
                        </button>
                    </div>
                    <button type="submit" id="ai-mentor-send-btn" class="w-9 h-9 bg-gradient-to-tr from-purple-700 to-indigo-600 hover:from-purple-800 hover:to-indigo-700 text-white rounded-full flex items-center justify-center shrink-0 shadow-md transition cursor-pointer">
                        <svg class="w-4 h-4 translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(container);

    // Elements
    const fab = document.getElementById('ai-mentor-fab');
    const win = document.getElementById('ai-mentor-window');
    const closeBtn = document.getElementById('ai-mentor-close-btn');
    const clearBtn = document.getElementById('ai-mentor-clear-btn');
    const sparkleBtn = document.getElementById('ai-mentor-sparkle-btn');
    const form = document.getElementById('ai-mentor-form');
    const input = document.getElementById('ai-mentor-input');
    const msgContainer = document.getElementById('ai-mentor-messages');
    const micBtn = document.getElementById('ai-mentor-mic-btn');
    const carousel = document.getElementById('pillsCarousel');
    const prevBtn = document.getElementById('carouselPrevBtn');
    const nextBtn = document.getElementById('carouselNextBtn');
    const subtitleEl = document.getElementById('mentorSubtitle');

    let chatHistory = [];

    // Carousel buttons
    if (prevBtn && carousel) {
        prevBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: -140, behavior: 'smooth' });
        });
    }
    if (nextBtn && carousel) {
        nextBtn.addEventListener('click', () => {
            carousel.scrollBy({ left: 140, behavior: 'smooth' });
        });
    }

    // Toggle window open / close
    fab.addEventListener('click', () => {
        win.classList.toggle('closed');
        if (!win.classList.contains('closed')) {
            if (subtitleEl) subtitleEl.textContent = getStudentInfo();
            input.focus();
        }
    });

    // Auto-sync subtitle after page load and auth session resolution
    setTimeout(() => { if (subtitleEl) subtitleEl.textContent = getStudentInfo(); }, 400);
    setTimeout(() => { if (subtitleEl) subtitleEl.textContent = getStudentInfo(); }, 1200);
    setTimeout(() => { if (subtitleEl) subtitleEl.textContent = getStudentInfo(); }, 2500);

    closeBtn.addEventListener('click', () => {
        win.classList.add('closed');
    });

    sparkleBtn.addEventListener('click', () => {
        sendMessage("What are the key placement modules and AI features in AI-TPMS?");
    });

    clearBtn.addEventListener('click', () => {
        msgContainer.innerHTML = `
            <div class="mentor-msg-bubble bg-white p-3.5 rounded-2xl border border-slate-200 shadow-xs text-slate-700 leading-relaxed">
                <p class="font-bold text-purple-950 mb-1">Chat history refreshed!</p>
                <p class="text-xs text-slate-600">Ask any placement doubt or click the quick topic pills above to get instant expert guidance.</p>
            </div>
        `;
        chatHistory = [];
    });

    // Pill Chips Handler
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.mentor-chip');
        if (chip) {
            const query = chip.getAttribute('data-query') || chip.textContent.trim();
            sendMessage(query);
            return;
        }

        const actionBtn = e.target.closest('.mentor-action-btn');
        if (actionBtn) {
            const action = actionBtn.getAttribute('data-action');
            if (action === 'tab-interview') {
                if (typeof window.showTab === 'function') window.showTab('interview');
                sendMessage("Give me essential tips for the AI Mock Interview: STAR method, eye gaze proctoring, and speech pacing.");
            } else if (action === 'tab-resume') {
                if (typeof window.showTab === 'function') window.showTab('resume');
                sendMessage("How do I optimize my resume for ATS scoring and format technical skills with symbols?");
            } else if (action === 'tab-placement') {
                if (typeof window.showTab === 'function') window.showTab('placement');
                sendMessage("What are the 47 active placement drives, top companies, and package tiers available?");
            }
        }
    });

    // Form submit
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        sendMessage(text);
        input.value = '';
    });

    // Speech-to-Text via Web Speech API
    let recognition = null;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            micBtn.classList.add('text-purple-600', 'animate-pulse');
            input.placeholder = 'Listening to your voice...';
        };

        recognition.onresult = (evt) => {
            const transcript = evt.results[0][0].transcript;
            input.value = transcript;
            sendMessage(transcript);
        };

        recognition.onerror = () => {
            micBtn.classList.remove('text-purple-600', 'animate-pulse');
            input.placeholder = 'Ask your doubt or concern...';
        };

        recognition.onend = () => {
            micBtn.classList.remove('text-purple-600', 'animate-pulse');
            input.placeholder = 'Ask your doubt or concern...';
        };

        micBtn.addEventListener('click', () => {
            try {
                recognition.start();
            } catch (err) {
                recognition.stop();
            }
        });
    }

    // Message Rendering Helpers
    function renderUserBubble(text) {
        const div = document.createElement('div');
        div.className = 'mentor-msg-bubble flex justify-end';
        div.innerHTML = `
            <div class="bg-gradient-to-r from-purple-700 to-indigo-600 text-white p-3 rounded-2xl rounded-tr-xs shadow-sm max-w-[85%] leading-relaxed font-medium text-xs">
                ${escapeHTML(text)}
            </div>
        `;
        msgContainer.appendChild(div);
        msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    function renderTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'mentor-msg-bubble flex items-start gap-2.5';
        div.innerHTML = `
            <div class="w-7 h-7 rounded-xl bg-purple-700 text-white flex items-center justify-center shrink-0 shadow-sm text-xs">
                🤖
            </div>
            <div class="bg-white p-3 rounded-2xl rounded-tl-xs border border-slate-200 shadow-xs text-slate-400 flex items-center gap-1.5 h-9">
                <span class="w-2 h-2 rounded-full bg-purple-600 mentor-typing-dot"></span>
                <span class="w-2 h-2 rounded-full bg-purple-600 mentor-typing-dot"></span>
                <span class="w-2 h-2 rounded-full bg-purple-600 mentor-typing-dot"></span>
            </div>
        `;
        msgContainer.appendChild(div);
        msgContainer.scrollTop = msgContainer.scrollHeight;
        return id;
    }

    function renderBotBubble(markdownText, engine) {
        const div = document.createElement('div');
        div.className = 'mentor-msg-bubble flex items-start gap-2.5';
        
        const badge = engine === 'google_gemini_llm' ? '✨ Gemini Live LLM' : '⚡ Mitra AI Knowledge Engine';
        
        div.innerHTML = `
            <div class="w-7 h-7 rounded-xl bg-gradient-to-tr from-purple-700 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-sm text-xs">
                🤖
            </div>
            <div class="bg-white p-3.5 rounded-2xl rounded-tl-xs border border-slate-200/90 shadow-xs text-slate-800 leading-relaxed max-w-[88%] space-y-2">
                <div class="flex items-center justify-between pb-1.5 border-b border-slate-100">
                    <span class="text-[9px] font-mono font-bold text-purple-700 uppercase tracking-wider">${badge}</span>
                </div>
                <div class="text-[12px] text-slate-700 leading-relaxed">
                    ${formatSimpleMarkdown(markdownText)}
                </div>
            </div>
        `;
        msgContainer.appendChild(div);
        msgContainer.scrollTop = msgContainer.scrollHeight;
    }

    async function sendMessage(text) {
        renderUserBubble(text);
        const typingId = renderTypingIndicator();

        chatHistory.push({ role: 'user', content: text });

        try {
            const token = localStorage.getItem('token') || '';
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const res = await fetch('/api/v1/chatbot/chat', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({
                    message: text,
                    history: chatHistory.slice(-4)
                })
            });

            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            if (!res.ok) throw new Error('Mentor API error');
            const data = await res.json();

            renderBotBubble(data.response, data.engine);
            chatHistory.push({ role: 'model', content: data.response });

        } catch (err) {
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();

            renderBotBubble(
                "### 🎓 Mitra Placement Guidance\\n\\nI'm currently assisting in offline mode. Here are the core pillars to succeed:\\n- **Round 1 (Aptitude)**: Solve high-confidence questions first; maintain speed without sacrificing accuracy.\\n- **Round 2 (Technical MCQ)**: Review DSA complexities ($O(1)$ Hash vs $O(N \\log N)$ Sort), DBMS ACID/Indexing, and OS paging.\\n- **Round 3 (AI Mock Interview)**: Use the **STAR method** (Situation, Task, Action, Result) and speak steadily at 120-150 WPM.",
                "offline_heuristic_kb"
            );
        }
    }

    function escapeHTML(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function formatSimpleMarkdown(txt) {
        if (!txt) return '';
        let html = txt
            .replace(/^### (.*$)/gim, '<h4 class="font-bold text-purple-950 text-xs mt-2.5 mb-1">$1</h4>')
            .replace(/^#### (.*$)/gim, '<h5 class="font-semibold text-slate-900 text-xs mt-2 mb-0.5">$1</h5>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong class="font-bold text-slate-900">$1</strong>')
            .replace(/\*(.*?)\*/gim, '<em class="italic">$1</em>')
            .replace(/```([\s\S]*?)```/gim, '<pre class="bg-slate-900 text-purple-200 p-2.5 rounded-lg text-[11px] font-mono overflow-x-auto my-2"><code>$1</code></pre>')
            .replace(/^[-*] (.*$)/gim, '<li class="ml-3.5 list-disc text-slate-700 my-0.5">$1</li>')
            .replace(/\n\n/gim, '<div class="h-2"></div>')
            .replace(/\n/gim, '<br />');
        return html;
    }
})();
