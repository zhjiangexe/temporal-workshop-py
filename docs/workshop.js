(() => {
  const escapeHtml = (text) =>
    text
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");

  const pythonKeywords = new Set([
    "and",
    "as",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "else",
    "except",
    "False",
    "finally",
    "for",
    "from",
    "if",
    "import",
    "in",
    "is",
    "None",
    "not",
    "or",
    "pass",
    "return",
    "self",
    "True",
    "try",
    "with",
  ]);

  const builtins = new Set([
    "ActivityConfig",
    "Callable",
    "RetryPolicy",
    "TimeoutError",
    "Worker",
    "workflow",
    "activity",
    "timedelta",
  ]);

  const tokenPattern =
    /(@[A-Za-z_][\w.]*)|(#.*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|\b(\d+(?:\.\d+)?)\b|\b([A-Za-z_][\w.]*)\b|(→|←|=>|->|✓|✗|×)/g;

  const highlightPython = (text) => {
    let output = "";
    let lastIndex = 0;
    text.replace(tokenPattern, (match, decorator, comment, string, number, word, arrow, offset) => {
      output += escapeHtml(text.slice(lastIndex, offset));
      const value = escapeHtml(match);
      if (decorator) output += `<span class="hl-decorator">${value}</span>`;
      else if (comment) output += `<span class="hl-comment">${value}</span>`;
      else if (string) output += `<span class="hl-string">${value}</span>`;
      else if (number) output += `<span class="hl-number">${value}</span>`;
      else if (arrow) output += `<span class="hl-arrow">${value}</span>`;
      else if (pythonKeywords.has(word)) output += `<span class="hl-keyword">${value}</span>`;
      else if (builtins.has(word)) output += `<span class="hl-builtin">${value}</span>`;
      else output += value;
      lastIndex = offset + match.length;
      return match;
    });
    output += escapeHtml(text.slice(lastIndex));
    return output;
  };

  const highlightShell = (text) =>
    escapeHtml(text)
      .replace(/(^|\n)(\s*#.*)/g, '$1<span class="hl-comment">$2</span>')
      .replace(/\b([A-Z_][A-Z0-9_]*=)/g, '<span class="hl-env">$1</span>')
      .replace(
        /(^|\n)(\s*)(uv|temporal|pkill|pytest|python|docker|make|curl|FAIL_PUBLISH=1)\b/g,
        '$1$2<span class="hl-command">$3</span>'
      );

  const highlightText = (text) =>
    escapeHtml(text).replace(/(→|←|=>|->|✓|✗|×)/g, '<span class="hl-arrow">$1</span>');

  const detect = (text) => {
    if (/@(?:workflow|activity)\.|^\s*(async\s+def|class|from|import|try:|except|await)\b/m.test(text)) {
      return "python";
    }
    if (/^\s*(uv|temporal|pkill|pytest|python|docker|make|curl|FAIL_PUBLISH=1)\b/m.test(text)) {
      return "shell";
    }
    return "text";
  };

  document.querySelectorAll("pre code").forEach((code) => {
    const raw = code.textContent;
    const language = detect(raw);
    code.classList.add("hl", `hl-${language}`);
    code.innerHTML =
      language === "python"
        ? highlightPython(raw)
        : language === "shell"
          ? highlightShell(raw)
          : highlightText(raw);
  });
})();
