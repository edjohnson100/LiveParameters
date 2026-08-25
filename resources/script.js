document.addEventListener('DOMContentLoaded', function() {
    // Theme Manager
    initThemeManager();

    // Tabs
    const savedTab = localStorage.getItem('live_active_tab') || 'tab-params';
    switchTab(savedTab);

    // Fav Filter
    const favCheck = document.getElementById('favFilterCheck');
    const savedFavState = localStorage.getItem('live_fav_only');
    favCheck.checked = (savedFavState === 'true');
    favCheck.addEventListener('change', function(e) {
        localStorage.setItem('live_fav_only', e.target.checked);
        if (lastReceivedData) renderUI(lastReceivedData);
    });

    // Search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function(e) {
        searchQuery = e.target.value.toLowerCase();
        if (lastReceivedData) renderUI(lastReceivedData);
    });

    // Buttons
    const scanBtn = document.getElementById('scanBtn');
    if (scanBtn) scanBtn.addEventListener('click', (e) => { e.stopPropagation(); refreshData(); });

    // CREATE PARAMETER LOGIC
    const createBtn = document.getElementById('createBtn');
    if (createBtn) {
        createBtn.addEventListener('click', function() {
            const name = document.getElementById('new_name').value.trim();
            const dropdownVal = document.getElementById('new_unit').value;
            let unit = dropdownVal;
            let expr = document.getElementById('new_expr').value.trim();
            const comm = document.getElementById('new_comm').value.trim();

            if (dropdownVal === 'OTHER') {
                unit = document.getElementById('custom_unit').value.trim();
            }
            if (dropdownVal === 'TEXT') {
                unit = "";
                if (!expr.startsWith("'") || !expr.endsWith("'")) {
                    showStatus({message: "Text must be enclosed in single quotes. e.g. 'MyText'", type: "error"});
                    return;
                }
                const content = expr.substring(1, expr.length - 1);
                const unescapedQuote = /(?<!\\)'/.test(content);
                if (unescapedQuote) {
                    showStatus({message: "Internal quotes must be escaped with \\. e.g. 'Ed\\'s Button'", type: "error"});
                    return;
                }
            }

            if(!name || !expr) {
                showStatus({message: "Name and Expression required", type: "error"});
                return;
            }

            showStatus({message: "Creating...", type: "info"});
            sendToFusion('create_param', {
                name: name, unit: unit, expression: expr, comment: comm
            });
        });
    }

    waitForFusion();
});

// --- UI HELPERS ---

function toggleSection(id) {
    const section = document.getElementById(id);
    if (!section) return;
    section.classList.toggle('collapsed');
    const header = section.querySelector('.section-header[aria-expanded]');
    if (header) header.setAttribute('aria-expanded', String(!section.classList.contains('collapsed')));
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(tabId);
    if (panel) panel.classList.add('active');
    document.querySelectorAll('.tab-btn').forEach(btn => {
        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId)) {
            btn.classList.add('active');
        }
    });
    localStorage.setItem('live_active_tab', tabId);
}

function toggleCustomUnit(selectObj) {
    const customInput = document.getElementById('custom_unit');
    if (selectObj.value === 'OTHER') {
        customInput.style.display = 'block';
        customInput.focus();
    } else {
        customInput.style.display = 'none';
    }
}

function deleteParam(name) {
    if (confirm("Are you sure you want to permanently delete '" + name + "'?")) {
        showStatus({message: "Deleting...", type: "info"});
        sendToFusion('delete_param', { name: name });
    }
}

