// didlab-gym: make /challenges behave "modal-only" when coming from /gym
(function () {
  function fromGym() {
    try {
      var params = new URLSearchParams(window.location.search);
      return params.get("from_gym") === "1";
    } catch (e) {
      return false;
    }
  }

  // Only run on the main challenges page, and only when from_gym=1
  if (window.location.pathname === "/challenges" && fromGym()) {
    // Wait until the DOM & jQuery/Bootstrap are ready
    var attach = function () {
      var modal = $("#challenge-window");
      if (!modal.length) {
        // Challenge modal not yet in DOM; try again shortly
        setTimeout(attach, 200);
        return;
      }

      // As soon as the challenge modal is closed, send user back to /gym
      modal.on("hidden.bs.modal", function () {
        window.location.href = "/gym";
      });
    };

    // jQuery ready
    if (typeof $ !== "undefined") {
      $(attach);
    } else {
      // Fallback if jQuery isn't ready for some reason
      document.addEventListener("DOMContentLoaded", attach);
    }
  }
})();
