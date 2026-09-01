/**
 * Jaimineeya Sama Veda - Visual Curation & Benchmarking Controller
 * Unified Editor with Live Vedic Accent Preview, Stacked/Split Layouts & Modifier Palettes
 */

// Application State
const state = {
  data: null,
  currentSectionIdx: 0,
  currentSubsecIdx: 0,
  currentSamamIdx: 0,
  currentSubNum: null,
  currentPage: 3,
  zoom: 1.0,
  panX: 0,
  panY: 0,
  isPanning: false,
  startX: 0,
  startY: 0,
  inverted: false,
  isStacked: false
};

// DOM Elements
const elements = {
  sectionSelect: document.getElementById('sectionSelect'),
  subsectionSelect: document.getElementById('subsectionSelect'),
  samamSelect: document.getElementById('samamSelect'),
  directSubInput: document.getElementById('directSubInput'),
  directSubBtn: document.getElementById('directSubBtn'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  saveBtn: document.getElementById('saveBtn'),
  layoutToggleBtn: document.getElementById('layoutToggleBtn'),
  layoutLabel: document.getElementById('layoutLabel'),
  fontToggleBtn: document.getElementById('fontToggleBtn'),
  fontLabel: document.getElementById('fontLabel'),
  workspaceGrid: document.querySelector('.workspace-grid'),
  
  manuscriptImg: document.getElementById('manuscriptImg'),
  panContainer: document.getElementById('panContainer'),
  viewport: document.getElementById('viewport'),
  pageLabel: document.getElementById('pageLabel'),
  zoomLevel: document.getElementById('zoomLevel'),
  prevPageBtn: document.getElementById('prevPageBtn'),
  nextPageBtn: document.getElementById('nextPageBtn'),
  zoomInBtn: document.getElementById('zoomInBtn'),
  zoomOutBtn: document.getElementById('zoomOutBtn'),
  fitWidthBtn: document.getElementById('fitWidthBtn'),
  invertBtn: document.getElementById('invertBtn'),
  
  curationTitle: document.getElementById('curationTitle'),
  curationStatus: document.getElementById('curationStatus'),
  mainVedicEditor: document.getElementById('mainVedicEditor'),
  renderedVedicDisplay: document.getElementById('renderedVedicDisplay'),
  toast: document.getElementById('toast')
};

// Exact Section and Subsection Ground-Truth Page Anchors
const SECTION_PAGE_MAP = [
  // Agneyam (SS1)
  { subMin: 1, subMax: 13, pageMin: 3, pageMax: 6 },
  { subMin: 14, subMax: 24, pageMin: 7, pageMax: 10 },
  { subMin: 25, subMax: 37, pageMin: 10, pageMax: 14 },
  { subMin: 38, subMax: 52, pageMin: 14, pageMax: 18 },
  { subMin: 53, subMax: 63, pageMin: 19, pageMax: 24 },
  { subMin: 64, subMax: 73, pageMin: 25, pageMax: 26 },
  { subMin: 74, subMax: 81, pageMin: 27, pageMax: 28 },
  { subMin: 82, subMax: 88, pageMin: 29, pageMax: 30 },
  { subMin: 89, subMax: 97, pageMin: 31, pageMax: 32 },
  { subMin: 98, subMax: 106, pageMin: 33, pageMax: 34 },
  { subMin: 107, subMax: 115, pageMin: 35, pageMax: 36 },
  { subMin: 116, subMax: 126, pageMin: 37, pageMax: 38 },
  // Tadva (SS2)
  { subMin: 127, subMax: 251, pageMin: 39, pageMax: 83 },
  // Bruhati (SS3)
  { subMin: 252, subMax: 346, pageMin: 84, pageMax: 130 },
  // Asaavi (SS4)
  { subMin: 348, subMax: 411, pageMin: 131, pageMax: 160 },
  // Aindram (SS5)
  { subMin: 1413, subMax: 1517, pageMin: 161, pageMax: 210 },
  // Pavamanam (SS6)
  { subMin: 519, subMax: 727, pageMin: 211, pageMax: 324 },
];

function estimateManuscriptPageForSub(sNum) {
  for (const range of SECTION_PAGE_MAP) {
    if (sNum >= range.subMin && sNum <= range.subMax) {
      if (range.subMax === range.subMin) return range.pageMin;
      const progress = (sNum - range.subMin) / (range.subMax - range.subMin);
      const est = Math.floor(range.pageMin + progress * (range.pageMax - range.pageMin));
      return Math.min(range.pageMax, Math.max(range.pageMin, est));
    }
  }
  return 3;
}

// App Initialization
document.addEventListener('DOMContentLoaded', initApp);

async function initApp() {
  const savedLayout = localStorage.getItem('jsv_layout_preference');
  if (savedLayout === 'stacked') {
    state.isStacked = true;
    elements.workspaceGrid.classList.add('stacked');
    elements.layoutLabel.textContent = 'Side-by-Side';
  }

  // Restore font preference (default is Noto Serif)
  const savedFont = localStorage.getItem('jsv_font_preference');
  if (savedFont === 'rachana') {
    document.body.classList.add('font-rachana');
  } else {
    document.body.classList.remove('font-rachana');
  }
  updateFontButtonLabel();

  setupEventListeners();
  setupPanZoom();
  await loadSamamsData();
}

function toggleFont() {
  const isRachana = document.body.classList.toggle('font-rachana');
  localStorage.setItem('jsv_font_preference', isRachana ? 'rachana' : 'noto');
  updateFontButtonLabel();
  showToast(isRachana ? "Switched font to RIT Rachana" : "Switched font to Noto Serif Malayalam", 1500);
}

function updateFontButtonLabel() {
  const isRachana = document.body.classList.contains('font-rachana');
  if (elements.fontLabel) {
    elements.fontLabel.textContent = isRachana ? 'Font: Rachana' : 'Font: Noto Serif';
  }
}

// Fetch all sections & samams from server
async function loadSamamsData() {
  try {
    showToast("Loading Samams from master archive...", 1500);
    const resp = await fetch('/api/samams');
    state.data = await resp.json();
    
    if (state.data.sections && state.data.sections.length > 0) {
      populateSectionDropdown();
      selectSection(0);
    }
  } catch (err) {
    showToast("Error loading data from server", 4000, true);
    console.error(err);
  }
}

// Dropdown Populators with Parva / SuperSection Grouping
function populateSectionDropdown() {
  elements.sectionSelect.innerHTML = '';
  
  const groups = {};
  state.data.sections.forEach((sec, idx) => {
    const groupTitle = sec.supersection || "General Sections";
    if (!groups[groupTitle]) {
      groups[groupTitle] = [];
    }
    groups[groupTitle].push({ sec, idx });
  });

  Object.entries(groups).forEach(([groupName, items]) => {
    const optgroup = document.createElement('optgroup');
    optgroup.label = groupName;
    items.forEach(({ sec, idx }) => {
      const opt = document.createElement('option');
      opt.value = idx;
      const tag = sec.supersection_tag ? `[${sec.supersection_tag}] ` : '';
      opt.textContent = `${tag}${sec.title || sec.id} (${sec.subsections.length} Subs)`;
      optgroup.appendChild(opt);
    });
    elements.sectionSelect.appendChild(optgroup);
  });
}

function selectSection(idx) {
  state.currentSectionIdx = idx;
  const sec = state.data.sections[idx];
  
  elements.subsectionSelect.innerHTML = '';
  sec.subsections.forEach((sub, subIdx) => {
    const opt = document.createElement('option');
    opt.value = subIdx;
    const numLabel = sub.number ? `[Sub ${sub.number}] ` : '';
    opt.textContent = `${numLabel}${sub.title || sub.id} (${sub.samams.length} Samams)`;
    elements.subsectionSelect.appendChild(opt);
  });
  
  selectSubsection(0);
}

function selectSubsection(subIdx) {
  state.currentSubsecIdx = subIdx;
  const sec = state.data.sections[state.currentSectionIdx];
  const subsec = sec.subsections[subIdx];
  
  if (!subsec) return;

  const sNum = subsec.number || parseInt(subsec.id.replace(/\D/g, ''), 10);
  if (elements.directSubInput && sNum) {
    elements.directSubInput.value = sNum;
  }

  elements.samamSelect.innerHTML = '';
  subsec.samams.forEach((sam, samIdx) => {
    const opt = document.createElement('option');
    opt.value = samIdx;
    opt.textContent = `Samam ${sam.num} ${sam.danda}`;
    elements.samamSelect.appendChild(opt);
  });
  
  selectSamam(0);
}

function selectSamam(samIdx) {
  state.currentSamamIdx = samIdx;
  
  const sec = state.data.sections[state.currentSectionIdx];
  const subsec = sec.subsections[state.currentSubsecIdx];
  const samam = subsec.samams[samIdx];
  
  if (!samam) return;

  elements.sectionSelect.value = state.currentSectionIdx;
  elements.subsectionSelect.value = state.currentSubsecIdx;
  elements.samamSelect.value = samIdx;
  
  const sNum = subsec.number || parseInt(subsec.id.replace(/\D/g, ''), 10);
  const tag = sec.supersection_tag ? `[${sec.supersection_tag}] ` : '';
  elements.curationTitle.textContent = `${tag}${sec.title} • Sub ${sNum} ${subsec.title} • Samam ${samam.num}`;
  elements.mainVedicEditor.value = samam.text;
  
  // Only auto-load estimated page when transitioning to a NEW subsection
  if (state.currentSubNum !== sNum) {
    state.currentSubNum = sNum;
    const estPage = estimateManuscriptPageForSub(sNum);
    loadManuscriptPage(estPage);
  }
  
  updateDisplays();
}

// Direct Jump to any Subsection across the entire corpus
function handleDirectSubJump() {
  const targetSub = parseInt(elements.directSubInput.value, 10);
  if (isNaN(targetSub)) {
    showToast("Please enter a valid subsection number", 2000, true);
    return;
  }

  if (!state.data || !state.data.sections) return;

  let found = false;
  for (let sIdx = 0; sIdx < state.data.sections.length; sIdx++) {
    const sec = state.data.sections[sIdx];
    for (let subIdx = 0; subIdx < sec.subsections.length; subIdx++) {
      const subsec = sec.subsections[subIdx];
      const sNum = subsec.number || parseInt(subsec.id.replace(/\D/g, ''), 10);
      if (sNum === targetSub) {
        state.currentSectionIdx = sIdx;
        elements.sectionSelect.value = sIdx;
        
        // Populate and select subsection
        elements.subsectionSelect.innerHTML = '';
        sec.subsections.forEach((sub, idx) => {
          const opt = document.createElement('option');
          opt.value = idx;
          const numLabel = sub.number ? `[Sub ${sub.number}] ` : '';
          opt.textContent = `${numLabel}${sub.title || sub.id} (${sub.samams.length} Samams)`;
          elements.subsectionSelect.appendChild(opt);
        });
        elements.subsectionSelect.value = subIdx;
        
        selectSubsection(subIdx);
        showToast(`Jumped to Subsection ${targetSub} (${sec.supersection_tag || ''} - ${sec.title})`, 2000);
        found = true;
        break;
      }
    }
    if (found) break;
  }

  if (!found) {
    showToast(`Subsection ${targetSub} not found in master archive`, 3000, true);
  }
}

// Manuscript Page Loading & Deep Zoom
function loadManuscriptPage(pageNum) {
  state.currentPage = pageNum;
  elements.pageLabel.textContent = `Page ${pageNum}`;
  elements.manuscriptImg.src = `/api/page/${pageNum}.png`;
}

function setupPanZoom() {
  const vp = elements.viewport;

  vp.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    state.isPanning = true;
    state.startX = e.clientX - state.panX;
    state.startY = e.clientY - state.panY;
  });

  window.addEventListener('mousemove', (e) => {
    if (!state.isPanning) return;
    state.panX = e.clientX - state.startX;
    state.panY = e.clientY - state.startY;
    applyTransform();
  });

  window.addEventListener('mouseup', () => {
    state.isPanning = false;
  });

  vp.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    const newZoom = Math.max(0.2, Math.min(state.zoom * zoomFactor, 5.0));
    
    // Zoom centered on cursor
    const rect = vp.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    state.panX = mouseX - (mouseX - state.panX) * (newZoom / state.zoom);
    state.panY = mouseY - (mouseY - state.panY) * (newZoom / state.zoom);
    state.zoom = newZoom;
    
    applyTransform();
  });
}