// --- EDIT MODAL LOGIC ---
function openEditModal(name, currentComment) {
    if (currentComment === 'null' || currentComment === null) currentComment = "";

    document.getElementById('editModalName').value = name;
    document.getElementById('editModalComment').value = currentComment;
    document.getElementById('editModalOldName').value = name;

    document.getElementById('editModal').style.display = 'flex';
    document.getElementById('editModalName').focus();
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function saveEditModal() {
    const oldName = document.getElementById('editModalOldName').value;
    const newName = document.getElementById('editModalName').value.trim();
    const newComment = document.getElementById('editModalComment').value.trim();

    if (!newName) {
        alert("Parameter name cannot be empty.");
        return;
    }

    closeEditModal();
    showStatus({message: "Saving...", type: "info"});

    sendToFusion('update_attributes', {
        old_name: oldName,
        new_name: newName,
        comment: newComment
    });
}

let statusTimeout;

function showStatus(data) {
    const box = document.getElementById('statusMessage');
    if (!box) return;

    // 1. Force display immediately
    box.innerText = data.message;
    box.className = 'status-box ' + (data.type || '');
    box.style.display = 'block';

    // 2. Clear any existing timer to prevent premature hiding
    if (statusTimeout) clearTimeout(statusTimeout);

    // 3. If Success: Clear Inputs
    if (data.type === 'success') {
        const newName = document.getElementById('new_name');
        if (newName) newName.value = '';
        const newExpr = document.getElementById('new_expr');
        if (newExpr) newExpr.value = '';
        const newComm = document.getElementById('new_comm');
        if (newComm) newComm.value = '';

        // Reset Unit Dropdown
        const newUnit = document.getElementById('new_unit');
        if (newUnit) newUnit.value = 'mm';
        const custUnit = document.getElementById('custom_unit');
        if (custUnit) custUnit.style.display = 'none';
    }

    // 4. Set NEW timer (3 seconds)
    statusTimeout = setTimeout(() => {
        box.style.display = 'none';
    }, 3000);
}

// --- THEME MANAGER ---
const THEME_VARS = [
    '--font-family', '--font-size-base',
    '--bg-body', '--text-main', '--text-sub', '--border-color',
    '--row-bg', '--row-border', '--input-bg', '--input-border', '--input-text',
    '--toggle-bg', '--header-hover',
    '--tab-bg', '--tab-active-bg', '--tab-text', '--tab-active-text',
    '--btn-primary', '--btn-primary-hover', '--btn-primary-text',
    '--btn-secondary', '--btn-secondary-hover', '--btn-secondary-text',
    '--btn-success', '--btn-success-hover', '--btn-success-text',
    '--status-success-bg', '--status-success-text', '--status-success-border',
    '--status-error-bg', '--status-error-text', '--status-error-border',
    '--status-info-bg', '--status-info-text', '--status-info-border',
    '--focus-ring', '--text-danger', '--overlay-bg'
];
const builtInThemeIds = new Set(['light', 'dark', 'sepia']);
let customThemes = JSON.parse(localStorage.getItem('live_custom_themes') || '{}');
let _importedThemesLoaded = false;
let themeSelector, themeRemoveBtn, fontFamilySelector, fontSizeSelector;

function initThemeManager() {
    themeSelector = document.getElementById('themeSelector');
    themeRemoveBtn = document.getElementById('themeRemoveBtn');
    fontFamilySelector = document.getElementById('fontFamilySelector');
    fontSizeSelector = document.getElementById('fontSizeSelector');

    themeRemoveBtn.addEventListener('click', removeSelectedTheme);
    themeSelector.addEventListener('change', changeTheme);

    for (const id in customThemes) addCustomOption(id);
    applyCustomThemeVars();

    const savedTheme = localStorage.getItem('live_theme') || 'dark';
    themeSelector.value = builtInThemeIds.has(savedTheme) || (savedTheme in customThemes) ? savedTheme : 'dark';
    changeTheme();
}

function applyCustomThemeVars() {
    let styleTag = document.getElementById('dynamic-theme-overrides');
    if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = 'dynamic-theme-overrides';
        document.head.appendChild(styleTag);
    }
    let out = '';
    for (const [themeId, themeVars] of Object.entries(customThemes)) {
        const decls = Object.entries(themeVars).map(([k, v]) => `${k}: ${v};`).join(' ');
        out += `[data-theme="${themeId}"] { ${decls} }\n`;
    }
    styleTag.textContent = out;
}

function findThemeOption(id) {
    return Array.from(themeSelector.options).find(o => o.value === id) || null;
}

