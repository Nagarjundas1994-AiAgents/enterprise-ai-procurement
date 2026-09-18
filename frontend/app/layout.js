import "./globals.css";

export const metadata = {
  title: "ProcureChat — AI Procurement Assistant",
  description: "Requisitions, orders, suppliers and a DeepSeek AI assistant."
};

// Runs synchronously before React hydrates: applies the persisted (or OS)
// theme to <html data-theme> so the first paint already has the right theme
// and client components read a consistent value. Static string — identical
// on server and client, so it never causes a hydration mismatch.
const THEME_SCRIPT = `(function(){try{var s=localStorage.getItem("pc-theme");var t=(s==="light"||s==="dark")?s:((window.matchMedia&&window.matchMedia("(prefers-color-scheme: light)").matches)?"light":"dark");document.documentElement.dataset.theme=t;}catch(e){document.documentElement.dataset.theme="dark";}})();`;

export default function RootLayout({ children }) {
  return (
    // suppressHydrationWarning: the blocking script below intentionally sets
    // data-theme (light/dark from localStorage) before hydration, so the DOM
    // attribute legitimately differs from this static "dark" default.
    // This is the documented next-themes pattern — React keeps the DOM value.
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <body>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
        {children}
      </body>
    </html>
  );
}
