const codeEditor = document.getElementById("code");
const output = document.getElementById("output");
const preview = document.getElementById("websitePreview");
const runButton = document.getElementById("runButton");

async function runCode() {
    const code = codeEditor.value;
    const inputs = [];
    runButton.disabled = true;
    runButton.textContent = "Running...";
    output.textContent = "Running Monty code...";

    try {
        while (true) {
            const response = await fetch("/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code, inputs })
            });
            const result = await response.json();

            if (result.inputNeeded !== undefined) {
                const answer = window.prompt(result.inputNeeded || "Enter a value:");
                if (answer === null) {
                    output.textContent = "Input cancelled.";
                    break;
                }
                inputs.push(answer);
                continue;
            }

            output.textContent = result.output || "(No output)";
            if (result.website_html) {
                preview.srcdoc = result.website_html;
            }
            break;
        }
    } catch (error) {
        output.textContent = "Could not run Monty: " + error.message;
    } finally {
        runButton.disabled = false;
        runButton.textContent = "▶ Run";
    }
}

runButton.addEventListener("click", runCode);
document.getElementById("clearButton").addEventListener("click", () => {
    output.textContent = "";
});
codeEditor.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
        event.preventDefault();
        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;
        codeEditor.setRangeText("    ", start, end, "end");
    }
});