function addCustomOption(id) {
    if (!findThemeOption(id)) {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = `${id} (custom)`;
        themeSelector.appendChild(opt);
    }
}

function mergeImportedThemes(hostThemes) {
    if (_importedThemesLoaded || !hostThemes || Object.keys(hostThemes).length === 0) return;
    _importedThemesLoaded = true;
    for (const id in hostThemes) {
        customThemes[id] = hostThemes[id];
        if (!builtInThemeIds.has(id)) addCustomOption(id);
    }
    localStorage.setItem('live_custom_themes', JSON.stringify(customThemes));
    applyCustomThemeVars();
    syncFontSelectors();
}

function updateRemoveButtonState() {
    const id = themeSelector.value;
    const removable = !builtInThemeIds.has(id) && (id in customThemes);
    themeRemoveBtn.disabled = !removable;
    themeRemoveBtn.title = removable ? `Remove the "${id}" theme` : 'Select a custom (imported) theme to enable';
}

function changeTheme() {
    const id = themeSelector.value;
    document.documentElement.setAttribute('data-theme', id);
    localStorage.setItem('live_theme', id);
    updateRemoveButtonState();
    syncFontSelectors();
}

function syncFontSelectors() {
    if (!fontFamilySelector && !fontSizeSelector) return;
    const computed = getComputedStyle(document.documentElement);
    if (fontFamilySelector) {
        const fam = computed.getPropertyValue('--font-family').trim().replace(/"/g, "'");
        const match = Array.from(fontFamilySelector.options).find(o => o.value === fam);
        if (match) fontFamilySelector.value = match.value;
    }
    if (fontSizeSelector) {
        const size = computed.getPropertyValue('--font-size-base').trim();
        const match = Array.from(fontSizeSelector.options).find(o => o.value === size);
        if (match) fontSizeSelector.value = match.value;
    }
}

function updateActiveThemeProperty(prop, value) {
    const id = themeSelector.value;
    if (!customThemes[id]) customThemes[id] = {};
    customThemes[id][prop] = value;
    localStorage.setItem('live_custom_themes', JSON.stringify(customThemes));
    applyCustomThemeVars();
}

function removeSelectedTheme() {
    const id = themeSelector.value;
    if (builtInThemeIds.has(id) || !(id in customThemes)) return;
    if (!confirm(`Permanently remove the "${id}" theme? Re-import its .theme.json to bring it back.`)) return;
    delete customThemes[id];
    localStorage.setItem('live_custom_themes', JSON.stringify(customThemes));
    sendToFusion('remove_imported_theme', { id: id });
    const opt = findThemeOption(id);
    if (opt) opt.remove();
    applyCustomThemeVars();
    themeSelector.value = 'dark';
    changeTheme();
}

function requestImportTheme(type) {
    sendToFusion('import_theme', { file_type: type });
}

function requestExportTheme(type) {
    const id = themeSelector.value;
    let content, defaultName;
    if (type === 'css') {
        content = generateFullCSS();
        defaultName = 'style.css';
    } else {
        const computed = getComputedStyle(document.documentElement);
        const vars = {};
        THEME_VARS.forEach(v => { vars[v] = computed.getPropertyValue(v).trim(); });
        content = JSON.stringify({ id: id, vars: vars }, null, 2);
        defaultName = `${id}.theme.json`;
    }
    sendToFusion('export_theme', { file_type: type, content: content, default_name: defaultName });
}

// Dumps every known theme (built-in + custom) as a [data-theme="id"] block by
// briefly applying each id and reading its computed values -- avoids keeping a
// second, easily-stale copy of the built-in light/dark/sepia values in JS.
function generateFullCSS() {
    const originalTheme = document.documentElement.getAttribute('data-theme');
    const allIds = new Set([...builtInThemeIds, ...Object.keys(customThemes)]);
    let out = '';
    let i = 1;
    for (const id of allIds) {
        document.documentElement.setAttribute('data-theme', id);
        const computed = getComputedStyle(document.documentElement);
        out += `/* ${i}. ${id} */\n[data-theme="${id}"] {\n`;
        THEME_VARS.forEach(v => {
            out += `    ${v}: ${computed.getPropertyValue(v).trim()};\n`;
        });
        out += `}\n\n`;
        i++;
    }
    document.documentElement.setAttribute('data-theme', originalTheme);
    return out.trim() + '\n';
}

function parseStyleCSS(cssText) {
    const themeRegex = /(?:\/\*[\s\S]*?\*\/\s*)?(?:(:root)|\[data-theme=["']?([^"']+)["']?\])\s*\{([^}]+)\}/g;
    let match;
    const parsedThemes = {};
    while ((match = themeRegex.exec(cssText)) !== null) {
        const themeId = match[1] ? 'light' : match[2];
        const content = match[3];
        const vars = {};
        const varRegex = /(--[\w-]+)\s*:\s*([^;]+?)(?=\s*;|\s*$)/g;
        let vMatch;
        while ((vMatch = varRegex.exec(content)) !== null) {
            vars[vMatch[1].trim()] = vMatch[2].trim();
        }
        parsedThemes[themeId] = vars;
    }
    return parsedThemes;
}

