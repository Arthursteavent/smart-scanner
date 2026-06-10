<!DOCTYPE html><html class="dark" lang="id"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Smart Organizer - Pindai Folder</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "secondary-container": "#00e3fd",
                        "on-secondary-fixed-variant": "#004f58",
                        "surface-bright": "#393841",
                        "surface-dim": "#13131b",
                        "on-secondary-container": "#00616d",
                        "surface-container-low": "#1b1b23",
                        "on-primary-fixed-variant": "#4f00d0",
                        "inverse-primary": "#6833ea",
                        "on-primary": "#370096",
                        "on-secondary-fixed": "#001f24",
                        "outline": "#948ea1",
                        "tertiary-container": "#b55800",
                        "on-surface-variant": "#cac3d8",
                        "on-primary-container": "#fcf6ff",
                        "on-background": "#e4e1ed",
                        "outline-variant": "#494455",
                        "on-tertiary-fixed": "#311300",
                        "surface-container-high": "#292932",
                        "primary-container": "#7c4dff",
                        "secondary": "#bdf4ff",
                        "on-tertiary": "#512400",
                        "primary-fixed": "#e8deff",
                        "inverse-on-surface": "#302f38",
                        "inverse-surface": "#e4e1ed",
                        "error-container": "#93000a",
                        "on-error": "#690005",
                        "on-primary-fixed": "#20005f",
                        "secondary-fixed": "#9cf0ff",
                        "on-tertiary-container": "#fff7f4",
                        "surface-container-highest": "#34343d",
                        "surface-variant": "#34343d",
                        "tertiary-fixed": "#ffdbc7",
                        "background": "#13131b",
                        "surface-tint": "#cdbdff",
                        "on-surface": "#e4e1ed",
                        "secondary-fixed-dim": "#00daf3",
                        "tertiary-fixed-dim": "#ffb688",
                        "surface": "#13131b",
                        "surface-container-lowest": "#0d0d15",
                        "on-tertiary-fixed-variant": "#733600",
                        "surface-container": "#1f1f27",
                        "primary-fixed-dim": "#cdbdff",
                        "tertiary": "#ffb688",
                        "error": "#ffb4ab",
                        "on-secondary": "#00363d",
                        "primary": "#cdbdff",
                        "on-error-container": "#ffdad6"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                    "spacing": {
                        "base": "8px",
                        "lg": "40px",
                        "sm": "12px",
                        "gutter": "24px",
                        "xs": "4px",
                        "md": "24px",
                        "xl": "64px",
                        "margin": "32px",
                        "container-max": "1440px"
                    },
                    "fontFamily": {
                        "label-sm": ["JetBrains Mono"],
                        "headline-md": ["Geist"],
                        "body-lg": ["Inter"],
                        "headline-lg": ["Geist"],
                        "headline-lg-mobile": ["Geist"],
                        "label-md": ["JetBrains Mono"],
                        "body-md": ["Inter"],
                        "body-sm": ["Inter"],
                        "display-lg": ["Geist"]
                    },
                    "fontSize": {
                        "label-sm": ["12px", {"lineHeight": "14px", "fontWeight": "500"}],
                        "headline-md": ["24px", {"lineHeight": "32px", "fontWeight": "600"}],
                        "body-lg": ["18px", {"lineHeight": "28px", "fontWeight": "400"}],
                        "headline-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "600"}],
                        "headline-lg-mobile": ["24px", {"lineHeight": "32px", "fontWeight": "600"}],
                        "label-md": ["14px", {"lineHeight": "16px", "letterSpacing": "0.02em", "fontWeight": "500"}],
                        "body-md": ["16px", {"lineHeight": "24px", "fontWeight": "400"}],
                        "body-sm": ["14px", {"lineHeight": "20px", "fontWeight": "400"}],
                        "display-lg": ["48px", {"lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700"}]
                    }
                },
            },
        }
    </script>
