(function () {
  const pageKey = document.body.dataset.page;
  const page = window.KNUS_PAGES[pageKey];
  if (!page) return;
  document.documentElement.classList.add("js");

  const TRACK_LABEL = { np: "Научно-педагогическая", prof: "Профильная" };
  const TRACK_SHORT = { np: "нп", prof: "проф" };

  const icon = (name, size = 18) => {
    const paths = {
      clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
      credits: '<path d="M4 19V5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2Z"/><path d="M8 7h6M8 11h6"/>',
      format: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
      lang: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
      check: '<path d="m5 12 5 5L20 7"/>',
      topics: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.6.6 1 1.4 1 2.5h6c0-1.1.4-1.9 1-2.5A6 6 0 0 0 12 3Z"/>',
      guide: '<path d="M4 4h10l6 6v10H4z"/><path d="M14 4v6h6M8 14h8M8 17h5"/>',
      plan: '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4M16 3v4M4 10h16M8 14h3M8 17h6"/>',
      mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
      field: '<path d="M3 21h18M5 21V10l7-5 7 5v11M9 21v-6h6v6"/>',
      research: '<circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5"/>',
      teach: '<path d="M2 9 12 4l10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
      lab: '<path d="M9 3h6M10 3v6L4 19a1 1 0 0 0 .9 1.5h14.2A1 1 0 0 0 20 19l-6-10V3"/>',
    };
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]}</svg>`;
  };

  const $ = (sel) => document.querySelector(sel);
  const programId = (p) => `program-${p.code}`;

  /* ---------- Resources ---------- */

  const resources = $("#resources-grid");
  if (resources) {
    resources.innerHTML = page.resources
      .map(
        (r) => `
        <a class="resource reveal" href="${r.href}">
          <span class="resource__icon">${icon(r.icon, 22)}</span>
          <span class="resource__title">${r.title}</span>
          <span class="resource__text">${r.text}</span>
          <span class="resource__arrow">Открыть →</span>
        </a>`
      )
      .join("");
  }

  /* ---------- Program cards ---------- */

  const facts = (p) => {
    const items = [
      ["clock", "Срок", p.duration],
      ["credits", "ECTS", p.ects],
      p.format ? ["format", "Формат", p.format] : ["field", "Группа", p.group.split(" ")[0]],
      ["lang", "Язык", p.languages.replace("Казахский", "Каз").replace("русский", "рус").replace("английский", "англ")],
    ];
    return items
      .map(([ic, label, value]) => `<span class="fact">${icon(ic, 16)}<span>${label}: <b>${value}</b></span></span>`)
      .join("");
  };

  const grid = $("#programs-grid");
  if (grid) {
    grid.classList.toggle("programs--wide", page.programs.length < 3);
    grid.innerHTML = page.programs
      .map(
        (p, i) => `
        <article class="program reveal" data-track="${p.track}" id="${programId(p)}" aria-labelledby="${programId(p)}-title">
          <div class="program__media">
            <img src="${p.image}" alt="" loading="${i < 3 ? "eager" : "lazy"}" />
            <div class="program__tags">
              <span class="tag">${p.code}</span>
              ${pageKey === "masters" ? `<span class="tag tag--${p.track}">${TRACK_LABEL[p.track]}</span>` : `<span class="tag tag--np">PhD</span>`}
            </div>
          </div>
          <div class="program__body">
            <h3 class="program__title" id="${programId(p)}-title">${p.title}</h3>
            ${p.subtitle ? `<p class="program__subtitle">${p.subtitle}</p>` : ""}
            <p class="program__goal">${p.goal}</p>
            <div class="facts">${facts(p)}</div>
          </div>
          <div class="program__actions">
            <button class="btn btn--primary btn--sm" type="button" data-open="${p.code}">Подробнее о программе</button>
          </div>
        </article>`
      )
      .join("");
  }

  /* ---------- Filters ---------- */

  const filters = $("#filters");
  if (filters && page.filters) {
    const count = (id) => (id === "all" ? page.programs.length : page.programs.filter((p) => p.track === id).length);
    filters.innerHTML = page.filters
      .map(
        (f, i) =>
          `<button class="chip" type="button" data-filter="${f.id}" aria-pressed="${i === 0}">${f.label}<span class="chip__count">${count(f.id)}</span></button>`
      )
      .join("");
    filters.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-filter]");
      if (!btn) return;
      applyFilter(btn.dataset.filter);
    });
  }

  function applyFilter(id) {
    if (!filters) return;
    filters.querySelectorAll("[data-filter]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.filter === id)));
    grid.querySelectorAll(".program").forEach((card) => {
      card.hidden = id !== "all" && card.dataset.track !== id;
    });
  }

  document.querySelectorAll("[data-apply-filter]").forEach((el) =>
    el.addEventListener("click", () => applyFilter(el.dataset.applyFilter))
  );

  /* ---------- Tracks (masters) ---------- */

  const tracks = $("#tracks-grid");
  if (tracks && page.tracks) {
    tracks.innerHTML = Object.entries(page.tracks)
      .map(
        ([id, t]) => `
        <article class="track track--${id} reveal">
          <span class="track__badge">${t.badge}</span>
          <h3 class="track__title">${t.title}</h3>
          <p class="track__text">${t.text}</p>
          <ul class="track__points">${t.points.map((pt) => `<li>${icon("check")}${pt}</li>`).join("")}</ul>
          <a class="btn btn--light btn--sm" href="#programs" data-apply-filter="${id}">Смотреть программы (${page.programs.filter((p) => p.track === id).length})</a>
        </article>`
      )
      .join("");
    tracks.querySelectorAll("[data-apply-filter]").forEach((el) =>
      el.addEventListener("click", () => applyFilter(el.dataset.applyFilter))
    );
  }

  /* ---------- Journey & pillars (phd) ---------- */

  const journey = $("#journey-list");
  if (journey && page.journey) {
    journey.innerHTML = page.journey.map((s) => `<li class="reveal"><h3>${s.title}</h3><p>${s.text}</p></li>`).join("");
  }

  const pillars = $("#pillars");
  if (pillars && page.sharedPractice) {
    const icons = ["research", "teach", "lab"];
    pillars.innerHTML = page.sharedPractice
      .map(
        (s, i) => `
        <article class="pillar reveal">
          <span class="resource__icon">${icon(icons[i], 22)}</span>
          <h3>${s.title}</h3>
          <p>${s.text}</p>
        </article>`
      )
      .join("");
  }

  /* ---------- Compare table ---------- */

  const compareBody = $("#compare-body");
  if (compareBody) {
    compareBody.innerHTML = page.programs
      .map((p) => {
        const middle =
          pageKey === "masters"
            ? `<td><span class="tag tag--${p.track}">${TRACK_LABEL[p.track]}</span></td><td class="nowrap">${p.duration}</td><td class="nowrap">${p.ects}</td><td>${p.format}</td>`
            : `<td>${p.group}</td><td class="nowrap">${p.duration}</td><td class="nowrap">${p.ects}</td>`;
        return `
        <tr>
          <th scope="row"><span class="compare__name">${p.title}</span><span class="compare__code">${p.code}</span></th>
          ${middle}
          <td>${p.languages}</td>
          <td><button class="link-btn" type="button" data-open="${p.code}">Подробнее</button></td>
        </tr>`;
      })
      .join("");
  }

  /* ---------- Faculty ---------- */

  const faculty = $("#faculty-grid");
  if (faculty && page.faculty) {
    const initials = (name) =>
      name
        .split(" ")
        .slice(0, 2)
        .map((w) => w[0])
        .join("");
    faculty.innerHTML = page.faculty
      .map(
        (f) => `
        <article class="person reveal">
          <div class="person__photo">
            ${f.photo ? `<img src="${f.photo}" alt="${f.name}" loading="lazy" />` : `<div class="person__initials" aria-hidden="true">${initials(f.name)}</div>`}
          </div>
          <div class="person__body">
            <h3 class="person__name">${f.name}</h3>
            ${f.role ? `<p class="person__role">${f.role}</p>` : ""}
          </div>
        </article>`
      )
      .join("");
  }

  /* ---------- FAQ ---------- */

  const faq = $("#faq-list");
  if (faq) {
    faq.innerHTML = page.faq
      .map((item, i) => `<details class="reveal"${i === 0 ? " open" : ""}><summary>${item.q}</summary><p>${item.a}</p></details>`)
      .join("");
  }

  /* ---------- Program dialog ---------- */

  const dialog = $("#program-dialog");
  let lastFocus = null;

  function renderDialog(p) {
    const tabs = [
      ["about", "О программе"],
      ["modules", "Модули"],
      ["skills", pageKey === "phd" ? "Компетенции" : "Навыки"],
    ];
    if (p.practice) tabs.push(["practice", "Практика и исследования"]);
    tabs.push(["career", "Карьера"]);

    const panels = {
      about: `
        <div class="goal-box">${p.goal}</div>
        <p>${p.about}</p>
        ${p.field ? `<p><b>Область образования:</b> ${p.field}<br /><b>Группа программ:</b> ${p.group}</p>` : ""}`,
      modules: `<ul class="list-grid list-grid--numbered">${p.modules.map((m) => `<li>${m}</li>`).join("")}</ul>`,
      skills: `<ul class="list-grid list-grid--check">${p.skills.map((s) => `<li>${icon("check")}<span>${s}</span></li>`).join("")}</ul>`,
      practice: p.practice
        ? `<ul class="practice-list">${p.practice.map((s) => `<li><h4>${s.title}</h4><p>${s.text}</p></li>`).join("")}</ul>`
        : "",
      career: `<p style="margin-bottom:16px;color:var(--ink-2)">Где работают выпускники программы:</p>
        <ul class="list-grid list-grid--check">${p.careers.map((c) => `<li>${icon("check")}<span>${c}</span></li>`).join("")}</ul>`,
    };

    const factCells = [
      ["Срок обучения", p.duration],
      ["Кредиты ECTS", p.ects],
      p.format ? ["Формат", p.format] : ["Степень", "Доктор философии (PhD)"],
      ["Язык", p.languages],
    ];

    const tagLabel = pageKey === "masters" ? TRACK_LABEL[p.track] : "Докторантура PhD";
    const tagClass = pageKey === "masters" ? p.track : "np";

    dialog.innerHTML = `
      <button class="dialog__close" type="button" aria-label="Закрыть" data-close>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
      </button>
      <header class="dialog__hero" style="background-image:url('${p.image}')">
        <div>
          <span class="tag">${p.code}</span>
          <span class="tag tag--${tagClass}">${tagLabel}</span>
          <h2 class="dialog__title" id="dialog-title">${p.title}${pageKey === "masters" ? ` (${TRACK_SHORT[p.track]})` : ""}</h2>
        </div>
      </header>
      <div class="dialog__facts">${factCells.map(([k, v]) => `<div><small>${k}</small><b>${v}</b></div>`).join("")}</div>
      <div class="tabs" role="tablist" aria-label="Разделы программы">
        ${tabs
          .map(
            ([id, label], i) =>
              `<button class="tab" role="tab" type="button" id="tab-${id}" aria-controls="panel-${id}" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}">${label}</button>`
          )
          .join("")}
      </div>
      <div class="dialog__content">
        ${tabs
          .map(
            ([id], i) =>
              `<section class="panel" role="tabpanel" id="panel-${id}" aria-labelledby="tab-${id}"${i === 0 ? "" : " hidden"}>${panels[id]}</section>`
          )
          .join("")}
      </div>
      <footer class="dialog__footer">
        <p>Остались вопросы? Приёмная комиссия: <a href="tel:87009570061">8 (700) 957-00-61</a></p>
        <a class="btn btn--primary btn--sm" href="${window.KNUS_SITE}/ru/applicants/how-to-apply">Как поступить</a>
      </footer>`;

    dialog.setAttribute("aria-labelledby", "dialog-title");
    dialog.querySelector("[data-close]").addEventListener("click", closeDialog);

    const tabButtons = [...dialog.querySelectorAll('[role="tab"]')];
    const select = (btn) => {
      tabButtons.forEach((b) => {
        const active = b === btn;
        b.setAttribute("aria-selected", String(active));
        b.tabIndex = active ? 0 : -1;
        dialog.querySelector(`#${b.getAttribute("aria-controls")}`).hidden = !active;
      });
      dialog.querySelector(".dialog__content").scrollTop = 0;
    };
    tabButtons.forEach((btn, i) => {
      btn.addEventListener("click", () => select(btn));
      btn.addEventListener("keydown", (e) => {
        const dir = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!dir) return;
        const next = tabButtons[(i + dir + tabButtons.length) % tabButtons.length];
        next.focus();
        select(next);
      });
    });
  }

  function openDialog(code, { updateHash = true } = {}) {
    const p = page.programs.find((x) => x.code === code);
    if (!p || !dialog) return;
    lastFocus = document.activeElement;
    renderDialog(p);
    dialog.showModal();
    document.body.classList.add("is-locked");
    if (updateHash) history.replaceState(null, "", `#${programId(p)}`);
  }

  function closeDialog() {
    if (dialog.open) dialog.close();
  }

  if (dialog) {
    dialog.addEventListener("close", () => {
      document.body.classList.remove("is-locked");
      history.replaceState(null, "", location.pathname + location.search);
      if (lastFocus) lastFocus.focus();
    });
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) closeDialog();
    });
  }

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-open]");
    if (btn) openDialog(btn.dataset.open);
  });

  const hashMatch = location.hash.match(/^#program-(.+)$/);
  if (hashMatch) openDialog(decodeURIComponent(hashMatch[1]), { updateHash: false });

  /* ---------- Mobile menu ---------- */

  const burger = $(".burger");
  const nav = $(".header__nav");
  if (burger && nav) {
    burger.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      burger.setAttribute("aria-expanded", String(open));
    });
  }

  /* ---------- Section nav highlight ---------- */

  const navLinks = [...document.querySelectorAll(".section-nav a")];
  const sections = navLinks.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === `#${entry.target.id}`));
        });
      },
      { rootMargin: "-40% 0px -55% 0px" }
    );
    sections.forEach((s) => spy.observe(s));
  }

  /* ---------- Reveal on scroll ---------- */

  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("is-visible"));
  }
})();
