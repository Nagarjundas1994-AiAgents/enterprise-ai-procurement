sap.ui.define(
  ["procure/chat/controller/BaseController"],
  function (BaseController) {
    "use strict";

    return BaseController.extend("procure.chat.controller.Chat", {
      _conversationId: null,

      onInit: function () {
        // One conversation per page load; the backend keeps no history,
        // the id simply correlates this session in logs/audit.
        this._conversationId =
          "ui-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
      },

      /**
       * External entry: Main controller posts a contextual question.
       */
      ask: function (sText) {
        this.byId("chatInput").setValue(sText);
        this.onSend();
      },

      onSend: async function () {
        var oInput = this.byId("chatInput");
        var sText = (oInput.getValue() || "").trim();
        if (!sText) return;
        var oApp = this.app();
        var aMsgs = oApp.getProperty("/messages").slice();
        aMsgs.push({ role: "user", text: sText, time: new Date().toLocaleTimeString() });
        // Typing indicator while DeepSeek answers
        var iTyping = aMsgs.push({ role: "typing", text: "Assistant is thinking…", time: "" }) - 1;
        oApp.setProperty("/messages", aMsgs);
        oApp.setProperty("/busy", true);
        oInput.setValue("");
        this.scrollDown();

        try {
          var sReply = await this.api("/odata/v4/agents/chat", {
            method: "POST",
            body: JSON.stringify({ conversationId: this._conversationId, message: sText })
          });
          aMsgs = oApp.getProperty("/messages").slice();
          aMsgs.splice(iTyping, 1, {
            role: "assistant",
            text: String(sReply),
            time: new Date().toLocaleTimeString()
          });
          oApp.setProperty("/messages", aMsgs);
        } catch (err) {
          aMsgs = oApp.getProperty("/messages").slice();
          aMsgs.splice(iTyping, 1, {
            role: "error",
            text: "Request failed: " + String((err && err.message) || err),
            time: new Date().toLocaleTimeString()
          });
          oApp.setProperty("/messages", aMsgs);
        } finally {
          oApp.setProperty("/busy", false);
          this.scrollDown();
        }
      },

      onClearChat: function () {
        this.app().setProperty("/messages", []);
      },

      scrollDown: function () {
        // Let the list re-render, then scroll the ScrollContainer to bottom.
        var oView = this.getView();
        setTimeout(function () {
          try {
            var oScroll = oView.getContent()[0].getItems()[1];
            if (oScroll && oScroll.scrollTo) oScroll.scrollTo(0, 999999, 300);
          } catch (e) {
            /* non-critical */
          }
        }, 150);
      },

      fmtAlign: function (sRole) {
        return sRole === "user" ? "End" : "Start";
      },

      fmtInitials: function (sRole) {
        if (sRole === "user") return "YOU";
        if (sRole === "error") return "!";
        if (sRole === "typing") return "…";
        return "AI";
      },

      fmtRole: function (sRole) {
        if (sRole === "user") return "You";
        if (sRole === "error") return "Error";
        if (sRole === "typing") return "";
        return "Assistant";
      },

      /**
       * Escape HTML, then light markdown: **bold**, line breaks, `code`.
       */
      fmtText: function (sText) {
        var s = String(sText == null ? "" : sText)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
        s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        s = s.replace(/`(.+?)`/g, "<code>$1</code>");
        s = s.replace(/\n/g, "<br>");
        return s;
      }
    });
  }
);
