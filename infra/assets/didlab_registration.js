// assets/didlab_registration.js

document.addEventListener("DOMContentLoaded", function () {
  // Only run on registration & profile pages
  const path = window.location.pathname;
  if (!path.includes("/register") && !path.includes("/settings")) {
    return;
  }

  const fieldConfigs = {
    "course_code": [
      { value: "COMP_SCI-361", text: "COMP_SCI-361 (Intro Cybersecurity)" },
      { value: "COMP_SCI-381", text: "COMP_SCI-381 (Info Sec Assurance)" },
      { value: "COMP_SCI-5533", text: "COMP_SCI-5533 (Blockchain)" },
      { value: "PRACTICE", text: "General Practice / Non-course" }
    ],
    "section": [
      { value: "0001", text: "Section 0001" },
      { value: "0002", text: "Section 0002" },
      { value: "PRACTICE", text: "N/A (Practice only)" }
    ],
    "term": [
      { value: "2026SP", text: "2026 Spring" }
      // add more terms later if needed
    ]
  };

  function makeSelect(labelText, options) {
    // Find the label whose text is exactly our field name
    const label = Array.from(document.querySelectorAll("label")).find(
      l => l.textContent.trim() === labelText
    );
    if (!label) return;

    const input = label.parentElement.querySelector("input.form-control");
    if (!input) return;

    const currentValue = input.value;

    const select = document.createElement("select");
    select.className = input.className;
    select.id = input.id;
    select.name = input.name;

    // Placeholder option
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.disabled = true;
    placeholder.selected = true;
    placeholder.textContent = "Select " + labelText.replace("_", " ");
    select.appendChild(placeholder);

    options.forEach(o => {
      const opt = document.createElement("option");
      opt.value = o.value;
      opt.textContent = o.text;
      if (currentValue && currentValue === o.value) {
        opt.selected = true;
        placeholder.selected = false;
      }
      select.appendChild(opt);
    });

    input.parentElement.replaceChild(select, input);
  }

  Object.entries(fieldConfigs).forEach(([labelText, options]) => {
    makeSelect(labelText, options);
  });
});
