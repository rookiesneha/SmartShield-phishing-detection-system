console.log("CONTENT SCRIPT LOADED ✅");

// Skip internal pages

if (

    window.location.href.startsWith("chrome://") ||
    window.location.href.startsWith("chrome-extension://") ||
    window.location.href.startsWith("edge://")

) {

    console.log("Skipped internal page");

}

else {

    window.addEventListener("load", () => {

        setTimeout(() => {

            try {

                console.log("Sending HTML...");

                let html =
                    document.documentElement.outerHTML;

                // Limit size (important)
                if (html.length > 200000) {

                    html =
                        html.substring(0, 200000);

                }

                chrome.runtime.sendMessage({

                    type: "HTML_CHECK",

                    html: html,

                    url: window.location.href

                });

            }

            catch (err) {

                console.log(
                    "CONTENT ERROR:",
                    err
                );

            }

        }, 1500); // wait page load

    });

}