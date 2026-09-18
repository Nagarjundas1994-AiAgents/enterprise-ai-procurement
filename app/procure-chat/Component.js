sap.ui.define(
  ["sap/ui/core/UIComponent", "sap/ui/Device"],
  function (UIComponent, Device) {
    "use strict";

    return UIComponent.extend("procure.chat.Component", {
      metadata: { manifest: "json" },

      init: function () {
        UIComponent.prototype.init.apply(this, arguments);
        // Device model (responsive behavior)
        var oDeviceModel = new sap.ui.model.json.JSONModel(Device);
        oDeviceModel.setDefaultBindingMode("OneWay");
        this.setModel(oDeviceModel, "device");
        // Shared app state: demo user (mock auth), lists, chat
        var oApp = new sap.ui.model.json.JSONModel({
          user: "admin@example.com",
          busy: false,
          prs: [],
          pos: [],
          suppliers: [],
          messages: [
            {
              role: "assistant",
              text: "Hi! I am your procurement assistant (DeepSeek). Ask me about requisitions, budgets, suppliers — or pick a row action to start.",
              time: new Date().toLocaleTimeString()
            }
          ]
        });
        this.setModel(oApp, "app");
      }
    });
  }
);
