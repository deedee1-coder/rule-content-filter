// ---------- Page elements ----------
const ruleCount = document.getElementById("rule-count");
const rulesTableBody = document.getElementById("rules-table-body");
const rulesEmpty = document.getElementById("rules-empty");
const ruleForm = document.getElementById("rule-form");
const keywordInput = document.getElementById("keyword");
const matchTypeSelect = document.getElementById("match-type");
const actionTypeSelect = document.getElementById("action-type");
const colorField = document.getElementById("color-field");
const labelField = document.getElementById("label-field");
const labelInput = document.getElementById("label");
const ruleMessage = document.getElementById("rule-message");

// Readable names for the values stored in the database
const MATCH_TYPE_NAMES = {
    contains: "Contains",
    startsWith: "Starts with",
    exact: "Exact match",
};

const ACTION_TYPE_NAMES = {
    highlight: "Highlight",
    tooltip: "Tooltip",
};

// ---------- Helpers ----------
function showMessage(element, text, type) {
    element.textContent = text;
    element.className = `message message--${type}`;
}

function createCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text; // textContent never runs user text as HTML
    return cell;
}

function createStyleCell(rule) {
    const cell = document.createElement("td");

    if (rule.action_type === "highlight") {
        const swatch = document.createElement("span");
        swatch.className = "swatch";
        swatch.style.backgroundColor = rule.color;
        cell.appendChild(swatch);
    } else {
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = rule.label;
        cell.appendChild(badge);
    }

    return cell;
}

// ---------- Rules list ----------
function renderRules(rules) {
    rulesTableBody.replaceChildren(); // remove old rows

    for (const rule of rules) {
        const row = document.createElement("tr");
        row.appendChild(createCell(rule.keyword));
        row.appendChild(createCell(MATCH_TYPE_NAMES[rule.match_type]));
        row.appendChild(createCell(ACTION_TYPE_NAMES[rule.action_type]));
        row.appendChild(createStyleCell(rule));
        rulesTableBody.appendChild(row);
    }

    rulesEmpty.hidden = rules.length > 0;
    ruleCount.textContent = rules.length === 1 ? "1 rule saved" : `${rules.length} rules saved`;
}

async function loadRules() {
    try {
        const response = await fetch("/api/rules");
        const rules = await response.json();
        renderRules(rules);
    } catch (error) {
        showMessage(ruleMessage, "Could not load rules from the server.", "error");
    }
}

// ---------- New rule form ----------
// Show Color for highlight rules and Label for tooltip rules
function updateActionFields() {
    const isHighlight = actionTypeSelect.value === "highlight";
    colorField.hidden = !isHighlight;
    labelField.hidden = isHighlight;
}

async function saveRule(event) {
    event.preventDefault(); // stop the browser from reloading the page

    const actionType = actionTypeSelect.value;
    const selectedColor = ruleForm.querySelector('input[name="color"]:checked');

    const newRule = {
        keyword: keywordInput.value.trim(),
        match_type: matchTypeSelect.value,
        action_type: actionType,
        color: actionType === "highlight" ? selectedColor.value : null,
        label: actionType === "tooltip" ? labelInput.value.trim() : null,
    };

    try {
        const response = await fetch("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newRule),
        });

        if (!response.ok) {
            showMessage(ruleMessage, "Could not save the rule.", "error");
            return;
        }

        ruleForm.reset();
        updateActionFields();
        showMessage(ruleMessage, `Rule "${newRule.keyword}" saved.`, "success");
        await loadRules();
    } catch (error) {
        showMessage(ruleMessage, "Could not reach the server.", "error");
    }
}

// ---------- Start ----------
actionTypeSelect.addEventListener("change", updateActionFields);
ruleForm.addEventListener("submit", saveRule);

updateActionFields();
loadRules();