function applyTransform() {
  elements.panContainer.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
  elements.zoomLevel.textContent = `${Math.round(state.zoom * 100)}%`;
}

function fitToWidth() {
  const vpWidth = elements.viewport.clientWidth;
  const imgWidth = elements.manuscriptImg.naturalWidth || 2480;
  state.zoom = (vpWidth - 20) / imgWidth;
  state.panX = 10;
  state.panY = 10;
  applyTransform();
}

// Canonical Swara normalization to authentic dedicated glyphs in JaimineeyaSwara.ttf
function getCanonicalSwaraGlyph(str) {
  if (!str) return '';
  let res = str;

  // 1. Pla family - convert any Grantha / Malayalam sequence to authentic JaimineeyaSwara Pla glyphs
  res = res.replace(/𑌪𑍍𑌲𑌾|പ്ലാ|\u1132A\u1134D\u11332\u1133E/g, '\uE021');
  res = res.replace(/𑌪𑍍𑌲𑍀|പ്ലീ|\u1132A\u1134D\u11332\u11340/g, '\uE023');
  res = res.replace(/𑌪𑍍𑌲𑌿|പ്ലി|\u1132A\u1134D\u11332\u1133F/g, '\uE022');
  res = res.replace(/𑌪𑍍𑌲𑍁|പ്ലു|\u1132A\u1134D\u11332\u11341/g, '\uE024');
  res = res.replace(/𑌪𑍍𑌲𑍂|പ്ലൂ|\u1132A\u1134D\u11332\u11342/g, '\uE025');
  res = res.replace(/𑌪𑍍𑌲𑍍|പ്ല്|\u1132A\u1134D\u11332\u1134D/g, '\uE026');
  res = res.replace(/𑌪𑍍𑌲|പ്ല|\u1132A\u1134D\u11332/g, '\uE020');

  // 2. Tra & Kra
  res = res.replace(/𑌤𑍍𑌰𑌾|ത്രാ|𑌤𑍍𑌰|ത്ര|\u11324\u1134D\u11330/g, '\uE01D');
  res = res.replace(/𑌕𑍍𑌰𑍍|ക്ര്|\u11315\u1134D\u11330\u1134D/g, '\uE01F');
  res = res.replace(/𑌕𑍍𑌰|ക്രം|ക്ര|\u11315\u1134D\u11330/g, '\uE01E');

  // 3. Sha family (Exact mapping to JaimineeyaSwara.ttf)
  res = res.replace(/𑌶𑍌|ശൌ|ശൗ/g, '\uE01C');
  res = res.replace(/𑌶𑍋|ശോ/g, '\uE01B');
  res = res.replace(/𑌶𑍈|ശൈ/g, '\uE01A');
  res = res.replace(/𑌶𑍇|ശേ/g, '\uE019');
  res = res.replace(/𑌶𑍄|ശൄ/g, '\uE018');
  res = res.replace(/𑌶𑍃|ശൃ/g, '\uE017');
  res = res.replace(/𑌶𑍂|ശൂ/g, '\uE016');
  res = res.replace(/𑌶𑍁|ശു/g, '\uE015');
  res = res.replace(/𑌶𑍀|ശീ/g, '\uE012');
  res = res.replace(/𑌶𑌿|ശി/g, '\uE011');
  res = res.replace(/𑌶𑍍|ശ്/g, '\uE013');
  res = res.replace(/𑌶𑌾|ശാ/g, '\uE010');
  res = res.replace(/𑌶/g, 'ശ');

  // 4. Composites
  res = res.replace(/𑌶𑍍𑌰𑍂|ശ്രൂ/g, '\uE027');
  res = res.replace(/𑌷𑍃|ശ്രൃ|ഷൃ/g, '\uE028');
  res = res.replace(/𑌣𑍂|𑌣𑍁|ണൂ|ണു/g, '\uE029');

  return res;
}