function resetThemeCache() {
    if (!confirm('This will permanently delete all custom imported themes. Continue?')) return;
    localStorage.removeItem('live_custom_themes');
    localStorage.removeItem('live_theme');
    customThemes = {};
    _importedThemesLoaded = false;
    sendToFusion('reset_imported_themes');
    themeSelector.querySelectorAll('option').forEach(opt => {
        if (!builtInThemeIds.has(opt.value)) opt.remove();
    });
    const styleTag = document.getElementById('dynamic-theme-overrides');
    if (styleTag) styleTag.textContent = '';
    themeSelector.value = 'dark';
    changeTheme();
}

function handleThemeImported(parsed) {
    if (parsed.file_type === 'css') {
        try {
            const parsedThemes = parseStyleCSS(parsed.content);
            let firstCustomId = null;
            for (const id in parsedThemes) {
                customThemes[id] = parsedThemes[id];
                if (!builtInThemeIds.has(id)) {
                    addCustomOption(id);
                    if (!firstCustomId) firstCustomId = id;
                }
                sendToFusion('save_imported_theme', { id: id, vars: parsedThemes[id] });
            }
            localStorage.setItem('live_custom_themes', JSON.stringify(customThemes));
            applyCustomThemeVars();
            if (firstCustomId) {
                themeSelector.value = firstCustomId;
                changeTheme();
            } else {
                syncFontSelectors();
            }
        } catch (e) { console.log('Invalid theme CSS', e); }
    } else {
        try {
            const themeData = JSON.parse(parsed.content);
            if (themeData.vars && themeData.id !== undefined) {
                customThemes[themeData.id] = themeData.vars;
                localStorage.setItem('live_custom_themes', JSON.stringify(customThemes));
                sendToFusion('save_imported_theme', { id: themeData.id, vars: themeData.vars });
                addCustomOption(themeData.id);
                applyCustomThemeVars();
                themeSelector.value = themeData.id;
                changeTheme();
            }
        } catch (e) { console.log('Invalid theme JSON', e); }
    }
}

// --- FUSION BRIDGE ---

let lastReceivedData = null;
let searchQuery = "";
let connectionAttempts = 0;
const MAX_ATTEMPTS = 20;

function waitForFusion() {
    if (window.adsk) {
        if (window.adsk.fusion && window.adsk.fusion.on) {
            window.adsk.fusion.on('update_ui', function(jsonString) {
                renderUI(JSON.parse(jsonString));
            });
        }
        window.fusionJavaScriptHandler = {
            handle: function(action, data) {
                try {
                    var parsed = typeof data === 'string' ? JSON.parse(data) : data;
                    if (action === 'update_ui') renderUI(parsed);
                    else if (action === 'notification') showStatus(parsed);
                    else if (action === 'theme_imported') handleThemeImported(parsed);
                } catch (e) { console.error(e); }
                return "OK";
            }
        };
        refreshData();
    } else {
        connectionAttempts++;
        if (connectionAttempts > MAX_ATTEMPTS) {
            const pContainer = document.getElementById('paramList');
            if(pContainer) pContainer.innerHTML = '<div class="empty-state" style="color:var(--text-danger)">Fusion Connection Timeout</div>';
            return;
        }
        setTimeout(waitForFusion, 500);
    }
}

