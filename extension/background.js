let lastUrl = "";

// Store URL results
let urlResultStore = {};

// Allow proceed URLs
let allowedUrl = "";
// -----------------------------
// URL CHECK
// -----------------------------

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {

  if (changeInfo.status !== "complete" || !tab.url) return;

  const url = tab.url;

  if (
    url.startsWith("chrome://") ||
    url.startsWith("chrome-extension://") ||
    url.startsWith("edge://") ||
    url.startsWith("about:")
  ) return;

  if (url.includes("warning.html")) return;

  // Skip if user allowed it
if (url === allowedUrl) {

  console.log("Allowed URL detected — skipping all checks");

  // keep allowedUrl for HTML skip also
  return;

}


if (url === lastUrl) return;

lastUrl = url;

  console.log("Checking URL:", url);

  fetch("http://127.0.0.1:5000/predict", {

    method: "POST",

    headers: {
      "Content-Type": "application/json"
    },

    body: JSON.stringify({
      url: url
    })

  })

  .then(res => res.json())

  .then(data => {

    console.log("URL result:", data);

    // Store URL result
    urlResultStore[tabId] = data;

  })

  .catch(err => {

    console.log("URL ERROR:", err);

  });

});


// -----------------------------
// HTML CHECK HANDLER
// -----------------------------

chrome.runtime.onMessage.addListener((msg, sender) => {

  if (msg.type === "HTML_CHECK") {
    // Skip HTML if allowed

if (msg.url === allowedUrl) {

  console.log("Allowed URL — skipping HTML check");

  allowedUrl = ""; // clear after full load

  return;

}

    console.log("HTML received from content");

    fetch("http://127.0.0.1:5000/predict_html", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({

        html: msg.html,
        url: msg.url

      })

    })

    .then(res => res.json())

    .then(htmlData => {

      console.log("HTML result:", htmlData);

      let urlData =
        urlResultStore[sender.tab.id];

      console.log("URL stored:", urlData);


  // -----------------------------
// FINAL DECISION (FIXED)
// -----------------------------

if (!urlData) return;

let finalResult = "SAFE";

// URL PHISHING → always phishing

if (urlData.result === "PHISHING") {

  finalResult = "PHISHING";

}

// URL SAFE but HTML PHISHING

else if (
  urlData.result === "SAFE" &&
  htmlData.result === "PHISHING"
) {

  finalResult = "SUSPICIOUS";

}

// BOTH suspicious

else if (
  urlData.result === "SUSPICIOUS" &&
  htmlData.result === "SUSPICIOUS"
) {

  finalResult = "SUSPICIOUS";

}

// otherwise SAFE

else {

  finalResult = "SAFE";

}

let confidence = Math.max(
  urlData.confidence,
  htmlData.confidence
);

console.log("FINAL RESULT:", finalResult);

// Show warning

if (
  finalResult === "PHISHING" ||
  finalResult === "SUSPICIOUS"
) {

  chrome.storage.local.set({

    warningData: {

      url: msg.url,
      result: finalResult,
      confidence: confidence

    }

  });

  chrome.tabs.update(
    sender.tab.id,
    {
      url: chrome.runtime.getURL(
        "warning.html"
      )
    }
  );

}

    })

    .catch(err => {

      console.log(
        "HTML FETCH ERROR:",
        err
      );

    });

  }

});
// -----------------------------
// PROCEED HANDLER
// -----------------------------
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

  if (msg.type === "ALLOW_URL") {

    allowedUrl = msg.url;

    console.log(
      "User allowed URL:",
      allowedUrl
    );

    // Send response back
    sendResponse({ status: "allowed" });

  }

  return true;

});