// Syllable-level akshara segmentation to align each swara & modifier precisely over/under its target syllable
function splitMalayalamSyllables(text) {
  if (!text) return [];
  let graphemes = [];
  if (typeof Intl !== 'undefined' && Intl.Segmenter) {
    const segmenter = new Intl.Segmenter('ml', { granularity: 'grapheme' });
    graphemes = Array.from(segmenter.segment(text), s => s.segment);
  } else {
    graphemes = text.match(/[\u0D00-\u0D7F][\u0D3E-\u0D4D\u0D57\u0D62\u0D63\u0D02\u0D03]*|[^\u0D00-\u0D7F]/gu) || [text];
  }

  const VIRAMA = '\u0D4D';
  const syllables = [];
  for (const g of graphemes) {
    if (syllables.length > 0 && (
      syllables[syllables.length - 1].endsWith(VIRAMA) ||
      (syllables[syllables.length - 1].length === 1 && syllables[syllables.length - 1] >= '\u0D7A' && syllables[syllables.length - 1] <= '\u0D7F') ||
      syllables[syllables.length - 1] === '൪'
    )) {
      syllables[syllables.length - 1] += g;
    } else {
      syllables.push(g);
    }
  }
  return syllables;
}

// Live Vedic HTML Accent Renderer (Stacked Red Swaras above without parens, Blue Modifiers)
function renderVedicHTML(text) {
  if (!text) return '';

  const tokens = text.split(/(\s+|[।॥])/g);
  let html = '';

  for (const token of tokens) {
    if (!token) continue;
    if (/^\s+$/.test(token)) {
      html += ' ';
      continue;
    }
    if (token === '।' || token === '॥') {
      html += `<span class="danda">${token}</span>`;
      continue;
    }

    // Match chunks: BaseAksharas + (SwaraLetterOrModifier)*
    let wordHtml = '';
    const chunkRegex = /([^\s()_.,]+)?((?:\([^()]+\)|[_,.])*)/gu;
    let m;
    while ((m = chunkRegex.exec(token)) !== null) {
      if (m.index === chunkRegex.lastIndex) {
        chunkRegex.lastIndex++;
      }
      const base = m[1] || '';
      const extras = m[2] || '';
      if (!base && !extras) continue;

      let swaraLetter = '';
      let modifiersHtml = '';
      let hasModB = false;

      // Parse all parens and punctuation in extras
      const parenRegex = /\(([^()]+)\)|(_|,|\.)/g;
      let pm;
      while ((pm = parenRegex.exec(extras)) !== null) {
        const inner = pm[1] ? pm[1].trim() : pm[2];
        if (inner === 'C' || inner === 'c' || inner === '·') {
          modifiersHtml += '<span class="swara-mod mod-c" title="MOD-C: Upper Shoulder Dot">&#xE001;</span>';
        } else if (inner === 'H' || inner === 'h' || inner === '|') {
          modifiersHtml += '<span class="swara-mod mod-h" title="MOD-H: High Pitch Swarita">&#xE00C;</span>';
        } else if (inner === 'G' || inner === 'g' || inner === '\\') {
          modifiersHtml += '<span class="swara-mod mod-g" title="MOD-G: Lower Under-Slash (\\)">&#xE003;</span>';
        } else if (inner === 'A' || inner === 'a' || inner === '⁀') {
          modifiersHtml += '<span class="swara-mod mod-a" title="MOD-A: Melodic Arc (⁀)">&#xE004;</span>';
        } else if (inner === 'A1' || inner === 'a1' || inner === 'A_1' || inner === 'a_1') {
          modifiersHtml += '<span class="swara-mod mod-a1" title="MOD-A1: Arc over Danda">&#xE00D;</span>';
        } else if (inner === 'D' || inner === 'd' || inner === '∧' || inner === 'Ʌ') {
          modifiersHtml += '<span class="swara-mod mod-d" title="MOD-D: Chevron Roof (∧)">&#xE006;</span>';
        } else if (inner === 'D1' || inner === 'd1' || inner === 'D_1' || inner === 'd_1' || inner === '↗') {
          modifiersHtml += '<span class="swara-mod mod-d1" title="MOD-D1: Rising Stroke (↗)">&#xE00E;</span>';
        } else if (inner === 'D2' || inner === 'd2' || inner === 'D_2' || inner === 'd_2' || inner === '✓') {
          modifiersHtml += '<span class="swara-mod mod-d2" title="MOD-D2: Check Tick (✓)">&#xE00F;</span>';
        } else if (inner === 'I' || inner === 'i' || inner === '⫽') {
          modifiersHtml += '<span class="swara-mod mod-i" title="MOD-I: Double Shoulder Dash (⫽)">&#xE02A;</span>';
        } else if (inner === 'J' || inner === 'j' || inner === '¯') {
          modifiersHtml += '<span class="swara-mod mod-j" title="MOD-J: Overhead Horizontal Bar (¯)">&#xE02B;</span>';
        } else if (inner === 'B1' || inner === 'b1' || inner === 'B_1' || inner === 'b_1') {
          modifiersHtml += '<span class="swara-mod mod-b1" title="MOD-B1: Diagonal Bridging Slash (/)">&#xE02C;</span>';
        } else if (inner === 'K' || inner === 'k' || inner === '⨯' || inner === 'x' || inner === 'X') {
          modifiersHtml += '<span class="swara-mod mod-k" title="MOD-K: Shoulder Cross Mark (⨯)">&#xE02D;</span>';
        } else if (inner === 'B' || inner === 'b' || inner === '^') {
          hasModB = true;
        } else if (inner === 'E' || inner === 'e' || inner === '┃') {
          modifiersHtml += '<span class="swara-mod mod-e" title="MOD-E: Bold Tone Column (┃)">&#xE002;</span>';
        } else if (inner === 'F' || inner === 'f' || inner === '╷' || inner === '\uE008') {
          modifiersHtml += '<span class="swara-mod mod-f" title="MOD-F: Danda with Overhead Dot (╷)">&#xE008;</span>';
        } else if (inner === '_') {
          modifiersHtml += '<span class="swara-mod mod-under" title="MOD-UNDERBAR">_</span>';
        } else if (inner === ',') {
          modifiersHtml += '<span class="swara-mod mod-comma" title="MOD-COMMA">,</span>';
        } else if (inner === '.') {
          modifiersHtml += '<span class="swara-mod mod-dot" title="MOD-DOT">.</span>';
        } else {
          // Authentic Swara letter: mapped to JaimineeyaSwara custom glyphs
          swaraLetter = getCanonicalSwaraGlyph(inner);
        }
      }

      // Split base into syllables so that modifiers attach strictly to the final syllable
      const syllables = splitMalayalamSyllables(base);
      const lastSyllable = syllables.pop() || '';

      // Preceding syllables are plain aksharas
      for (const syl of syllables) {
        wordHtml += `<span class="akshara-base">${syl}</span>`;
      }

      // If this syllable has Mod-B (Peak Caret with embedded swara on peak)
      if (hasModB) {
        const caretGroup = `<span class="swara-mod mod-b"><span class="caret-glyph">&#xE005;</span><span class="swara-on-caret">${swaraLetter}</span></span>`;
        wordHtml += `<span class="akshara-base">${lastSyllable}${modifiersHtml}${caretGroup}</span>`;
      } else if (swaraLetter && lastSyllable) {
        wordHtml += `<ruby class="vedic-ruby"><rb class="akshara-base">${lastSyllable}${modifiersHtml}</rb><rt class="swara-above">${swaraLetter}</rt></ruby>`;
      } else if (swaraLetter && !lastSyllable) {
        wordHtml += `<ruby class="vedic-ruby"><rb class="akshara-base">&nbsp;${modifiersHtml}</rb><rt class="swara-above">${swaraLetter}</rt></ruby>`;
      } else if (lastSyllable || modifiersHtml) {
        wordHtml += `<span class="akshara-base">${lastSyllable}${modifiersHtml}</span>`;
      }
    }

    html += `<span class="mantra-word">${wordHtml || token}</span>`;
  }

  return html;
}

