// ---------- Page elements ----------
const ruleCount = document.getElementById("rule-count");
const rulesTableBody = document.getElementById("rules-table-body");
const rulesEmpty = document.getElementById("rules-empty");
const rulesMessage = document.getElementById("rules-message");
const ruleForm = document.getElementById("rule-form");
const keywordInput = document.getElementById("keyword");
const matchTypeSelect = document.getElementById("match-type");
const actionTypeSelect = document.getElementById("action-type");
const colorField = document.getElementById("color-field");
const labelField = document.getElementById("label-field");
const labelInput = document.getElementById("label");
const ruleMessage = document.getElementById("rule-message");
const inputText = document.getElementById("input-text");
const charCount = document.getElementById("char-count");
const processButton = document.getElementById("process-button");
const processMessage = document.getElementById("process-message");
const resultOutput = document.getElementById("result-output");
const summaryBox = document.getElementById("summary");

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

// A color dot for highlight rules, or a label badge for tooltip rules
function createRuleStyle(rule) {
    if (rule.action_type === "highlight") {
        const swatch = document.createElement("span");
        swatch.className = "swatch";
        swatch.style.backgroundColor = rule.color;
        return swatch;
    }

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = rule.label;
    return badge;
}

function createStyleCell(rule) {
    const cell = document.createElement("td");
    cell.appendChild(createRuleStyle(rule));
    return cell;
}

// Read the error message sent by the backend, e.g. {"error": "Keyword is required."}
async function getErrorMessage(response, fallback) {
    try {
        const data = await response.json();
        return data.error || fallback;
    } catch (error) {
        return fallback; // the response was not JSON
    }
}

function createDeleteCell(rule) {
    const cell = document.createElement("td");
    cell.className = "cell-actions";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "button-link";
    button.textContent = "Delete";
    button.setAttribute("aria-label", `Delete rule ${rule.keyword}`);
    button.addEventListener("click", () => deleteRule(rule));

    cell.appendChild(button);
    return cell;
}

function plural(count, word) {
    return `${count} ${word}${count === 1 ? "" : "s"}`;
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
        row.appendChild(createDeleteCell(rule));
        rulesTableBody.appendChild(row);
    }

    rulesEmpty.hidden = rules.length > 0;
    ruleCount.textContent = rules.length === 1 ? "1 rule saved" : `${rules.length} rules saved`;
}

async function loadRules() {
    try {
        const response = await fetch("/api/rules");
        if (!response.ok) {
            showMessage(rulesMessage, "Could not load rules from the server.", "error");
            return;
        }
        const rules = await response.json();
        renderRules(rules);
    } catch (error) {
        showMessage(rulesMessage, "Could not load rules from the server.", "error");
    }
}

