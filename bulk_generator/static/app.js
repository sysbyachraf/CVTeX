/* app.js — CVTeX Bulk Generator frontend logic */

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  mode:    'single',   // 'single' | 'bulk'
  offers:  [],         // bulk mode offer rows
  jobIds:  [],         // list of active job IDs
  stage1JobId: null,   // job currently open in Stage 1 panel
  stage2JobId: null,   // job currently open in Stage 2 modal
  pollInterval: null,
};

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupNav();
  setupModeToggle();
  setupSingleForm();
  setupBulkTable();
  setupCSVUpload();
  setupBulkGenerate();
  setupStage1Panel();
  setupStage2Modal();
  setupBatchActions();
  setupClearAll();
});

// ── Navigation ────────────────────────────────────────────────────────────────
function setupNav() {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.dataset.view;
      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
      btn.classList.add('active');
      $(`view-${view}`).classList.add('active');
      if (view === 'jobs') refreshJobsTable();
    });
  });
}

// ── Mode toggle ───────────────────────────────────────────────────────────────
function setupModeToggle() {
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      state.mode = btn.dataset.mode;
      document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.mode-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $(`panel-${state.mode}`).classList.add('active');
    });
  });
}

// ── Single mode form ──────────────────────────────────────────────────────────
function setupSingleForm() {
  $('form-single').addEventListener('submit', async e => {
    e.preventDefault();
    const offer = {
      company:         $('s-company').value.trim(),
      job_title:       $('s-job-title').value.trim(),
      job_description: $('s-description').value.trim(),
      keywords:        $('s-keywords').value.trim(),
    };
    await submitOffers([offer]);
    // Switch to Jobs view
    $('nav-jobs').click();
  });
}

// ── Bulk table ────────────────────────────────────────────────────────────────
function setupBulkTable() {
  $('btn-add-row').addEventListener('click', () => addOfferRow());
  addOfferRow(); // start with one empty row
}