function updateDisplays() {
  const rawText = elements.mainVedicEditor.value;
  elements.renderedVedicDisplay.innerHTML = renderVedicHTML(rawText);
}

// Insert Text at Cursor Position
function insertAtCursor(textToInsert) {
  const textarea = elements.mainVedicEditor;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = textarea.value;

  const before = text.substring(0, start);
  const after = text.substring(end, text.length);

  textarea.value = before + textToInsert + after;
  textarea.selectionStart = textarea.selectionEnd = start + textToInsert.length;
  textarea.focus();
  
  updateDisplays();
}

// Toggle Side-by-Side vs Stacked Top-Bottom Layout
function toggleLayout() {
  state.isStacked = !state.isStacked;
  elements.workspaceGrid.classList.toggle('stacked', state.isStacked);
  elements.layoutLabel.textContent = state.isStacked ? 'Side-by-Side' : 'Stacked Layout';
  setTimeout(fitToWidth, 100);
}

// Save Current Samam back to Master File
async function saveCurrentSamam() {
  const sec = state.data.sections[state.currentSectionIdx];
  const subsec = sec.subsections[state.currentSubsecIdx];
  const samam = subsec.samams[state.currentSamamIdx];
  const newText = elements.mainVedicEditor.value;

  elements.saveBtn.disabled = true;
  elements.curationStatus.textContent = "Saving & Validating...";

  try {
    const resp = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subsec_id: subsec.id,
        samam_num: samam.num,
        new_text: newText
      })
    });

    const res = await resp.json();
    if (res.success) {
      showToast("Saved & Validated 100% in Master File!");
      elements.curationStatus.textContent = "Saved & Valid";
      samam.text = newText;
    } else {
      showToast(`Save Error: ${res.error}`, 5000, true);
      elements.curationStatus.textContent = "Validation Failed";
    }
  } catch (err) {
    showToast("Network or Server error during save", 4000, true);
    console.error(err);
  } finally {
    elements.saveBtn.disabled = false;
  }
}

