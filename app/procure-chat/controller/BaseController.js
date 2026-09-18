sap.ui.define(["sap/ui/core/mvc/Controller"], function (Controller) {
  "use strict";

  return Controller.extend("procure.chat.controller.BaseController", {
    app: function () {
      return this.getOwnerComponent().getModel("app");
    },

    user: function () {
      return this.app().getProperty("/user") || "admin@example.com";
    },

    /**
     * Same-origin backend call. Local dev authenticates via x-mock-user
     * (ALLOW_MOCK_AUTH=true); in BTP the approuter injects the JWT user.
     */
    api: async function (path, options) {
      var opts = options || {};
      var res = await fetch(path, {
        method: opts.method || "GET",
        headers: Object.assign(
          { "Content-Type": "application/json", "x-mock-user": this.user() },
          opts.headers || {}
        ),
        body: opts.body
      });
      var data = null;
      try {
        data = await res.json();
      } catch (e) {
        data = null;
      }
      if (!res.ok) {
        var msg =
          (data && data.error && data.error.message) ||
          "Request failed (" + res.status + ")";
        throw new Error(msg);
      }
      return data && data.value !== undefined ? data.value : data;
    },

    toast: function (text) {
      sap.m.MessageToast.show(text);
    },

    boxError: function (err) {
      sap.m.MessageBox.error(String((err && err.message) || err));
    }
  });
});