function sendToFusion(action, data = {}) {
    data.action = action;
    try {
        const json = JSON.stringify(data);
        if (window.adsk && window.adsk.fusion && window.adsk.fusion.sendCommand) {
            window.adsk.fusion.sendCommand(json);
        } else if (window.adsk && window.adsk.fusionSendData) {
            window.adsk.fusionSendData('send', json);
        }
    } catch (e) {}
}

function refreshData() { sendToFusion('refresh_data'); }

// Free text (expressions, comments) can legally contain " or & (e.g. a TEXT
// parameter's expression like 'He said "hi"') and gets embedded straight into
// double-quoted HTML attributes -- escape both or a literal " breaks the
// attribute and corrupts the row's markup.
function escapeHtmlAttr(s) {
    return String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;');
}

function renderUI(data) {
    lastReceivedData = data;
    if (data.addin_version) {
        document.getElementById('versionTag').textContent = 'v' + data.addin_version;
        const footerVersionEl = document.getElementById('footerVersion');
        if (footerVersionEl) footerVersionEl.textContent = 'v' + data.addin_version + ', August 2026';
    }
    if (data.imported_themes) mergeImportedThemes(data.imported_themes);
    const docNameEl = document.getElementById('docName');
    if (docNameEl) docNameEl.innerText = data.doc_name || "Unknown Design";

    const pContainer = document.getElementById('paramList');
    const favOnly = document.getElementById('favFilterCheck').checked;

    if (pContainer) {
        pContainer.innerHTML = '';
        let paramsToShow = data.parameters || [];

        if (favOnly) paramsToShow = paramsToShow.filter(p => p.isFavorite);

        if (searchQuery) {
            paramsToShow = paramsToShow.filter(p =>
                p.name.toLowerCase().includes(searchQuery)
            );
        }

        if (paramsToShow.length === 0) {
            let msg = 'No User Parameters found.';
            if (data.parameters.length > 0) {
                if (searchQuery) msg = 'No matching parameters found.';
                else if (favOnly) msg = 'No Favorites marked. Uncheck "Favs Only".';
            }
            pContainer.innerHTML = `<div class="empty-state">${msg}</div>`;
        } else {
            paramsToShow.forEach(param => {
                const row = document.createElement('div');
                row.className = 'param-row';
                const starColor = param.isFavorite ? '#ff9e3b' : '#555';
                const displayComment = param.comment || "";
                const encodedComment = encodeURIComponent(displayComment).replace(/'/g, '%27');
                const titleComment = escapeHtmlAttr(displayComment);

                row.innerHTML = `
                    <div class="param-label" title="${param.name}\n${titleComment}">
                        <span style="color:${starColor}; margin-right:6px; cursor:pointer;" onclick="toggleFavorite('${param.name}')">★</span>
                        ${param.name}
                    </div>
                    <div class="param-input">
                        <input type="text" value="${escapeHtmlAttr(param.expression)}"
                            onchange="updateParam('${param.name}', this.value)"
                            onkeydown="if(event.key==='Enter')this.blur()">

                        <button class="icon-action-btn" title="Edit Name & Comment"
                            onclick="openEditModal('${param.name}', decodeURIComponent('${encodedComment}'))">✎</button>

                        <button class="icon-action-btn del-btn" title="Delete Parameter"
                            onclick="deleteParam('${param.name}')">×</button>
                    </div>
                `;
                pContainer.appendChild(row);
            });
        }
    }
}

function updateParam(name, value) { sendToFusion('update_param', { name: name, value: value }); }
function toggleFavorite(name) { sendToFusion('toggle_favorite', { name: name }); }
