async function postForm(url, data) {
  const form = new URLSearchParams();
  for (const [k, v] of Object.entries(data)) form.append(k, v);
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });
  if (!res.ok) throw new Error("Request failed");
  return await res.json();
}

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else e.setAttribute(k, v);
  }
  for (const c of children) e.appendChild(c);
  return e;
}

async function refreshUserSearch() {
  const input = document.querySelector("[data-user-search]");
  const out = document.querySelector("[data-user-search-results]");
  if (!input || !out) return;

  const q = input.value.trim();
  if (!q) {
    out.innerHTML = "";
    return;
  }

  const res = await fetch(`/social/api/users/search?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  out.innerHTML = "";

  for (const u of data.results) {
    const btn = el("button", {
      class: `btn btn-sm ${u.is_friend ? "btn-outline-light" : "btn-accent"}`,
      type: "button",
      text: u.is_friend ? "Уже в друзьях" : "Добавить в друзья",
      "data-username": u.username,
    });
    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      btn.disabled = true;
      try {
        const r = await postForm("/social/api/friends/add", { username: u.username });
        if (r.ok) {
          btn.textContent = "Добавлено";
          btn.className = "btn btn-sm btn-outline-light";
        }
      } catch (e) {
        btn.textContent = "Ошибка";
      } finally {
        setTimeout(() => (btn.disabled = false), 700);
      }
    });

    const row = el("div", { class: "d-flex align-items-center justify-content-between gap-3 p-3 glass rounded-3 mb-2" }, [
      el("div", {}, [
        el("div", { class: "fw-semibold", text: u.username }),
        el("div", { class: "small muted", text: u.email }),
      ]),
      btn,
    ]);
    out.appendChild(row);
  }
}

document.addEventListener("input", (e) => {
  if (e.target && e.target.matches("[data-user-search]")) {
    refreshUserSearch().catch(() => {});
  }
});

