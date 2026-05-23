let info = null;

chrome.storage.local.get(
  "warningData",
  (data) => {

    info = data.warningData;

    document.getElementById(
      "url"
    ).innerText =
      "URL: " + info.url;

    document.getElementById(
      "result"
    ).innerText =
      "Result: " + info.result;

    document.getElementById(
      "confidence"
    ).innerText =
      "Confidence: " +
      info.confidence;

});


// -----------------------------
// GO BACK
// -----------------------------

document.getElementById(
  "back"
).onclick = () => {

  window.location.href =
    "https://www.google.com";

};


// -----------------------------
// PROCEED ANYWAY
// -----------------------------

document.getElementById(
  "proceed"
).onclick = () => {

chrome.runtime.sendMessage({

  type: "ALLOW_URL",

  url: info.url

},

(response) => {

  if (chrome.runtime.lastError) {

    console.log(
      "Message error:",
      chrome.runtime.lastError
    );

    return;

  }

  console.log(
    "Proceed allowed:",
    response
  );

  setTimeout(() => {

    window.location.href =
      info.url;

  }, 200);

});

};


// -----------------------------
// FEEDBACK BUTTONS
// -----------------------------

function sendFeedback(type) {

fetch(
  "http://127.0.0.1:5000/save_feedback",
{

  method: "POST",

  headers: {

    "Content-Type":
      "application/json"

  },

  body: JSON.stringify({

    url: info.url,
    prediction: info.result,
    feedback: type

  })

})

.then(res => res.json())

.then(data => {

  console.log(
    "Feedback stored:",
    data
  );

  showThankYou();

})

.catch(err => {

  console.log(
    "Feedback error:",
    err
  );

});

}


document.getElementById(
  "correctBtn"
).onclick = () => {

  sendFeedback("CORRECT");

};


document.getElementById(
  "wrongBtn"
).onclick = () => {

  sendFeedback("WRONG");

};


// -----------------------------
// THANK YOU SCREEN
// -----------------------------

function showThankYou() {

document.getElementById(
  "warningBox"
).style.display = "none";

document.getElementById(
  "thankBox"
).style.display = "block";

}


// -----------------------------
// CLOSE BUTTON
// -----------------------------

document.getElementById(
  "closeBtn"
).onclick = () => {

location.reload();

};