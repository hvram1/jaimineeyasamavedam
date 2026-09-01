// Jaimineeya Samavedam Website JavaScript
// Deterministic Navigation System v2.1

document.addEventListener('DOMContentLoaded', function() {
    console.log("[JS] Jaimineeya Website Loaded");

    // Centralized Scroll Handler
    const scrollToTarget = (targetId, smooth = true) => {
        if (!targetId) return;
        
        // Clean hash (strip #)
        const id = targetId.startsWith('#') ? targetId.substring(1) : targetId;
        const element = document.getElementById(id);
        
        if (element) {
            console.log("[Scroll] Navigating to:", id);
            
            // Fixed header offset (adjust based on CSS)
            const headerOffset = 100;
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: smooth ? 'smooth' : 'auto'
            });
            
            return true;
        }
        console.warn("[Scroll] Target not found:", id);
        return false;
    };

    // 1. Handle Initial Load Scroll (Deterministic Wait)
    window.addEventListener('load', () => {
        if (window.location.hash) {
            console.log("[Load] Initial hash detected:", window.location.hash);
            // Wait for Sanskrit web fonts and layout to finish settling
            setTimeout(() => {
                scrollToTarget(window.location.hash, false);
            }, 200);
        }
    });

    // 2. Handle Hash Changes (Link clicks, History)
    window.addEventListener('hashchange', () => {
        console.log("[HashChange] New hash:", window.location.hash);
        scrollToTarget(window.location.hash, true);
    });

    // 3. Smooth scroll for ALL internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const hash = this.getAttribute('href');
            if (hash === '#') return;
            
            e.preventDefault();
            // Update hash which triggers hashchange listener
            if (window.location.hash === hash) {
                // Manually trigger if hash is identical
                scrollToTarget(hash, true);
            } else {
                window.location.hash = hash;
            }
        });
    });

    // 4. Parva Map for Jump resolution
    const parvaMap = {};
    document.querySelectorAll('.parva-link').forEach(link => {
        const href = link.getAttribute('href') || '';
        const ssMatch = href.match(/kandah[/]([^/]+)[/]/);
        if (ssMatch) {
            const displayNum = parseInt(link.textContent.trim());
            if (!isNaN(displayNum)) {
                parvaMap[displayNum] = ssMatch[1];
            }
        }
    });

    // 5. Consolidated Navigation Logic (Deterministic P.K.S Resolution)
    window.resolveJump = (val, smooth = true) => {
        if (!val) return;
        
        console.log("[Navigation] Resolving reference:", val);
        const parts = val.split('.');
        
        // Resolve prefix based on current depth
        const path = window.location.pathname;
        let depth = 0;
        if (path.includes('/kandah/')) depth = 2;
        else if (path.includes('/classification/') || path.includes('/vargeekaran/')) depth = 1;
        const prefix = '../'.repeat(depth);

        if (parts.length >= 2) {
            const parvaNum = parseInt(parts[0]);
            
            // Site-aware prefix resolution (Handles Samhita vs Aaranam cross-links)
            let sitePrefix = "";
            const currentPath = window.location.pathname;
            
            // Only switch sites if the parvaNum is NOT in our local parvaMap
            if (!parvaMap[parvaNum]) {
                if (parvaNum <= 6 && currentPath.includes('/aaranam/')) {
                    sitePrefix = "../samhita/";
                } else if (parvaNum > 6 && currentPath.includes('/samhita/')) {
                    sitePrefix = "../aaranam/";
                }
            }

            const parvaId = parvaMap[parvaNum] || `supersection_${parts[0]}`;
            const kandahId = parts[1];
            
            // Deterministic hash: point to specific Samam Sequence ID (#sama-N)
            const targetHash = parts.length === 3 ? `#sama-${parts[2]}` : "";
            const targetPage = `kandah/${parvaId}/${kandahId}.html`;
            const currentPage = window.location.pathname;
            
            console.log("[Navigation] Target determined:", prefix + sitePrefix + targetPage + targetHash);

            if (currentPage.endsWith(targetPage) || currentPage.includes('/' + targetPage)) {
                // Same file: Just scroll
                if (window.location.hash === targetHash) scrollToTarget(targetHash, true);
                else window.location.hash = targetHash;
            } else {
                // Different file: Redirect
                window.location.assign(prefix + sitePrefix + targetPage + targetHash);
            }
            return true;
        }
        return false;
    };

    // Link Jump Box to Consolidated Logic
    const jumpInput = document.getElementById('sidebar-jump');
    const handleJump = () => {
        const val = jumpInput ? jumpInput.value.trim() : '';
        window.resolveJump(val, true);
    };

    // 6. Sidebar Highlighting (Intersection Observer)
    const observerOptions = {
        root: null,
        rootMargin: '-100px 0px -70% 0px',
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const samaStart = entry.target.getAttribute('data-sama-start');
                if (samaStart) {
                    document.querySelectorAll('.nav-links a.active, .jump-links a.active').forEach(l => {
                        l.classList.remove('active');
                    });
                    
                    const links = document.querySelectorAll(`.nav-links a[href="#sama-${samaStart}"], .jump-links a[href="#sama-${samaStart}"]`);
                    links.forEach(l => {
                        l.classList.add('active');
                    });
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.sama-entry').forEach(el => observer.observe(el));

    if (jumpInput) {
        jumpInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') handleJump();
        });
    }

    // Search Interactivity (Standard)
    const searchModal = document.getElementById('search-modal');
    const searchOverlay = document.getElementById('search-overlay');
    const searchInput = document.getElementById('search-input');
    const searchClose = document.getElementById('search-close');
    const searchResults = document.getElementById('search-results');
    const searchBtn = document.querySelector('.search-btn');
    let searchIndex = null;
    
    const loadSearchIndex = () => {
        if (typeof SEARCH_INDEX !== 'undefined') {
            searchIndex = SEARCH_INDEX;
            if (searchResults) searchResults.innerHTML = '';
        } else {
            if (searchResults) searchResults.innerHTML = '<div class="search-no-results"><div class="icon">⚠️</div>Could not load search index.</div>';
        }
    };
    
    const openSearchModal = () => {
        if (searchModal) {
            searchModal.classList.add('active');
            searchOverlay.classList.add('active');
            if (searchInput) searchInput.focus();
            if (!searchIndex) loadSearchIndex();
        }
    };
    
    const closeSearchModal = () => {
        if (searchModal) searchModal.classList.remove('active');
        if (searchOverlay) searchOverlay.classList.remove('active');
    };
    
    if (searchClose) searchClose.addEventListener('click', closeSearchModal);
    if (searchOverlay) searchOverlay.addEventListener('click', closeSearchModal);
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeSearchModal();
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            openSearchModal();
        }
    });
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openSearchModal();
        });
    }
    
    document.querySelectorAll('.top-nav a').forEach(link => {
        if (link.textContent.includes('Search') || link.textContent.includes('अन्वेषणम्')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                openSearchModal();
            });
        }
    });
    
    // Detect current page depth for relative path resolution
    const path = window.location.pathname;
    let depth = 0;
    if (path.includes('/kandah/')) depth = 2;
    else if (path.includes('/classification/') || path.includes('/vargeekaran/')) depth = 1;
    const depthPrefix = '../'.repeat(depth);
    