function addOfferRow(data = {}) {
  const tbody = $('offers-body');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><button class="cell-del" title="Remove row">x</button></td>
    <td><input class="cell-input" type="text" placeholder="Company" value="${esc(data.company || '')}" /></td>
    <td><input class="cell-input" type="text" placeholder="Job Title" value="${esc(data.job_title || '')}" /></td>
    <td><input class="cell-input" type="text" placeholder="Job Description" value="${esc(data.job_description || '')}" /></td>
    <td><input class="cell-input" type="text" placeholder="optional" value="${esc(data.keywords || '')}" /></td>
  `;
  tr.querySelector('.cell-del').addEventListener('click', () => {
    tr.remove();
    updateBulkGenerateBtn();
  });
  tr.querySelectorAll('.cell-input').forEach(inp => inp.addEventListener('input', updateBulkGenerateBtn));
  tbody.appendChild(tr);
  updateBulkGenerateBtn();
}

function updateBulkGenerateBtn() {
  const rows = collectBulkRows();
  $('btn-bulk-generate').disabled = rows.length === 0;
}

function collectBulkRows() {
  const rows = [];
  $('offers-body').querySelectorAll('tr').forEach(tr => {
    const inputs = tr.querySelectorAll('.cell-input');
    if (inputs.length < 4) return;
    const company = inputs[0].value.trim();
    const job_title = inputs[1].value.trim();
    const job_description = inputs[2].value.trim();
    const keywords = inputs[3].value.trim();
    if (company && job_title) {
      rows.push({ company, job_title, job_description, keywords });
    }
  });
  return rows;
}

// ── CSV Upload ────────────────────────────────────────────────────────────────
function setupCSVUpload() {
  const zone = $('upload-zone');
  const fileInput = $('csv-input');

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) uploadCSV(file);
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) uploadCSV(fileInput.files[0]);
  });

  zone.addEventListener('click', () => fileInput.click());
}

async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/upload-csv', { method: 'POST', body: formData });
  const data = await res.json();
  if (data.error) { alert(data.error); return; }

  // Clear existing rows and populate from CSV
  $('offers-body').innerHTML = '';
  data.offers.forEach(o => addOfferRow(o));
  updateBulkGenerateBtn();
}

// ── Bulk generate ─────────────────────────────────────────────────────────────
function setupBulkGenerate() {
  $('btn-bulk-generate').addEventListener('click', async () => {
    const offers = collectBulkRows();
    if (!offers.length) return;
    await submitOffers(offers);
    $('nav-jobs').click();
  });
}

async function submitOffers(offers) {
  const res = await fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ offers }),
  });
  const data = await res.json();
  state.jobIds.push(...data.job_ids);
  updateBadge();
  startPolling();
}

// ── Jobs table ────────────────────────────────────────────────────────────────
async function refreshJobsTable() {
  const res = await fetch('/jobs');
  const jobs = await res.json();
  const tbody = $('jobs-body');

  if (!Object.keys(jobs).length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="4">No applications yet. Generate from the Generate view.</td></tr>';
    return;
  }

  tbody.innerHTML = '';
  for (const [jobId, job] of Object.entries(jobs)) {
    const tr = document.createElement('tr');
    tr.id = `job-row-${jobId}`;
    tr.innerHTML = renderJobRow(jobId, job);
    tbody.appendChild(tr);
    attachRowActions(tr, jobId, job.status);
  }
}

function renderJobRow(jobId, job) {
  const badgeClass = `status-${job.status}`;
  const pages = job.overflow === true ? '<span style="color:#c9a227">2+</span>' : (job.cv_pages > 0 ? job.cv_pages : '—');

  let actions = '';
  if (job.status === 'ready') {
    actions = `<button class="btn-link" data-action="review" data-job="${jobId}">Review</button>`;
  } else if (job.status === 'compiled') {
    actions = `<button class="btn-link" data-action="preview" data-job="${jobId}">Preview PDF</button>`;
  } else if (job.status === 'saved') {
    actions = `<span style="color:var(--text-3);font-size:11px;">Saved to offres/</span>`;
  } else if (job.status === 'error') {
    actions = `<span style="color:var(--danger);font-size:11px;">Error</span>`;
  }

  return `
    <td>${esc(job.company)}</td>
    <td><span class="status-badge ${badgeClass}">${job.status}</span></td>
    <td>${pages}</td>
    <td class="row-actions">${actions}</td>
  `;
}

function attachRowActions(tr, jobId, status) {
  tr.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      if (action === 'review') openStage1(jobId);
      if (action === 'preview') openStage2(jobId);
    });
  });
}

// ── Polling ───────────────────────────────────────────────────────────────────
function startPolling() {
  if (state.pollInterval) return;
  state.pollInterval = setInterval(async () => {
    await refreshJobsTable();
    updateBadge();

    // Stop polling when all jobs are terminal
    const res = await fetch('/jobs');
    const jobs = await res.json();
    const allDone = Object.values(jobs).every(j =>
      ['saved', 'rejected', 'error', 'compiled', 'ready'].includes(j.status)
    );
    if (allDone) { clearInterval(state.pollInterval); state.pollInterval = null; }
  }, 1500);
}

async function updateBadge() {
  const res = await fetch('/jobs');
  const jobs = await res.json();
  const count = Object.keys(jobs).length;
  const badge = $('badge-count');
  if (count > 0) { badge.textContent = count; badge.style.display = ''; }
  else badge.style.display = 'none';
}

// ── Stage 1 Panel ─────────────────────────────────────────────────────────────
function setupStage1Panel() {
  $('s1-close').addEventListener('click', closeStage1);
  $('s1-overlay').addEventListener('click', closeStage1);

  $('s1-reject').addEventListener('click', async () => {
    await fetch(`/stage1/reject/${state.stage1JobId}`, { method: 'POST' });
    closeStage1();
    refreshJobsTable();
  });

  $('s1-regenerate').addEventListener('click', async () => {
    await fetch(`/stage1/regenerate/${state.stage1JobId}`, { method: 'POST' });
    closeStage1();
    startPolling();
    refreshJobsTable();
  });

  $('s1-approve').addEventListener('click', async () => {
    const profil = $('s1-profil').value;
    const lettre = $('s1-lettre').value;
    const selectedProjects = [...$('s1-projects').querySelectorAll('input:checked')].map(c => c.value);
    const selectedCertifs  = [...$('s1-certifs').querySelectorAll('input:checked')].map(c => c.value);

    await fetch(`/stage1/approve/${state.stage1JobId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profil, lettre, selected_projects: selectedProjects, selected_certifs: selectedCertifs }),
    });
    closeStage1();
    startPolling();
    refreshJobsTable();
  });
}