<style>
        body {
            background-color: #13131b;
            color: #e4e1ed;
            font-family: 'Inter', sans-serif;
        }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #1b1b23;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #494455;
            border-radius: 10px;
        }
        .glass-panel {
            background: rgba(31, 31, 39, 0.6);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(148, 142, 161, 0.15);
        }
        .gradient-primary {
            background: linear-gradient(135deg, #cdbdff 0%, #7c4dff 100%);
        }
        .gradient-secondary {
            background: linear-gradient(135deg, #ffb688 0%, #ffdbc7 100%);
        }
    </style>
</head>
<body class="overflow-hidden bg-surface">
<!-- Navigation Shell: SideNavBar -->
<aside class="fixed h-full w-[260px] left-0 top-0 border-r border-outline-variant bg-surface-container-low flex flex-col z-50">
<div class="px-md py-xl">
<h1 class="text-headline-md font-headline-md font-bold text-primary">Smart Organizer</h1>
<p class="text-label-md font-label-md text-on-surface-variant opacity-70">Enterprise Edition</p>
</div>
<nav class="flex-1 space-y-sm px-sm py-lg">
<!-- Active State -->
<a class="flex items-center gap-md px-md py-md text-primary font-bold bg-primary-container/10 border-l-2 border-primary transition-all duration-200 active:scale-[0.98]" href="#">
<span class="material-symbols-outlined" data-icon="folder_open">folder_open</span>
<span class="text-label-md font-label-md">Scan Folders</span>
</a>
<a class="flex items-center gap-md px-md py-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all duration-400" href="#">
<span class="material-symbols-outlined" data-icon="visibility">visibility</span>
<span class="text-label-md font-label-md">Preview</span>
</a>
<a class="flex items-center gap-md px-md py-md text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all duration-400" href="#">
<span class="material-symbols-outlined" data-icon="settings">settings</span>
<span class="text-label-md font-label-md">Settings</span>
</a>
</nav>

</aside>
<!-- Navigation Shell: TopAppBar -->
<header class="fixed top-0 right-0 w-[calc(100%-260px)] z-40 flex justify-between items-center h-16 px-gutter bg-surface-container/80 backdrop-blur-md border-b border-outline-variant shadow-sm ml-[260px]">
<div class="flex items-center gap-md">
<span class="text-label-md font-label-md text-on-surface-variant">Langkah 1: Konfigurasi Sumber</span>
</div>
<div class="flex items-center gap-lg">
<button class="text-on-surface-variant hover:text-primary transition-colors">
<span class="material-symbols-outlined" data-icon="notifications">notifications</span>
</button>

</div>
</header>
<!-- Main Content Canvas -->
<main class="ml-[260px] pt-16 h-screen flex flex-col">
<div class="flex-1 overflow-y-auto p-gutter custom-scrollbar bg-surface-dim">
<div class="max-w-container-max mx-auto space-y-xl">
<!-- Page Header -->
<div class="space-y-sm">
<h2 class="text-headline-lg font-headline-lg text-on-surface">Pindai Folder</h2>
<p class="text-body-md font-body-md text-on-surface-variant max-w-3xl">
                    Konfigurasikan direktori sumber Anda untuk mulai mengindeks file secara cerdas menggunakan algoritma klasifikasi otomatis kami.
                </p>
</div>
<!-- Scan Overview Stats Dashboard -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-lg">
<div class="glass-panel p-md rounded-xl flex flex-col gap-sm hover:border-primary/40 transition-colors">
<div class="flex items-center gap-md text-primary">
<span class="material-symbols-outlined">folder_managed</span>
<span class="text-label-md font-bold uppercase tracking-wider opacity-80">Total Folder</span>
</div>
<div class="text-display-lg leading-none font-display-lg">1</div>
<p class="text-label-sm text-on-surface-variant">Folder aktif yang dipantau</p>
</div>
<div class="glass-panel p-md rounded-xl flex flex-col gap-sm hover:border-primary/40 transition-colors">
<div class="flex items-center gap-md text-primary-fixed-dim">
<span class="material-symbols-outlined">description</span>
<span class="text-label-md font-bold uppercase tracking-wider opacity-80">Potensi File</span>
</div>
<div class="text-display-lg leading-none font-display-lg">~1.2k</div>
<p class="text-label-sm text-on-surface-variant">Estimasi item yang terdeteksi</p>
</div>
<div class="glass-panel p-md rounded-xl flex flex-col gap-sm hover:border-primary/40 transition-colors">
<div class="flex items-center gap-md text-tertiary">
<span class="material-symbols-outlined">timer</span>
<span class="text-label-md font-bold uppercase tracking-wider opacity-80">Estimasi Waktu</span>
</div>
<div class="text-display-lg leading-none font-display-lg">4m 12s</div>
<p class="text-label-sm text-on-surface-variant">Waktu pemrosesan indeks</p>
</div>
</div>
<!-- Folder Management Section -->
<div class="space-y-lg">
<div class="flex justify-between items-center">
<div class="flex items-center gap-md">
<h3 class="text-headline-md text-on-surface">Manajemen Path</h3>
<span class="px-sm py-xs bg-surface-container-high text-label-sm text-on-surface-variant rounded">1 Aktif</span>
</div>
<div class="flex gap-sm">
<button class="flex items-center gap-sm gradient-primary text-on-primary-container px-lg py-md rounded-xl font-bold hover:brightness-110 active:scale-95 transition-all shadow-lg shadow-primary/20">
<span class="material-symbols-outlined" data-icon="add">add</span>
<span class="text-label-md">Tambah Folder</span>
</button>
</div>
</div>
<!-- Structured List -->
<div class="space-y-md">
<div class="glass-panel rounded-xl overflow-hidden shadow-xl border-none">
<table class="w-full text-left border-collapse">
<thead>
<tr class="bg-surface-container-low text-label-sm text-on-surface-variant border-b border-outline-variant">
<th class="px-lg py-md font-medium">NAMA PATH</th>
<th class="px-lg py-md font-medium">UKURAN</th>
<th class="px-lg py-md font-medium">MODIFIKASI TERAKHIR</th>
<th class="px-lg py-md font-medium">AKSI</th>
</tr>
</thead>
<tbody class="divide-y divide-outline-variant/30">
<tr class="group hover:bg-primary-container/5 transition-colors">
<td class="px-lg py-md">
<div class="flex items-center gap-md">
<div class="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary">
<span class="material-symbols-outlined">folder</span>
</div>
<div class="flex flex-col">
<span class="text-body-md font-bold text-on-surface">C:/Joki Tugas</span>
<span class="text-label-sm text-on-surface-variant">System Local Path</span>
</div>
</div>
</td>
<td class="px-lg py-md text-label-md text-on-surface">12.4 GB</td>
<td class="px-lg py-md text-label-md text-on-surface">12 Jan 2024, 14:30</td>
<td class="px-lg py-md">
<button class="p-sm text-error/60 hover:text-error hover:bg-error/10 rounded-lg transition-all">
<span class="material-symbols-outlined">delete</span>
</button>
</td>
</tr>
</tbody>
</table>
</div>
<!-- Drag & Drop Zone -->
<div class="border-2 border-dashed border-outline/30 rounded-xl p-xl flex flex-col items-center justify-center text-on-surface-variant hover:border-primary/50 hover:bg-primary/5 transition-all group cursor-pointer">
<div class="w-16 h-16 rounded-full bg-surface-container-highest flex items-center justify-center mb-md group-hover:scale-110 transition-transform">
<span class="material-symbols-outlined text-3xl group-hover:text-primary transition-colors">drive_folder_upload</span>
</div>
<p class="text-label-md font-medium text-on-surface">Tarik folder ke sini untuk menambah</p>
<p class="text-label-sm opacity-60">Mendukung multi-direktori sekaligus</p>
</div>
</div>
</div>
<!-- Progress Card -->
<div class="glass-panel p-lg rounded-xl space-y-md border-l-4 border-l-primary relative overflow-hidden">
<div class="flex justify-between items-start">
<div class="space-y-1">
<p class="text-headline-md font-bold text-on-surface">Mempersiapkan Indeks...</p>
<p class="text-body-md text-on-surface-variant">Sistem sedang memetakan struktur file di direktori sumber.</p>
</div>
<span class="text-display-lg text-primary-fixed-dim" id="progress-val">38%</span>
</div>
<!-- Improved Progress Bar -->
<div class="relative pt-1">
<div class="overflow-hidden h-3 text-xs flex rounded-full bg-surface-container-highest">
<div class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center gradient-primary transition-all duration-700 shadow-[0_0_15px_rgba(124,77,255,0.3)]" id="progress-bar" style="width: 38%;"></div>
</div>
</div>
<div class="pt-md">
<button class="w-full gradient-secondary text-on-tertiary font-bold text-label-md py-lg rounded-xl flex items-center justify-center gap-md hover:brightness-105 active:scale-[0.99] transition-all shadow-lg shadow-secondary/10">
<span class="material-symbols-outlined">rocket_launch</span>
                        Mulai Pindai Cerdas
                    </button>
</div>
</div>
</div>
</div>
<!-- Developer Console Terminal -->
<footer class="h-64 bg-surface-container-lowest/90 backdrop-blur-xl border-t border-outline-variant p-md flex flex-col font-mono">
<div class="flex items-center gap-md mb-md border-b border-outline-variant/30 pb-sm">
<span class="material-symbols-outlined text-primary text-sm">terminal</span>
<span class="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">Developer Console v2.4.0</span>
<div class="ml-auto flex gap-sm">
<div class="w-2.5 h-2.5 rounded-full bg-error/40 hover:bg-error transition-colors"></div>
<div class="w-2.5 h-2.5 rounded-full bg-tertiary/40 hover:bg-tertiary transition-colors"></div>
<div class="w-2.5 h-2.5 rounded-full bg-primary/40 hover:bg-primary transition-colors"></div>
</div>
</div>
<div class="flex-1 overflow-y-auto custom-scrollbar space-y-1.5 text-[13px]" id="console-output">
<p class="text-primary opacity-90"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Initializing Smart Organizer Core Engine...</p>
<p class="text-on-surface-variant"><span class="text-on-surface-variant/40 mr-2">[NETWORK]</span> Connecting to neural indexing service...</p>
<p class="text-on-surface-variant"><span class="text-on-surface-variant/40 mr-2">[NETWORK]</span> Service connected at port 8080.</p>
<p class="text-tertiary-fixed-dim"><span class="text-on-surface-variant/40 mr-2">[AUTH]</span> User session validated: Admin_Root</p>
<p class="text-on-surface-variant"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Ready for folder ingestion.</p>
<div class="mt-4 space-y-1 opacity-50">
<p class="text-on-surface-variant">&gt; undo "seblak.webp" back to "C:\Joki Tugas"</p>
<p class="text-on-surface-variant">&gt; undo "ruangan.jpg" back to "C:\Joki Tugas"</p>
<p class="text-on-surface-variant">&gt; undo "pp.jpg" back to "C:\Joki Tugas"</p>
</div>
<p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[DEBUG]</span> Found 1,242 unindexed items in local cache.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[INFO]</span> Checking file permissions for C:/Joki Tugas...</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[INFO]</span> Checking file permissions for C:/Joki Tugas...</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-error/60 mr-2">[WARN]</span> File 'archive.rar' exceeds soft limit size (500MB).</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Background worker ID #429 active and listening.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-error/60 mr-2">[WARN]</span> File 'archive.rar' exceeds soft limit size (500MB).</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[INFO]</span> Checking file permissions for C:/Joki Tugas...</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Background worker ID #429 active and listening.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[DEBUG]</span> Found 1,242 unindexed items in local cache.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-error/60 mr-2">[WARN]</span> File 'archive.rar' exceeds soft limit size (500MB).</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Background worker ID #429 active and listening.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[INFO]</span> Checking file permissions for C:/Joki Tugas...</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[DEBUG]</span> Found 1,242 unindexed items in local cache.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Background worker ID #429 active and listening.</p><p class="text-on-surface-variant/80 transition-opacity duration-1000"><span class="text-on-surface-variant/40 mr-2">[SYSTEM]</span> Background worker ID #429 active and listening.</p></div>
</footer>
</main>
<script>
    // Micro-interaction: Progress bar simulation
    document.addEventListener('DOMContentLoaded', () => {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-val');
        let progress = 12;

        const interval = setInterval(() => {
            if (progress >= 38) {
                clearInterval(interval);
            } else {
                progress += Math.random() * 1.5;
                if(progress > 38) progress = 38;
                progressBar.style.width = progress + '%';
                progressText.innerText = Math.round(progress) + '%';
            }
        }, 800);
    });

    // Console scrolling simulation
    const consoleOutput = document.getElementById('console-output');
    setInterval(() => {
        const logs = [
            "<span class='text-on-surface-variant/40 mr-2'>[INFO]</span> Checking file permissions for C:/Joki Tugas...",
            "<span class='text-on-surface-variant/40 mr-2'>[DEBUG]</span> Found 1,242 unindexed items in local cache.",
            "<span class='text-on-surface-variant/40 mr-2'>[SYSTEM]</span> Background worker ID #429 active and listening.",
            "<span class='text-error/60 mr-2'>[WARN]</span> File 'archive.rar' exceeds soft limit size (500MB)."
        ];
        const p = document.createElement('p');
        p.className = 'text-on-surface-variant/80 transition-opacity duration-1000';
        p.innerHTML = logs[Math.floor(Math.random() * logs.length)];
        consoleOutput.appendChild(p);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
        
        if(consoleOutput.children.length > 40) {
            consoleOutput.removeChild(consoleOutput.children[5]);
        }
    }, 5000);
</script>


</body></html>