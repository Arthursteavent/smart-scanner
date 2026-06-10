// State
let selectedPaths = [];
let currentTree = null;

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page-view');
const consoleOutput = document.getElementById('console-output');
const topBarTitle = document.getElementById('top-bar-title');

// Scan Page Elements
const btnAddFolder = document.getElementById('btn-add-folder');
const folderListBody = document.getElementById('folder-list-body');
const badgeActiveCount = document.getElementById('badge-active-count');
const statFolderCount = document.getElementById('stat-folder-count');
const btnStartScan = document.getElementById('btn-start-scan');
const scanProgressSection = document.getElementById('scan-progress-section');
const scanStatusTitle = document.getElementById('scan-status-title');
const scanPct = document.getElementById('scan-pct');
const scanProgressFill = document.getElementById('scan-progress-fill');

// Preview Page Elements
const treeView = document.getElementById('tree-view');
const btnDeleteDuplicates = document.getElementById('btn-delete-duplicates');
const btnApplyOrg = document.getElementById('btn-apply-org');
const btnUndo = document.getElementById('btn-undo');
const orgProgressSection = document.getElementById('org-progress-section');
const orgPct = document.getElementById('org-pct');
const orgProgressFill = document.getElementById('org-progress-fill');

// Settings Page Elements
const targetFolderInput = document.getElementById('target-folder-input');
const btnBrowseTarget = document.getElementById('btn-browse-target');
const btnSaveSettings = document.getElementById('btn-save-settings');
const settingsMsg = document.getElementById('settings-msg');

// ==========================================
// Navigation
// ==========================================
const pageTitles = {
    'scan-page': 'Langkah 1: Konfigurasi Sumber',
    'preview-page': 'Langkah 2: Tinjauan Organisasi',
    'settings-page': 'Pengaturan Sistem'
};

const activeClasses = ['text-primary', 'font-bold', 'bg-primary/10', 'border-primary'];
const inactiveClasses = ['text-[#cac3d8]', 'hover:text-white', 'hover:bg-surface-container-high', 'border-transparent'];

navItems.forEach(item => {
    item.addEventListener('click', () => {
        const targetId = item.dataset.target;
        switchPage(targetId);
    });
});

function switchPage(pageId) {
    // Update Nav
    navItems.forEach(n => {
        if (n.dataset.target === pageId) {
            n.classList.remove(...inactiveClasses);
            n.classList.add(...activeClasses);
        } else {
            n.classList.remove(...activeClasses);
            n.classList.add(...inactiveClasses);
        }
    });

    // Update Pages
    pages.forEach(p => {
        if (p.id === pageId) {
            p.classList.remove('hidden', 'opacity-0', 'pointer-events-none');
            p.classList.add('active', 'opacity-100');
        } else {
            p.classList.remove('active', 'opacity-100');
            p.classList.add('hidden', 'opacity-0', 'pointer-events-none');
        }
    });

    topBarTitle.innerText = pageTitles[pageId];
}

// Ensure default view
switchPage('scan-page');

// ==========================================
// Eel Callbacks (Called from Python)
// ==========================================
eel.expose(append_log);
function append_log(message) {
    const p = document.createElement('p');
    p.className = 'text-on-surface-variant/80 transition-opacity duration-300';
    
    // Style formatting based on message prefix
    if (message.includes('! Error') || message.includes('! Warning')) {
        p.innerHTML = `<span class='text-error/80 mr-2'>[ERROR]</span> ${message}`;
        p.classList.replace('text-on-surface-variant/80', 'text-error/90');
    } else if (message.startsWith('>')) {
        p.innerHTML = `<span class='text-on-surface-variant/40 mr-2'>[INFO]</span> ${message.substring(1).trim()}`;
    } else {
        p.innerHTML = `<span class='text-primary/60 mr-2'>[SYS]</span> ${message}`;
    }

    consoleOutput.appendChild(p);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
    
    // Keep log concise
    if(consoleOutput.children.length > 50) {
        consoleOutput.removeChild(consoleOutput.children[0]);
    }
}

eel.expose(update_status);
function update_status(message, progress) {
    scanStatusTitle.innerText = message;
    if (progress !== null && progress !== undefined) {
        const pct = Math.round(progress * 100);
        scanPct.innerText = `${pct}%`;
        scanProgressFill.style.width = `${pct}%`;
    }
}

