const loginShellEl = document.querySelector("#login-shell");
const appShellEl = document.querySelector("#app-shell");
const loginFormEl = document.querySelector("#login-form");
const loginErrorEl = document.querySelector("#login-error");
const usernameEl = document.querySelector("#username");
const passwordEl = document.querySelector("#password");
const customerActionsEl = document.querySelector("#customer-actions");
const customerNameEl = document.querySelector("#customer-name");
const logoutButtonEl = document.querySelector("#logout-button");
const greetingEl = document.querySelector("#greeting");
const accountsEl = document.querySelector("#accounts");
const transactionsEl = document.querySelector("#transactions");
const chatEl = document.querySelector("#chat");
const formEl = document.querySelector("#chat-form");
const inputEl = document.querySelector("#message");
const traceEl = document.querySelector("#trace");

const money = new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" });

async function getJson(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 204) return null;

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.detail || `Request failed: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}

function showLogin() {
  loginShellEl.classList.remove("hidden");
  appShellEl.classList.add("hidden");
  customerActionsEl.classList.add("hidden");
  accountsEl.innerHTML = "";
  transactionsEl.innerHTML = "";
  traceEl.textContent = "Run a request to see the deterministic steps.";
}

function showApp(customer) {
  loginShellEl.classList.add("hidden");
  appShellEl.classList.remove("hidden");
  customerActionsEl.classList.remove("hidden");
  customerNameEl.textContent = customer.display_name;
  greetingEl.textContent = `Hello, ${customer.display_name.split(" ")[0]}`;
}

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  chatEl.appendChild(row);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function renderTrace(steps) {
  traceEl.innerHTML = "";
  steps.forEach((step) => {
    const el = document.createElement("div");
    el.className = "trace-step";
    el.innerHTML = `<strong>${step.step}</strong><div>${step.detail}</div>`;
    traceEl.appendChild(el);
  });
}

async function loadDashboard() {
  const [accounts, transactions] = await Promise.all([
    getJson("/api/accounts"),
    getJson("/api/transactions?limit=6"),
  ]);

  accountsEl.innerHTML = accounts.map((account) => `
    <article class="account-card">
      <div class="account-name">${account.name}</div>
      <div class="account-balance">${money.format(Number(account.balance))}</div>
      <div class="account-type">${account.type} · ${account.currency}</div>
    </article>
  `).join("");

  transactionsEl.innerHTML = transactions.map((txn) => {
    const sign = txn.direction === "credit" ? "+" : "−";
    return `
      <div class="transaction-row">
        <div>
          <div class="txn-merchant">${txn.merchant}</div>
          <div class="txn-meta">${txn.date} · ${txn.category}</div>
        </div>
        <div class="txn-amount">${sign}${money.format(Number(txn.amount))}</div>
      </div>
    `;
  }).join("");
}

loginFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginErrorEl.textContent = "";

  try {
    const customer = await getJson("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: usernameEl.value.trim(),
        password: passwordEl.value,
      }),
    });
    passwordEl.value = "";
    showApp(customer);
    await loadDashboard();
  } catch (error) {
    loginErrorEl.textContent = error.message;
  }
});

logoutButtonEl.addEventListener("click", async () => {
  await getJson("/api/auth/logout", { method: "POST" }).catch(() => null);
  showLogin();
  usernameEl.focus();
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage("user", message);
  inputEl.value = "";
  inputEl.disabled = true;

  try {
    const payload = await getJson("/api/assistant/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    addMessage("assistant", payload.answer);
    renderTrace(payload.execution_steps);
  } catch (error) {
    if (error.status === 401) {
      showLogin();
      addMessage("assistant", "Your session has ended. Please log in again.");
    } else {
      addMessage("assistant", "Something went wrong while running the workflow.");
      traceEl.textContent = error.message;
    }
  } finally {
    inputEl.disabled = false;
    inputEl.focus();
  }
});

async function initialise() {
  try {
    const customer = await getJson("/api/auth/session");
    showApp(customer);
    await loadDashboard();
  } catch (error) {
    showLogin();
    usernameEl.focus();
  }
}

initialise();