async function openStage1(jobId) {
  const res  = await fetch(`/stage1/${jobId}`);
  const data = await res.json();
  if (data.error) { alert(data.error); return; }

  state.stage1JobId = jobId;
  $('s1-title').textContent   = data.company;
  $('s1-subtitle').textContent = data.job_title;
  $('s1-profil').value = data.profil;
  $('s1-lettre').value = data.lettre;

  // Projects checkboxes
  $('s1-projects').innerHTML = data.projects.map(p => `
    <label class="checkbox-item">
      <input type="checkbox" value="${esc(p.title)}" ${p.selected ? 'checked' : ''} />
      <label>${esc(p.title)}</label>
    </label>
  `).join('');

  // Certifs checkboxes
  $('s1-certifs').innerHTML = data.certifs.map(c => `
    <label class="checkbox-item">
      <input type="checkbox" value="${esc(c.title)}" ${c.selected ? 'checked' : ''} />
      <label>${esc(c.title)}</label>
    </label>
  `).join('');

  $('s1-overlay').hidden = false;
  $('side-panel').hidden = false;
}

function closeStage1() {
  $('s1-overlay').hidden = true;
  $('side-panel').hidden = true;
  state.stage1JobId = null;
}

// ── Stage 2 Modal ─────────────────────────────────────────────────────────────
function setupStage2Modal() {
  $('s2-overlay')?.addEventListener('click', (e) => {
    if (e.target.id === 's2-overlay') closeStage2();
  });
  $('s2-close')?.addEventListener('click', closeStage2);
  $('s2-close-btn')?.addEventListener('click', closeStage2);
  $('s2-save')?.addEventListener('click', async () => {
    const jobId = state.stage2JobId;
    if (!jobId) return;
    await fetch(`/stage2/save/${jobId}`, { method: 'POST' });
    closeStage2();
    refreshJobsTable();
  });
}

async function openStage2(jobId) {
  const res  = await fetch(`/stage2/${jobId}`);
  const data = await res.json();
  if (data.error) { alert(data.error); return; }

  state.stage2JobId = jobId;
  $('s2-title').textContent = data.company;
  $('s2-overflow').hidden = !data.overflow;
  $('s2-cv-frame').src    = data.cv_url;
  $('s2-lettre-frame').src = data.lettre_url;
  $('s2-overlay').hidden = false;
}

function closeStage2() {
  $('s2-overlay').hidden = true;
  $('s2-cv-frame').src = 'about:blank';
  $('s2-lettre-frame').src = 'about:blank';
  state.stage2JobId = null;
}

// ── Batch actions ─────────────────────────────────────────────────────────────
function setupBatchActions() {
  $('btn-save-all').addEventListener('click', async () => {
    await fetch('/stage2/save-all', { method: 'POST' });
    refreshJobsTable();
  });

  $('btn-approve-all').addEventListener('click', async () => {
    const res  = await fetch('/jobs');
    const jobs = await res.json();
    for (const [jobId, job] of Object.entries(jobs)) {
      if (job.status === 'ready') {
        await fetch(`/stage1/approve/${jobId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ profil: '', lettre: '', selected_projects: [], selected_certifs: [] }),
        });
      }
    }
    startPolling();
    refreshJobsTable();
  });
}

// ── Clear all ─────────────────────────────────────────────────────────────────
function setupClearAll() {
  $('btn-clear-all').addEventListener('click', async () => {
    if (!confirm('Clear all job state?')) return;
    await fetch('/jobs/clear', { method: 'POST' });
    state.jobIds = [];
    updateBadge();
    refreshJobsTable();
  });
}

// ── Utils ──────────────────────────────────────────────────────────────────────
function esc(str) {
  return String(str ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