// Event Listeners
function setupEventListeners() {
  elements.sectionSelect.addEventListener('change', (e) => selectSection(parseInt(e.target.value)));
  elements.subsectionSelect.addEventListener('change', (e) => selectSubsection(parseInt(e.target.value)));
  elements.samamSelect.addEventListener('change', (e) => selectSamam(parseInt(e.target.value)));

  // Direct Jump
  if (elements.directSubBtn) {
    elements.directSubBtn.addEventListener('click', handleDirectSubJump);
  }
  if (elements.directSubInput) {
    elements.directSubInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleDirectSubJump();
    });
  }

  // Navigation
  elements.prevBtn.addEventListener('click', () => navigateSamam(-1));
  elements.nextBtn.addEventListener('click', () => navigateSamam(1));
  elements.layoutToggleBtn.addEventListener('click', toggleLayout);
  if (elements.fontToggleBtn) {
    elements.fontToggleBtn.addEventListener('click', toggleFont);
  }

  // Toolbar
  elements.prevPageBtn.addEventListener('click', () => loadManuscriptPage(Math.max(1, state.currentPage - 1)));
  elements.nextPageBtn.addEventListener('click', () => loadManuscriptPage(state.currentPage + 1));
  
  elements.zoomInBtn.addEventListener('click', () => { state.zoom *= 1.25; applyTransform(); });
  elements.zoomOutBtn.addEventListener('click', () => { state.zoom *= 0.8; applyTransform(); });
  elements.fitWidthBtn.addEventListener('click', fitToWidth);
  elements.invertBtn.addEventListener('click', () => {
    state.inverted = !state.inverted;
    elements.manuscriptImg.classList.toggle('inverted', state.inverted);
  });

  // Editor Input
  elements.mainVedicEditor.addEventListener('input', updateDisplays);
  elements.saveBtn.addEventListener('click', saveCurrentSamam);

  // Modifier Palette Clicks
  document.querySelectorAll('.mod-chip').forEach(btn => {
    btn.addEventListener('click', () => insertAtCursor(btn.getAttribute('data-mod')));
  });

  // Global & In-Editor Hotkeys
  window.addEventListener('keydown', handleHotkeys);
}

