/**
 * form_dynamic.js
 * Handles dynamic add/remove of child (മക്കൾ) and sister (സഹോദരിമാർ)
 * entries in the Pakkada family data collection form.
 *
 * Name conventions used in form POST data:
 *   child_relation[]  child_name[]  child_mobile[]  child_wife_name[]
 *   child_above5[]    child_below5[]
 *
 *   sister_name[]  sister_mobile[]  sister_above5[]  sister_below5[]
 */

(function () {
    'use strict';

    /* ─── State counters ─────────────────────────────────── */
    let childCount = 0;
    let sisterCount = 0;

    /* ─── Helpers ────────────────────────────────────────── */

    /**
     * Update the visibility of "empty" hint messages.
     * @param {string} containerId  - id of the container div
     * @param {string} emptyMsgId  - id of the empty message paragraph
     */
    function updateEmptyMessage(containerId, emptyMsgId) {
        const container = document.getElementById(containerId);
        const msg = document.getElementById(emptyMsgId);
        if (!container || !msg) return;
        msg.style.display = container.children.length === 0 ? '' : 'none';
    }

    /**
     * Re-number item labels after removal so they stay sequential.
     * @param {string} containerId
     * @param {string} labelPrefix  - e.g. "മകൻ/മകൾ" or "സഹോദരി"
     */
    function renumberItems(containerId, labelPrefix) {
        const container = document.getElementById(containerId);
        if (!container) return;
        const items = container.querySelectorAll('.dynamic-item');
        items.forEach(function (item, idx) {
            const label = item.querySelector('.item-number');
            if (label) {
                label.textContent = labelPrefix + ' ' + (idx + 1);
            }
        });
    }

    /* ─── CHILDREN (മക്കൾ) ───────────────────────────────── */

    /**
     * Build and insert a child entry card.
     */
    function addChild() {
        childCount += 1;
        const container = document.getElementById('childrenContainer');

        const wrapper = document.createElement('div');
        wrapper.className = 'dynamic-item';
        wrapper.dataset.index = childCount;

        wrapper.innerHTML = `
            <div class="d-flex align-items-center justify-content-between mb-3">
                <span class="item-number">മകൻ / മകൾ ${childCount}</span>
                <button type="button" class="btn-remove" aria-label="Remove entry">
                    <i class="bi bi-trash3 me-1"></i>നീക്കം
                </button>
            </div>
            <div class="row g-3">

                <!-- ബന്ധം -->
                <div class="col-md-3">
                    <label class="form-label">ബന്ധം</label>
                    <select class="form-select child-relation-select" name="child_relation">
                        <option value="">- തിരഞ്ഞെടുക്കുക -</option>
                        <option value="മകൻ">മകൻ</option>
                        <option value="മകൾ">മകൾ</option>
                    </select>
                </div>

                <!-- പേര് -->
                <div class="col-md-4">
                    <label class="form-label">പേര്</label>
                    <input type="text" class="form-control" name="child_name"
                           placeholder="മക്കളുടെ പേര്">
                </div>

                <!-- മൊബൈൽ -->
                <div class="col-md-3">
                    <label class="form-label">മൊബൈൽ നമ്പർ</label>
                    <input type="tel" class="form-control" name="child_mobile"
                           placeholder="Mobile Number" maxlength="15" inputmode="numeric">
                </div>

                <!-- ഭാര്യ (shown only for മകൻ) -->
                <div class="col-md-4 child-wife-field" style="display:none;">
                    <label class="form-label">ഭാര്യയുടെ പേര്</label>
                    <input type="text" class="form-control child-wife-input"
                           name="child_wife_name" placeholder="ഭാര്യ">
                </div>

                <!-- കുട്ടികൾ counts -->
                <div class="col-md-4">
                    <label class="form-label">കുട്ടികൾ – 5 വയസിനു മുകളിൽ</label>
                    <input type="number" class="form-control" name="child_above5"
                           value="0" min="0">
                </div>
                <div class="col-md-4">
                    <label class="form-label">കുട്ടികൾ – 5 വയസിനു താഴെ</label>
                    <input type="number" class="form-control" name="child_below5"
                           value="0" min="0">
                </div>

            </div>
        `;

        container.appendChild(wrapper);
        updateEmptyMessage('childrenContainer', 'childEmptyMsg');

        /* Wire up ബന്ധം → show/hide ഭാര്യ */
        const select = wrapper.querySelector('.child-relation-select');
        const wifeField = wrapper.querySelector('.child-wife-field');
        const wifeInput = wrapper.querySelector('.child-wife-input');

        select.addEventListener('change', function () {
            if (this.value === 'മകൻ') {
                wifeField.style.display = '';
                wifeInput.disabled = false;
            } else {
                wifeField.style.display = 'none';
                wifeInput.disabled = true;
                wifeInput.value = '';
            }
        });

        /* Wire up remove button */
        const removeBtn = wrapper.querySelector('.btn-remove');
        removeBtn.addEventListener('click', function () {
            wrapper.remove();
            renumberItems('childrenContainer', 'മകൻ / മകൾ');
            updateEmptyMessage('childrenContainer', 'childEmptyMsg');
        });
    }

    /* ─── SISTERS (സഹോദരിമാർ) ──────────────────────────── */

    /**
     * Build and insert a sister entry card.
     */
    function addSister() {
        sisterCount += 1;
        const container = document.getElementById('sistersContainer');

        const wrapper = document.createElement('div');
        wrapper.className = 'dynamic-item';
        wrapper.dataset.index = sisterCount;

        wrapper.innerHTML = `
            <div class="d-flex align-items-center justify-content-between mb-3">
                <span class="item-number">സഹോദരി ${sisterCount}</span>
                <button type="button" class="btn-remove" aria-label="Remove entry">
                    <i class="bi bi-trash3 me-1"></i>നീക്കം
                </button>
            </div>
            <div class="row g-3">

                <!-- സഹോദരിയുടെ പേര് -->
                <div class="col-md-5">
                    <label class="form-label">സഹോദരിയുടെ പേര്</label>
                    <input type="text" class="form-control" name="sister_name"
                           placeholder="സഹോദരി">
                </div>

                <!-- മൊബൈൽ -->
                <div class="col-md-4">
                    <label class="form-label">മൊബൈൽ നമ്പർ</label>
                    <input type="tel" class="form-control" name="sister_mobile"
                           placeholder="10 അക്കം" maxlength="15" inputmode="numeric">
                </div>

                <!-- കുട്ടികൾ counts -->
                <div class="col-md-3 col-lg-4">
                    <label class="form-label">കുട്ടികൾ – 5 വയസിനു മുകളിൽ</label>
                    <input type="number" class="form-control" name="sister_above5"
                           value="0" min="0">
                </div>
                <div class="col-md-3 col-lg-4">
                    <label class="form-label">കുട്ടികൾ – 5 വയസിനു താഴെ</label>
                    <input type="number" class="form-control" name="sister_below5"
                           value="0" min="0">
                </div>

            </div>
        `;

        container.appendChild(wrapper);
        updateEmptyMessage('sistersContainer', 'sisterEmptyMsg');

        /* Wire up remove button */
        const removeBtn = wrapper.querySelector('.btn-remove');
        removeBtn.addEventListener('click', function () {
            wrapper.remove();
            renumberItems('sistersContainer', 'സഹോദരി');
            updateEmptyMessage('sistersContainer', 'sisterEmptyMsg');
        });
    }

    /* ─── Boot ───────────────────────────────────────────── */

    document.addEventListener('DOMContentLoaded', function () {
        /* Initial empty message state */
        updateEmptyMessage('childrenContainer', 'childEmptyMsg');
        updateEmptyMessage('sistersContainer', 'sisterEmptyMsg');

        /* Button listeners */
        const addChildBtn = document.getElementById('addChildBtn');
        if (addChildBtn) {
            addChildBtn.addEventListener('click', addChild);
        }

        const addSisterBtn = document.getElementById('addSisterBtn');
        if (addSisterBtn) {
            addSisterBtn.addEventListener('click', addSister);
        }

        /* Basic client-side validation on submit */
        const form = document.getElementById('familyForm');
        if (form) {
            form.addEventListener('submit', function (e) {
                // Disable all hidden wife inputs before submit so they
                // are excluded from POST data entirely.
                form.querySelectorAll('.child-wife-field').forEach(function (field) {
                    if (field.style.display === 'none') {
                        const input = field.querySelector('input');
                        if (input) input.disabled = true;
                    }
                });
            });
        }

        /* ── Pre-fill for edit mode ────────────────────────────────────────── */
        const prefillEl = document.getElementById('prefillData');
        if (prefillEl) {
            const prefill = JSON.parse(prefillEl.textContent);

            (prefill.children || []).forEach(function (child) {
                addChild();
                const items = document.querySelectorAll('#childrenContainer .dynamic-item');
                const item = items[items.length - 1];

                const selectEl = item.querySelector('.child-relation-select');
                const nameEl = item.querySelector('[name="child_name"]');
                const mobEl = item.querySelector('[name="child_mobile"]');
                const wifeEl = item.querySelector('.child-wife-input');
                const wifeFld = item.querySelector('.child-wife-field');
                const above5El = item.querySelector('[name="child_above5"]');
                const below5El = item.querySelector('[name="child_below5"]');

                if (selectEl) {
                    selectEl.value = child['\u0d2c\u0d28\u0d4d\u0d27\u0d02'] || '';
                    selectEl.dispatchEvent(new Event('change'));
                }
                if (nameEl) nameEl.value = child['\u0d2a\u0d47\u0d30\u0d4d'] || '';
                if (mobEl) mobEl.value = child['\u0d2e\u0d4a\u0d2c\u0d48\u0d7d \u0d28\u0d2e\u0d4d\u0d2a\u0d7c'] || '';
                if (wifeEl) wifeEl.value = child['\u0d2d\u0d3e\u0d30\u0d4d\u0d2f\u0d2f\u0d41\u0d1f\u0d46 \u0d2a\u0d47\u0d30\u0d4d'] || '';
                const kids = child['\u0d15\u0d41\u0d1f\u0d4d\u0d1f\u0d3f\u0d15\u0d7e'] || {};
                if (above5El) above5El.value = kids['5 \u0d35\u0d2f\u0d38\u0d3f\u0d28\u0d41 \u0d2e\u0d41\u0d15\u0d33\u0d3f\u0d7d'] ?? 0;
                if (below5El) below5El.value = kids['5 \u0d35\u0d2f\u0d38\u0d3f\u0d28\u0d41 \u0d24\u0d3e\u0d34\u0d46'] ?? 0;
            });

            (prefill.sisters || []).forEach(function (sister) {
                addSister();
                const items = document.querySelectorAll('#sistersContainer .dynamic-item');
                const item = items[items.length - 1];

                const nameEl = item.querySelector('[name="sister_name"]');
                const mobEl = item.querySelector('[name="sister_mobile"]');
                const above5El = item.querySelector('[name="sister_above5"]');
                const below5El = item.querySelector('[name="sister_below5"]');

                if (nameEl) nameEl.value = sister['\u0d38\u0d39\u0d4b\u0d26\u0d30\u0d3f\u0d2f\u0d41\u0d1f\u0d46 \u0d2a\u0d47\u0d30\u0d4d'] || '';
                if (mobEl) mobEl.value = sister['\u0d2e\u0d4a\u0d2c\u0d48\u0d7d \u0d28\u0d2e\u0d4d\u0d2a\u0d7c'] || '';
                const kids = sister['\u0d15\u0d41\u0d1f\u0d4d\u0d1f\u0d3f\u0d15\u0d7e'] || {};
                if (above5El) above5El.value = kids['5 \u0d35\u0d2f\u0d38\u0d3f\u0d28\u0d41 \u0d2e\u0d41\u0d15\u0d33\u0d3f\u0d7d'] ?? 0;
                if (below5El) below5El.value = kids['5 \u0d35\u0d2f\u0d38\u0d3f\u0d28\u0d41 \u0d24\u0d3e\u0d34\u0d46'] ?? 0;
            });
        }
    });

})();