eel.expose(scan_complete);
function scan_complete(success, message, tree) {
    btnStartScan.disabled = false;
    btnAddFolder.disabled = false;
    
    if (success) {
        scanPct.innerText = '100%';
        scanProgressFill.style.width = '100%';
        currentTree = tree;
        renderTree(tree);
        btnApplyOrg.disabled = false;
        
        if (tree && tree['Duplicates']) {
            let dupCount = 0;
            for (const key in tree['Duplicates']) {
                if (Array.isArray(tree['Duplicates'][key])) {
                    dupCount += tree['Duplicates'][key].length;
                } else if (tree['Duplicates'][key] && Array.isArray(tree['Duplicates'][key]['_files'])) {
                    dupCount += tree['Duplicates'][key]['_files'].length;
                }
            }
            btnDeleteDuplicates.innerHTML = `<span class="material-symbols-outlined text-sm">delete</span> Hapus Duplikat (${dupCount} File)`;
            btnDeleteDuplicates.style.display = 'inline-flex';
        } else {
            btnDeleteDuplicates.style.display = 'none';
        }
        
        // Auto navigate to preview
        setTimeout(() => switchPage('preview-page'), 1500);
    } else {
        alert(message);
    }
}

eel.expose(update_org_progress);
function update_org_progress(progress) {
    const pct = Math.round(progress * 100);
    orgPct.innerText = `${pct}%`;
    orgProgressFill.style.width = `${pct}%`;
}

const successModal = document.getElementById('success-modal');
const successModalContent = document.getElementById('success-modal-content');
const successModalMessage = document.getElementById('success-modal-message');
const btnCloseModal = document.getElementById('btn-close-modal');

if (btnCloseModal) {
    btnCloseModal.addEventListener('click', () => {
        successModal.classList.remove('opacity-100', 'pointer-events-auto');
        successModal.classList.add('opacity-0', 'pointer-events-none');
        successModalContent.classList.remove('scale-100');
        successModalContent.classList.add('scale-95');
    });
}

eel.expose(org_complete);
function org_complete(success, message) {
    btnApplyOrg.disabled = false;
    if (success) {
        orgPct.innerText = '100%';
        orgProgressFill.style.width = '100%';
        
        let totalFiles = 0;
        let totalCategories = 0;
        if (currentTree) {
            totalCategories = Object.keys(currentTree).filter(k => k !== 'Duplicates').length;
            for (const cat in currentTree) {
                if (cat === 'Duplicates') continue;
                for (const subcat in currentTree[cat]) {
                    if (Array.isArray(currentTree[cat][subcat])) {
                        totalFiles += currentTree[cat][subcat].length;
                    } else if (currentTree[cat][subcat] && Array.isArray(currentTree[cat][subcat]['_files'])) {
                        totalFiles += currentTree[cat][subcat]['_files'].length;
                    }
                }
            }
        }
        
        const modalStatTotal = document.getElementById('modal-stat-total');
        const modalStatCat = document.getElementById('modal-stat-categories');
        if (modalStatTotal) modalStatTotal.innerText = totalFiles;
        if (modalStatCat) modalStatCat.innerText = totalCategories;

        successModalMessage.innerText = "Keren! File-file Anda sudah berhasil dirapikan ke folder tujuan dengan sukses.";
        successModal.classList.remove('opacity-0', 'pointer-events-none');
        successModal.classList.add('opacity-100', 'pointer-events-auto');
        successModalContent.classList.remove('scale-95');
        successModalContent.classList.add('scale-100');
    } else {
        alert('Gagal: ' + message);
    }
}

// ==========================================
// Scan Page Logic
// ==========================================
btnAddFolder.addEventListener('click', async () => {
    const path = await eel.select_folder()();
    if (path && !selectedPaths.includes(path)) {
        selectedPaths.push(path);
        updateFolderList();
    }
});