function navigateSamam(delta) {
  const sec = state.data.sections[state.currentSectionIdx];
  const subsec = sec.subsections[state.currentSubsecIdx];
  
  let newSamIdx = state.currentSamamIdx + delta;
  if (newSamIdx >= 0 && newSamIdx < subsec.samams.length) {
    selectSamam(newSamIdx);
  } else if (delta > 0 && state.currentSubsecIdx + 1 < sec.subsections.length) {
    selectSubsection(state.currentSubsecIdx + 1);
  } else if (delta < 0 && state.currentSubsecIdx - 1 >= 0) {
    state.currentSubsecIdx -= 1;
    const prevSub = sec.subsections[state.currentSubsecIdx];
    selectSubsection(state.currentSubsecIdx);
    selectSamam(prevSub.samams.length - 1);
  }
}

function handleHotkeys(e) {
  // 1. Save shortcut: Ctrl+S or Cmd+S
  if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
    e.preventDefault();
    saveCurrentSamam();
    return;
  }

  // 2. Navigation shortcuts: Alt+Left / Alt+Right or Ctrl+[ / Ctrl+]
  if ((e.altKey && e.key === 'ArrowLeft') || ((e.ctrlKey || e.metaKey) && e.key === '[')) {
    e.preventDefault();
    navigateSamam(-1);
    return;
  }
  if ((e.altKey && e.key === 'ArrowRight') || ((e.ctrlKey || e.metaKey) && e.key === ']')) {
    e.preventDefault();
    navigateSamam(1);
    return;
  }

  // 3. In-Editor Modifier Insertion Shortcuts (Alt + Key)
  if (e.altKey && !e.ctrlKey && !e.metaKey) {
    const key = e.key.toLowerCase();
    const shortcutMap = {
      'h': '(H)',
      'g': '(G)',
      'c': '(C)',
      'a': '(A)',
      '1': '(A1)',
      'b': '(B)',
      'd': '(D)',
      'e': '(E)',
      'u': '_',
      '_': '_',
      ',': ',',
      '.': '.'
    };

    if (shortcutMap[key] || shortcutMap[e.key]) {
      e.preventDefault();
      insertAtCursor(shortcutMap[key] || shortcutMap[e.key]);
      return;
    }
  }
}

function showToast(msg, duration = 3000, isError = false) {
  const t = elements.toast;
  t.textContent = msg;
  t.style.borderColor = isError ? 'var(--accent-red)' : 'var(--accent-gold)';
  t.style.display = 'block';
  setTimeout(() => { t.style.display = 'none'; }, duration);
}

// Start
document.addEventListener('DOMContentLoaded', init);