const highlightText = (text, query, devanagariQuery) => {
        if (!text) return text;
        if (!query && !devanagariQuery) return text;

        let searchQ = query;
        if (devanagariQuery && devanagariQuery.length > 0) {
            searchQ = devanagariQuery;
        }

        if (text.toLowerCase().indexOf(searchQ.toLowerCase()) !== -1) {
            const re = new RegExp(searchQ.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
            return text.replace(re, '<mark>$&</mark>');
        }

        return text;
    };

    const latinToDevanagari = (text) => {
        const mapping = {
            'aa': 'आ', 'ee': 'ई', 'oo': 'ऊ', 'ai': 'ऐ', 'au': 'औ', 'ri': 'ऋ', 'rii': 'ॠ',
            'kh': 'ख', 'gh': 'घ', 'ch': 'च', 'chh': 'छ', 'jh': 'झ', 'th': 'थ', 'dh': 'ध',
            'ph': 'फ', 'bh': 'भ', 'sh': 'श', 'ng': 'ङ', 'nj': 'ञ', 'nn': 'ण',
            'a': 'अ', 'i': 'इ', 'u': 'उ', 'e': 'ए', 'o': 'ओ',
            'k': 'क', 'g': 'ग', 'c': 'च', 'j': 'ज', 't': 'त', 'd': 'द', 'n': 'न',
            'p': 'प', 'b': 'ब', 'm': 'म', 'y': 'य', 'r': 'र', 'l': 'ल', 'v': 'व', 'w': 'व', 's': 'स', 'h': 'ह',
            '.': '।', '|': '॥'
        };
        let result = text.toLowerCase();
        for (const [k, v] of Object.entries(mapping).sort((a, b) => b[0].length - a[0].length)) {
            result = result.replaceAll(k, v);
        }
        return result;
    };

    const performSearch = (query, callIsLatin, callDevanagariQuery) => {
        if (!query || query.length < 2 || !searchIndex) return [];
        const q = query.toLowerCase().trim();
        const results = [];

        const isLatin = callIsLatin !== undefined ? callIsLatin : (/[a-z]/.test(q) && !/[\u0900-\u097F]/.test(q));

        const normalizeLatin = (text) => {
            if (!text) return "";
            const map = {
                'aa': 'a', 'ee': 'i', 'oo': 'u', 'ii': 'i', 'uu': 'u',
                'kh': 'k', 'gh': 'g', 'ch': 'c', 'jh': 'j', 'th': 't', 'dh': 'd', 'ph': 'p', 'bh': 'b',
                'sh': 's', 'z': 's', 'w': 'v', 'ñ': 'n', 'ṅ': 'n', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
                'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṭ': 't', 'ḍ': 'd', 'ḥ': 'h', 'ṃ': 'n', 'ṁ': 'n'
            };
            let result = text.toLowerCase().replace(/[^a-z]/g, '');
            for (const [k, v] of Object.entries(map)) {
                result = result.replaceAll(k, v);
            }
            return result;
        };

        // Use the passed devanagariQuery if provided, otherwise compute it
        const devanagariQuery = callDevanagariQuery !== undefined ? callDevanagariQuery : (isLatin ? latinToDevanagari(q) : null);

        for (const entry of searchIndex) {
            let score = 0;
            let matchedFields = [];
            
            const checkField = (text, fieldScore, fieldName, displayHtml) => {
                if (!text) return;
                // Remove spaces for comparison
                const wsRegex = /\s+/g;
                const textNoSpaces = text.replace(wsRegex, '');
                const qNoSpaces = q.replace(wsRegex, '');
                
                // Check exact match
                if (textNoSpaces.toLowerCase().includes(qNoSpaces)) {
                    score += fieldScore;
                    matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    return;
                }
                
                // Check permissive (diacritic-stripped) match
                // We must strip parentheses content for Samam swara ignoring
                const stripAll = (t) => t.replace(/\([^)]*\)/g, '').replace(/[\u093E-\u094D\u0951-\u0957\u1CD0-\u1CFF\u0964\u0965\u0966-\u096F0-9]/g, '');
                const textPermissive = stripAll(textNoSpaces);
                const qPermissive = stripAll(qNoSpaces);
                if (textPermissive.toLowerCase().includes(qPermissive)) {
                    score += fieldScore * 0.8;
                    matchedFields.push({ name: fieldName, text: text, html: displayHtml, matchedInDevanagari: true });
                    return;
                }
                
                // Check Latin match if input is Latin
                if (isLatin) {
                    const qLatin = normalizeLatin(qNoSpaces);
                    // Match against various latin fields found in entries
                    if (fieldName === 'Mantra' && entry.mantra_latin && entry.mantra_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (fieldName === 'Rik' && entry.rik_latin && entry.rik_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (fieldName === 'Title' && entry.title_latin && entry.title_latin.includes(qLatin)) {
                        score += fieldScore * 0.75;
                        matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                    } else if (devanagariQuery) {
                        // Fallback: check Devanagari conversion match
                        const textLatin = textNoSpaces.replace(/[\u093E-\u094D\u0951-\u0954]/g, '');
                        const dqNoSpaces = devanagariQuery.replace(wsRegex, '');
                        if (textLatin.toLowerCase().includes(dqNoSpaces.toLowerCase())) {
                            score += fieldScore * 0.65;
                            matchedFields.push({ name: fieldName, text: text, html: displayHtml });
                        }
                    }
                }
            };
            
            checkField(entry.mantra_clean, 10, 'Mantra', entry.mantra_html);
            checkField(entry.rik_clean, 8, 'Rik', entry.rik_html);
            
            for (const c of entry.classifications) {
                checkField(c.rishi_clean, 7, 'Rishi', c.rishi);
                // Latin match for Rishi
                if (isLatin && c.rishi_latin && c.rishi_latin.includes(normalizeLatin(q))) {
                    score += 5; matchedFields.push({ name: 'Rishi', text: c.rishi_clean, html: c.rishi });
                }
                
                checkField(c.devata_clean, 6, 'Devata', c.devata);
                // Latin match for Devata
                if (isLatin && c.devata_latin && c.devata_latin.includes(normalizeLatin(q))) {
                    score += 4; matchedFields.push({ name: 'Devata', text: c.devata_clean, html: c.devata });
                }
                
                checkField(c.chandas_clean, 4, 'Chandas', c.chandas);
            }
            
            checkField(entry.title_clean, 5, 'Title', entry.title_html);
            checkField(entry.metadata_clean, 3, 'Metadata', entry.metadata_html);
            
            if (score > 0) {
                results.push({ ...entry, score, matchedFields });
            }
        }
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, 50);
    };
    
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (!query) {
                    if (searchResults) searchResults.innerHTML = '';
                    return;
                }
                if (!searchIndex) {
                    if (searchResults) searchResults.innerHTML = '<div class="search-loading">Loading search index...</div>';
                    return;
                }
                const q = query.toLowerCase().trim();
                const isLatin = /[a-z]/.test(q) && !/[\u0900-\u097F]/.test(q);
                const devanagariQuery = isLatin ? latinToDevanagari(q) : null;
                const results = performSearch(query, isLatin, devanagariQuery);
                if (results.length === 0) {
                    searchResults.innerHTML = '<div class="search-no-results"><div class="icon">🔍</div>No results found for "' + query + '"</div>';
                    return;
                }
                let html = '';
                for (const r of results) {
                    const classInfo = r.classifications.length > 0 
                        ? r.classifications.map(c => [c.rishi, c.devata, c.chandas].filter(Boolean).join(' | ')).filter(Boolean).join('; ')
                        : '';
                    const fieldLabels = { 'Mantra': 'मन्त्र', 'Rik': 'ऋक्', 'Rishi': 'ऋषि', 'Devata': 'देवता', 'Chandas': 'छन्दस्', 'Title': 'शीर्षक', 'Metadata': 'विवरण' };
                    let fieldsHtml = '';
                    for (const mf of r.matchedFields) {
                        const highlighted = highlightText(mf.html || mf.text, query, devanagariQuery);
                        const label = fieldLabels[mf.name] || mf.name;
                        fieldsHtml += `<div class="search-result-field"><span class="search-result-field-label">${label}</span><div class="search-result-text">${highlighted}</div></div>`;
                    }
                    html += `<div class="search-result-item">
                        <div class="search-result-ref"><a href="${depthPrefix}${r.link}">${r.ref} — ${r.parva_title}, Kandah ${r.kandah_num}</a></div>
                        <div class="search-result-meta">${classInfo || ''}</div>
                        ${fieldsHtml}
                    </div>`;
                }
                searchResults.innerHTML = html;
                
                // Add click handlers to result items for navigation
                document.querySelectorAll('.search-result-item').forEach(item => {
                    let startX, startY;
                    item.addEventListener('mousedown', function(e) {
                        if (e.button !== 0) return;
                        startX = e.clientX;
                        startY = e.clientY;
                    });
                    item.addEventListener('mouseup', function(e) {
                        if (e.button !== 0) return;
                        const dx = Math.abs(e.clientX - startX);
                        const dy = Math.abs(e.clientY - startY);
                        if (dx > 5 || dy > 5) return;
                        const selection = window.getSelection();
                        if (selection && selection.toString().trim().length > 0) {
                            return;
                        }
                        const link = this.querySelector('.search-result-ref a');
                        if (link) {
                            // Extract reference from text (e.g. "1.1.1 — ...")
                            const refPart = link.textContent.split('—')[0].trim();
                            if (refPart && window.resolveJump) {
                                e.preventDefault();
                                window.resolveJump(refPart, true);
                                closeSearchModal();
                            } else {
                                window.location.href = link.href;
                            }
                        }
                    });
                    // Double-click always navigates
                    item.addEventListener('dblclick', function(e) {
                        const link = this.querySelector('.search-result-ref a');
                        if (link) {
                            window.location.href = link.href;
                        }
                    });
                });
            }, 250);
        });
    }
    
    // Audio error handling
    document.querySelectorAll('audio').forEach(audio => {
        audio.addEventListener('error', function() {
            const container = this.closest('.audio-section');
            if (container) {
                container.innerHTML = `
                    <div class="audio-pending">
                        <span>🎵</span>
                        <span>Audio coming soon</span>
                    </div>
                `;
            }
        });
    });
});