function updateFolderList() {
    folderListBody.innerHTML = '';
    
    badgeActiveCount.innerText = `${selectedPaths.length} Aktif`;
    statFolderCount.innerText = selectedPaths.length;
    
    if (selectedPaths.length === 0) {
        folderListBody.innerHTML = `
            <tr id="empty-folder-row">
                <td colspan="3" class="px-4 py-8 text-center text-[#cac3d8] italic panel-inset">
                    Belum ada folder yang ditambahkan.
                </td>
            </tr>
        `;
        btnStartScan.disabled = true;
        return;
    }

    btnStartScan.disabled = false;

    selectedPaths.forEach(path => {
        const tr = document.createElement('tr');
        tr.className = 'group hover:bg-primary-container/5 transition-colors';
        
        // Extract a short name for UI
        const parts = path.split(/\\|\//);
        const folderName = parts[parts.length - 1] || path;

        tr.innerHTML = `
            <td class="px-4 py-3 border-r border-outline-variant/30">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 border border-outline-variant/50 rounded-sm bg-surface-container-highest flex items-center justify-center text-primary shrink-0">
                        <span class="material-symbols-outlined text-sm">folder</span>
                    </div>
                    <div class="flex flex-col overflow-hidden">
                        <span class="text-sm font-bold text-white truncate">${folderName}</span>
                        <span class="text-[10px] text-[#cac3d8] truncate">${path}</span>
                    </div>
                </div>
            </td>
            <td class="px-4 py-3 text-xs text-[#cac3d8] border-r border-outline-variant/30">Menunggu Scan</td>
            <td class="px-4 py-3 text-center">
                <button class="text-error/60 hover:text-error transition-colors" onclick="removeFolder('${path.replace(/\\\\/g, '\\\\\\\\')}')">
                    <span class="material-symbols-outlined text-sm">delete</span>
                </button>
            </td>
        `;
        folderListBody.appendChild(tr);
    });
}

window.removeFolder = function(path) {
    selectedPaths = selectedPaths.filter(p => p !== path);
    updateFolderList();
}

btnStartScan.addEventListener('click', () => {
    if (selectedPaths.length === 0) return;
    
    btnStartScan.disabled = true;
    btnAddFolder.disabled = true;
    
    scanStatusTitle.innerText = "Mempersiapkan Indeks...";
    scanPct.innerText = "0%";
    scanProgressFill.style.width = "0%";
    
    eel.run_scan_and_ai(selectedPaths)();
});

// ==========================================
// Preview Page Logic
// ==========================================
function renderTree(tree) {
    treeView.innerHTML = '';
    if (!tree || Object.keys(tree).length === 0) {
        treeView.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full opacity-50">
                <span class="material-symbols-outlined text-6xl mb-md">account_tree</span>
                <p>Tidak ada data untuk ditampilkan.</p>
            </div>
        `;
        return;
    }

    function createNode(name, content, isRoot = false) {
        const node = document.createElement('div');
        node.className = 'tree-node';
        
        const cat = document.createElement('div');
        cat.className = 'tree-category';
        cat.innerHTML = `<span class="material-symbols-outlined tree-icon">folder_open</span> ${name}`;
        
        const childrenContainer = document.createElement('div');
        childrenContainer.style.display = 'block';

        cat.addEventListener('click', () => {
            const isHidden = childrenContainer.style.display === 'none';
            childrenContainer.style.display = isHidden ? 'block' : 'none';
            cat.querySelector('.material-symbols-outlined').innerText = isHidden ? 'folder_open' : 'folder';
        });

        node.appendChild(cat);
        node.appendChild(childrenContainer);

        if (Array.isArray(content)) {
            content.forEach(file => {
                const fNode = document.createElement('div');
                fNode.className = 'tree-file';
                fNode.innerHTML = `<span class="material-symbols-outlined tree-icon text-[#cac3d8]">description</span> ${file.name}`;
                childrenContainer.appendChild(fNode);
            });
        } else {
            for (const [key, value] of Object.entries(content)) {
                if (key === '_files') {
                    value.forEach(file => {
                        const fNode = document.createElement('div');
                        fNode.className = 'tree-file';
                        fNode.innerHTML = `<span class="material-symbols-outlined tree-icon text-[#cac3d8]">description</span> ${file.name}`;
                        childrenContainer.appendChild(fNode);
                    });
                } else {
                    childrenContainer.appendChild(createNode(key, value));
                }
            }
        }
        
        return node;
    }

    // Wrap the root nodes to apply some margin
    const rootContainer = document.createElement('div');
    rootContainer.className = 'space-y-sm';
    
    for (const [catName, catContent] of Object.entries(tree)) {
        rootContainer.appendChild(createNode(catName, catContent, true));
    }
    
    treeView.appendChild(rootContainer);
}

btnDeleteDuplicates.addEventListener('click', async () => {
    btnDeleteDuplicates.disabled = true;
    const result = await eel.delete_duplicates()();
    alert(`Berhasil menghapus ${result.deleted} file duplikat. Gagal: ${result.failed}`);
    currentTree = result.tree;
    renderTree(currentTree);
    btnDeleteDuplicates.style.display = 'none';
});

btnApplyOrg.addEventListener('click', async () => {
    btnApplyOrg.disabled = true;
    orgProgressSection.classList.remove('hidden');
    orgPct.innerText = "0%";
    orgProgressFill.style.width = "0%";
    
    await eel.apply_organization()();
});

btnUndo.addEventListener('click', async () => {
    btnUndo.disabled = true;
    const result = await eel.undo_last_operation()();
    alert(`Undo selesai. Berhasil: ${result.restored}, Gagal: ${result.failed}`);
    btnUndo.disabled = false;
});

// ==========================================
// Settings Page Logic
// ==========================================
btnBrowseTarget.addEventListener('click', async () => {
    const path = await eel.select_folder()();
    if (path) {
        targetFolderInput.value = path;
    }
});

btnSaveSettings.addEventListener('click', async () => {
    const settings = await eel.get_config()();
    settings.target_folder = targetFolderInput.value;
    settings.provider = "Local";
    
    await eel.save_settings(settings)();
    settingsMsg.innerText = "Pengaturan berhasil disimpan!";
    setTimeout(() => settingsMsg.innerText = "", 3000);
});

// Initialize Settings
window.addEventListener('DOMContentLoaded', async () => {
    const config = await eel.get_config()();
    if (config && config.target_folder) {
        targetFolderInput.value = config.target_folder;
    }
});