async function deleteRule(rule) {
    if (!confirm(`Delete the rule "${rule.keyword}"?`)) {
        return; // the user clicked Cancel
    }

    try {
        const response = await fetch(`/api/rules/${rule.id}`, { method: "DELETE" });

        if (!response.ok) {
            showMessage(rulesMessage, await getErrorMessage(response, "Could not delete the rule."), "error");
            return;
        }

        showMessage(rulesMessage, `Rule "${rule.keyword}" deleted.`, "success");
        await loadRules();
    } catch (error) {
        showMessage(rulesMessage, "Could not reach the server.", "error");
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

    // Quick checks in the browser; the backend checks everything again
    if (!newRule.keyword) {
        showMessage(ruleMessage, "Keyword is required.", "error");
        keywordInput.focus();
        return;
    }
    if (/\s/.test(newRule.keyword)) {
        showMessage(ruleMessage, "Keyword must be a single word.", "error");
        keywordInput.focus();
        return;
    }
    if (actionType === "tooltip" && !newRule.label) {
        showMessage(ruleMessage, "Label is required for tooltip rules.", "error");
        labelInput.focus();
        return;
    }

    try {
        const response = await fetch("/api/rules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newRule),
        });

        if (!response.ok) {
            showMessage(ruleMessage, await getErrorMessage(response, "Could not save the rule."), "error");
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

// ---------- Processed result ----------
function describeRule(rule) {
    const action = rule.action_type === "highlight" ? "highlight" : `label ${rule.label}`;
    return `${MATCH_TYPE_NAMES[rule.match_type]} "${rule.keyword}": ${action}`;
}

function createMatchedWord(piece) {
    const wrapper = document.createElement("span");
    wrapper.className = "match";

    const word = document.createElement("span");
    word.textContent = piece.text;
    wrapper.appendChild(word);

    // Rules arrive oldest first, so the first highlight rule found decides the color
    const highlightRule = piece.rules.find((rule) => rule.action_type === "highlight");
    if (highlightRule) {
        word.className = "match-highlight";
        word.style.backgroundColor = highlightRule.color;
    } else {
        word.className = "match-underline";
    }

    // Every matching tooltip rule adds its label after the word
    for (const rule of piece.rules) {
        if (rule.action_type === "tooltip") {
            const badge = createRuleStyle(rule);
            badge.classList.add("match-tag");
            wrapper.appendChild(badge);
        }
    }

    // Hovering the word lists every rule that matched it
    wrapper.title = "Matched rules:\n" + piece.rules.map(describeRule).join("\n");

    return wrapper;
}

function renderResult(pieces) {
    const container = document.createElement("div");
    container.className = "result-text";

    for (const piece of pieces) {
        if (piece.rules.length === 0) {
            container.appendChild(document.createTextNode(piece.text)); // plain text, never HTML
        } else {
            container.appendChild(createMatchedWord(piece));
        }
    }

    resultOutput.replaceChildren(container);
}

function renderSummary(summary) {
    summaryBox.replaceChildren();
    summaryBox.hidden = false;

    const heading = document.createElement("p");
    heading.className = "summary-heading";
    summaryBox.appendChild(heading);

    if (summary.rules_checked === 0) {
        heading.textContent = "No saved rules to apply. Create a rule first.";
        return;
    }

    if (summary.matched_words === 0) {
        heading.textContent = "No rules matched this text.";
        return;
    }

    heading.textContent =
        `${plural(summary.matched_words, "word")} matched by ` +
        `${summary.rules_matched} of ${plural(summary.rules_checked, "rule")}.`;

    const list = document.createElement("ul");
    list.className = "summary-list";

    for (const item of summary.rule_counts) {
        const listItem = document.createElement("li");
        if (item.count === 0) {
            listItem.className = "is-unmatched";
        }

        const name = document.createElement("span");
        name.textContent = `${item.rule.keyword} (${MATCH_TYPE_NAMES[item.rule.match_type]})`;

        const count = document.createElement("span");
        count.className = "summary-count";
        count.textContent = item.count;

        listItem.append(name, createRuleStyle(item.rule), count);
        list.appendChild(listItem);
    }

    summaryBox.appendChild(list);
}

function updateCharCount() {
    charCount.textContent = `${inputText.value.length} / ${inputText.maxLength}`;
}

async function processText() {
    processMessage.textContent = "";

    if (!inputText.value.trim()) {
        showMessage(processMessage, "Please enter some text to process.", "error");
        inputText.focus();
        return;
    }

    processButton.disabled = true; // prevent double clicks while waiting

    try {
        const response = await fetch("/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: inputText.value }),
        });

        if (!response.ok) {
            showMessage(processMessage, await getErrorMessage(response, "Could not process the text."), "error");
            return;
        }

        const data = await response.json();
        renderResult(data.pieces);
        renderSummary(data.summary);
    } catch (error) {
        showMessage(processMessage, "Could not reach the server.", "error");
    } finally {
        processButton.disabled = false;
    }
}

// ---------- Start ----------
actionTypeSelect.addEventListener("change", updateActionFields);
ruleForm.addEventListener("submit", saveRule);
processButton.addEventListener("click", processText);
inputText.addEventListener("input", updateCharCount);

updateActionFields();
updateCharCount();
loadRules();