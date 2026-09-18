sap.ui.define(
  ["procure/chat/controller/BaseController"],
  function (BaseController) {
    "use strict";

    return BaseController.extend("procure.chat.controller.Main", {
      onInit: function () {
        this.loadAll();
      },

      onUserChange: function () {
        var sUser = this.byId("userSelect").getSelectedKey();
        this.app().setProperty("/user", sUser);
        this.loadAll();
        this.toast("Acting as " + sUser);
      },

      onRefresh: function () {
        this.loadAll();
      },

      onTabSelect: function () {
        // Lists are preloaded; tab switch needs no reload.
      },

      loadAll: async function () {
        var oApp = this.app();
        oApp.setProperty("/busy", true);
        try {
          var prs = await this.api(
            "/odata/v4/procurement/PurchaseRequisitions?$top=50&$orderby=createdAt%20desc"
          );
          var pos = await this.api(
            "/odata/v4/procurement/PurchaseOrders?$top=50&$orderby=createdAt%20desc"
          );
          var suppliers = await this.api(
            "/odata/v4/suppliers/Suppliers?$top=50"
          );
          oApp.setProperty("/prs", prs.value || prs || []);
          oApp.setProperty("/pos", pos.value || pos || []);
          oApp.setProperty("/suppliers", suppliers.value || suppliers || []);
        } catch (err) {
          this.boxError(err);
        } finally {
          oApp.setProperty("/busy", false);
        }
      },

      selectedPr: function (oEvent) {
        var oCtx = oEvent.getParameter("listItem").getBindingContext("app");
        return oCtx ? oCtx.getObject() : null;
      },

      onPrSelect: function () {
        // Selection is used implicitly by row buttons; nothing to do.
      },

      prOfButton: function (oEvent) {
        var oCtx = oEvent.getSource().getBindingContext("app");
        return oCtx ? oCtx.getObject() : null;
      },

      onCheckBudget: async function (oEvent) {
        var pr = this.prOfButton(oEvent);
        if (!pr) return;
        try {
          // checkBudget is an OData *function* -> GET with parenthesis params.
          var sDept = String(pr.department_ID).replace(/'/g, "''");
          var ok = await this.api(
            "/odata/v4/catalog/checkBudget(departmentID='" + sDept +
              "',amount=" + Number(pr.totalAmount) + ")"
          );
          this.toast(
            ok === true
              ? "Budget covers " + pr.requisitionNo
              : "Budget INSUFFICIENT for " + pr.requisitionNo
          );
        } catch (err) {
          this.boxError(err);
        }
      },

      onSubmitPr: async function (oEvent) {
        var pr = this.prOfButton(oEvent);
        if (!pr) return;
        try {
          var res = await this.api("/odata/v4/procurement/submitRequisition", {
            method: "POST",
            body: JSON.stringify({ ID: pr.ID })
          });
          this.toast(typeof res === "string" ? res : "Submitted " + pr.requisitionNo);
          this.loadAll();
        } catch (err) {
          this.boxError(err);
        }
      },

      /**
       * Row action -> hands the PR to the chat: posts a contextual question
       * to the AI assistant via the Chat controller.
       */
      onAskAi: function (oEvent) {
        var pr = this.prOfButton(oEvent);
        if (!pr) return;
        var sQ =
          "PR " + pr.requisitionNo + " '" + pr.title + "' (" + pr.status +
          ", " + pr.totalAmount + " " + pr.currency +
          "): summarize status, budget outlook and recommended next step.";
        var oChatView = this.byId("chatView");
        if (oChatView && oChatView.getController) {
          oChatView.getController().ask(sQ);
        }
      },

      fmtStatus: function (s) {
        switch (s) {
          case "APPROVED": return "Success";
          case "DRAFT": return "None";
          case "SUBMITTED": return "Information";
          case "REJECTED": return "Error";
          default: return "Warning";
        }
      },

      fmtRisk: function (s) {
        if (s === "LOW") return "Success";
        if (s === "MEDIUM") return "Warning";
        if (s === "HIGH" || s === "CRITICAL") return "Error";
        return "None";
      }
    });
  }
);
