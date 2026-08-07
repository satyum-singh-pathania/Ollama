async function summarizeText() {
  const inputText = document.getElementById("inputText").value;
  const resultDiv = document.getElementById("result");

  if (!inputText) {
    resultDiv.textContent = "Please enter some text to summarize.";
    return;
  }

  try {
    const response = await fetch("/summarize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: inputText }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    resultDiv.textContent = data.response;
  } catch (error) {
    console.error("Error:", error);
    resultDiv.textContent = "An error occurred while summarizing the text.";
  }
}
